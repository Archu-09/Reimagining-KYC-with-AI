import logging
from typing import Dict
import numpy as np

logger = logging.getLogger(__name__)

_FACENET_AVAILABLE = False
_MTCNN = None
_RESNET = None

try:
    import torch
    from facenet_pytorch import MTCNN, InceptionResnetV1
    from PIL import Image

    # Initialize models lazily
    def _init_models(device=None):
        global _FACENET_AVAILABLE, _MTCNN, _RESNET
        if _FACENET_AVAILABLE:
            return
        if device is None:
            device = 'cuda' if torch.cuda.is_available() else 'cpu'
        _MTCNN = MTCNN(keep_all=False, device=device)
        _RESNET = InceptionResnetV1(pretrained='vggface2').eval().to(device)
        _FACENET_AVAILABLE = True

    def _get_embedding(image_path: str):
        img = Image.open(image_path).convert('RGB')
        # detect and crop to face using MTCNN
        if not _FACENET_AVAILABLE:
            _init_models()
        face = _MTCNN(img)
        if face is None:
            return None
        # face is a tensor (3 x 160 x 160)
        with torch.no_grad():
            emb = _RESNET(face.unsqueeze(0).to(_RESNET.device))
        return emb[0].cpu().numpy()

    def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

    def match_faces(id_image_path: str, selfie_path: str) -> Dict[str, object]:
        """Match faces using facenet-pytorch. Returns similarity and match boolean.

        If facenet-pytorch is not available or face not found, falls back to placeholder.
        """
        logger.debug(f"[FACE] match_faces: comparing {id_image_path} and {selfie_path}")
        try:
            emb1 = _get_embedding(id_image_path)
            emb2 = _get_embedding(selfie_path)
            if emb1 is None or emb2 is None:
                logger.warning(f"[FACE] Face not found in one or both images")
                return {"similarity": 0.0, "match": False, "method": "facenet", "note": "face not found"}
            sim = _cosine_similarity(emb1, emb2)
            # threshold typical values: 0.6-0.8 (tune in production)
            match = sim >= 0.6
            logger.info(f"[FACE] Face match result: similarity={sim:.4f}, match={match}")
            return {"similarity": round(sim, 4), "match": bool(match), "method": "facenet"}
        except Exception as e:
            logger.exception("Facenet matching failed: %s", e)
            return {"similarity": 0.0, "match": False, "method": "facenet", "error": str(e)}

    def liveness_check(selfie_path: str, id_document_path: str = None) -> Dict[str, object]:
        """Enhanced liveness detection with document face validation."""
        try:
            # Use enhanced liveness detection if document path provided
            if id_document_path:
                from app.services.enhanced_liveness import enhanced_liveness_detector
                return enhanced_liveness_detector.comprehensive_liveness_check(id_document_path, selfie_path)
            else:
                # Fallback to original method for backward compatibility
                from app.services.liveness_service import liveness_detector
                result = liveness_detector.detect_liveness_single_image(selfie_path)
                # Apply stricter scoring for security
                if result.get('liveness_score', 0) > 0:
                    result['liveness_score'] = result['liveness_score'] * 0.8  # Make it harder to pass
                    result['passed'] = result['liveness_score'] >= 0.75  # Higher threshold
                    result['security_level'] = 'enhanced'
                return result
        except ImportError:
            logger.warning("Enhanced liveness service not available, using basic check with strict validation")
            # Even basic check should require face detection
            try:
                import cv2
                img = cv2.imread(selfie_path)
                if img is None:
                    return {"liveness_score": 0.0, "passed": False, "method": "basic", "error": "Cannot load image"}
                
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
                faces = face_cascade.detectMultiScale(gray, 1.3, 5)
                
                if len(faces) == 0:
                    return {"liveness_score": 0.0, "passed": False, "method": "basic", "error": "No face detected"}
                elif len(faces) > 1:
                    return {"liveness_score": 0.0, "passed": False, "method": "basic", "error": "Multiple faces detected"}
                else:
                    # Even with face detected, use conservative score
                    return {"liveness_score": 0.6, "passed": False, "method": "basic", "warning": "Basic check - upgrade to enhanced detection recommended"}
            except:
                return {"liveness_score": 0.0, "passed": False, "method": "basic", "error": "Face detection failed"}

except Exception:
    # facenet/torch not available: implement OpenCV-based fallback for
    # real face detection and a lightweight liveness heuristic.
    logger.warning("facenet-pytorch or torch not available; using OpenCV fallback for face matching and liveness")

    import cv2

    # Haar cascades shipped with OpenCV (available via cv2.data.haarcascades)
    FACE_CASCADE = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    EYE_CASCADE = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')

    def _read_image(path: str):
        img = cv2.imread(path)
        if img is None:
            raise ValueError(f'Unable to read image at {path}')
        return img

    def _detect_faces(img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = FACE_CASCADE.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=4, minSize=(50, 50))
        return faces, gray

    def _crop_and_normalize(face_box, img, size=(100, 100)):
        x, y, w, h = face_box
        crop = img[y:y + h, x:x + w]
        resized = cv2.resize(crop, size)
        gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY) if len(resized.shape) == 3 else resized
        vec = gray.flatten().astype('float32')
        norm = (vec - vec.mean()) / (vec.std() + 1e-6)
        return norm

    def _cosine_similarity(a, b):
        denom = (np.linalg.norm(a) * np.linalg.norm(b))
        if denom == 0:
            return 0.0
        return float(np.dot(a, b) / denom)

    def match_faces(id_image_path: str, selfie_path: str) -> Dict[str, object]:
        """Fallback face matching using OpenCV detection and a simple
        normalized-pixel embedding + cosine similarity.
        """
        logger.debug(f"[FACE-OPENCV] match_faces: comparing {id_image_path} and {selfie_path}")
        try:
            img1 = _read_image(id_image_path)
            img2 = _read_image(selfie_path)

            faces1, _ = _detect_faces(img1)
            faces2, _ = _detect_faces(img2)

            if len(faces1) == 0 or len(faces2) == 0:
                logger.warning(f"[FACE-OPENCV] Face not found: faces1={len(faces1)}, faces2={len(faces2)}")
                return {"similarity": 0.0, "match": False, "method": "opencv-fallback", "note": "face not found"}

            face1 = max(faces1, key=lambda b: b[2] * b[3])
            face2 = max(faces2, key=lambda b: b[2] * b[3])

            v1 = _crop_and_normalize(face1, img1)
            v2 = _crop_and_normalize(face2, img2)

            sim = _cosine_similarity(v1, v2)
            match = sim >= 0.45
            logger.info(f"[FACE-OPENCV] Match result: similarity={sim:.4f}, match={match}")
            return {"similarity": round(sim, 4), "match": bool(match), "method": "opencv-fallback"}
        except Exception as e:
            logger.exception("OpenCV fallback matching failed: %s", e)
            return {"similarity": 0.0, "match": False, "method": "opencv-fallback", "error": str(e)}

    def liveness_check(selfie_path: str, id_document_path: str = None) -> Dict[str, object]:
        """Enhanced liveness check that validates both selfie and document face.

        - Verifies a face is present in selfie
        - Verifies face exists in document (if provided)
        - Enhanced eye detection and analysis
        - Anti-spoofing measures
        """
        logger.debug(f"[FACE-LIVENESS] Enhanced checking for {selfie_path}")
        try:
            # Use enhanced detection if document provided
            if id_document_path:
                try:
                    from app.services.enhanced_liveness import enhanced_liveness_detector
                    return enhanced_liveness_detector.comprehensive_liveness_check(id_document_path, selfie_path)
                except ImportError:
                    logger.warning("Enhanced liveness detector not available, using strict OpenCV fallback")
            
            # Strict OpenCV-based liveness check
            img = _read_image(selfie_path)
            faces, gray = _detect_faces(img)
            
            if len(faces) == 0:
                logger.warning(f"[FACE-LIVENESS] No face detected")
                return {"liveness_score": 0.0, "passed": False, "method": "opencv-strict", "reason": "no_face"}
            
            if len(faces) > 1:
                logger.warning(f"[FACE-LIVENESS] Multiple faces detected: {len(faces)}")
                return {"liveness_score": 0.0, "passed": False, "method": "opencv-strict", "reason": "multiple_faces"}

            face = max(faces, key=lambda b: b[2] * b[3])
            x, y, w, h = face
            face_region_gray = gray[y:y + h, x:x + w]

            img_h, img_w = gray.shape
            face_area_ratio = (w * h) / float(img_w * img_h)

            # Stricter face size requirement
            if face_area_ratio < 0.05:  # Face must be at least 5% of image
                logger.warning(f"[FACE-LIVENESS] Face too small: {face_area_ratio:.3f}")
                return {"liveness_score": 0.0, "passed": False, "method": "opencv-strict", "reason": "face_too_small"}

            # Enhanced eye detection
            eyes = EYE_CASCADE.detectMultiScale(face_region_gray, scaleFactor=1.1, minNeighbors=4, minSize=(10, 10))

            # Stricter scoring system
            score = 0.0
            
            # Face size scoring (more strict)
            if face_area_ratio > 0.1:
                score += 0.3
            elif face_area_ratio > 0.05:
                score += 0.15
            
            # Eye detection scoring (require both eyes)
            if len(eyes) >= 2:
                score += 0.4
                # Bonus for good eye quality
                for (ex, ey, ew, eh) in eyes[:2]:
                    eye_region = face_region_gray[ey:ey+eh, ex:ex+ew]
                    eye_contrast = np.std(eye_region)
                    if eye_contrast > 15:  # Good eye contrast
                        score += 0.05
            elif len(eyes) == 1:
                score += 0.1  # Much lower score for single eye
            else:
                # No eyes detected - fail immediately
                logger.warning(f"[FACE-LIVENESS] No eyes detected")
                return {"liveness_score": 0.0, "passed": False, "method": "opencv-strict", "reason": "no_eyes"}
            
            # Image quality checks
            # 1. Sharpness check
            laplacian_var = cv2.Laplacian(face_region_gray, cv2.CV_64F).var()
            if laplacian_var > 100:  # Minimum sharpness
                score += 0.1
            
            # 2. Brightness check
            mean_brightness = np.mean(face_region_gray)
            if 50 < mean_brightness < 200:  # Reasonable brightness range
                score += 0.1
            
            # 3. Anti-spoofing: check for screen artifacts
            # Look for excessive uniformity (printed photos)
            texture_std = np.std(face_region_gray)
            if texture_std > 20:  # Natural texture variation
                score += 0.05
            
            score = max(0.0, min(1.0, score))
            
            # Much stricter passing threshold
            passed = score >= 0.75 and len(eyes) >= 2
            
            meta = {
                "face_area_ratio": round(face_area_ratio, 4), 
                "eyes_detected": int(len(eyes)),
                "face_sharpness": round(laplacian_var, 2),
                "face_brightness": round(mean_brightness, 2),
                "texture_variation": round(texture_std, 2),
                "security_level": "strict"
            }
            
            logger.info(f"[FACE-LIVENESS] Enhanced Score={score:.3f}, passed={passed}, eyes={len(eyes)}, area_ratio={face_area_ratio:.3f}")
            return {"liveness_score": round(score, 3), "passed": bool(passed), "method": "opencv-strict", **meta}
            
        except Exception as e:
            logger.exception("Enhanced OpenCV liveness check failed: %s", e)
            return {"liveness_score": 0.0, "passed": False, "method": "opencv-strict", "error": str(e)}
