"""
Enhanced Liveness Detection with Document Face Validation
Addresses the security vulnerabilities in the current system
"""
import logging
import numpy as np
from typing import Dict, List, Tuple, Optional
import cv2
from pathlib import Path

logger = logging.getLogger(__name__)

class EnhancedLivenessDetector:
    """
    Multi-stage liveness detection that validates:
    1. Document contains a valid face photo
    2. Selfie contains a live person 
    3. Face matching between document and selfie
    4. Anti-spoofing measures for both images
    """
    
    def __init__(self):
        # Initialize cascade classifiers
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
        self.profile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_profileface.xml')
        
        # Enhanced thresholds for security
        self.min_face_size = (50, 50)
        self.min_face_area_ratio = 0.05  # Face should be at least 5% of image
        self.min_eye_count = 2  # Require both eyes for liveness
        self.liveness_threshold = 0.75  # Higher threshold for security
        self.face_match_threshold = 0.6  # Minimum similarity for face matching
        
    def comprehensive_liveness_check(self, id_document_path: str, selfie_path: str) -> Dict[str, any]:
        """
        Comprehensive liveness detection that validates both document and selfie
        """
        logger.info(f"Starting comprehensive liveness check: {id_document_path} -> {selfie_path}")
        
        try:
            # Stage 1: Validate document contains a face photo
            document_validation = self._validate_document_face(id_document_path)
            
            # Stage 2: Validate selfie for liveness
            selfie_validation = self._validate_selfie_liveness(selfie_path)
            
            # Stage 3: Cross-validate faces match
            if document_validation['face_detected'] and selfie_validation['face_detected']:
                face_matching = self._cross_validate_faces(id_document_path, selfie_path)
            else:
                face_matching = {
                    'faces_match': False,
                    'similarity_score': 0.0,
                    'error': 'One or both images missing valid faces'
                }
            
            # Stage 4: Anti-spoofing checks
            anti_spoofing = self._anti_spoofing_analysis(selfie_path)
            
            # Calculate composite score with strict requirements
            composite_result = self._calculate_enhanced_score(
                document_validation, 
                selfie_validation, 
                face_matching, 
                anti_spoofing
            )
            
            return {
                **composite_result,
                'document_validation': document_validation,
                'selfie_validation': selfie_validation,
                'face_matching': face_matching,
                'anti_spoofing': anti_spoofing,
                'method': 'enhanced_multi_stage',
                'security_level': 'high'
            }
            
        except Exception as e:
            logger.exception(f"Enhanced liveness check failed: {e}")
            return {
                'liveness_score': 0.0,
                'passed': False,
                'error': str(e),
                'method': 'enhanced_multi_stage',
                'security_level': 'high'
            }
    
    def _validate_document_face(self, document_path: str) -> Dict[str, any]:
        """
        Validate that the ID document contains a proper face photograph
        """
        logger.debug("Validating document face...")
        
        try:
            image = cv2.imread(document_path)
            if image is None:
                return {'face_detected': False, 'error': 'Could not load document image'}
            
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Detect faces with multiple methods for accuracy
            frontal_faces = self.face_cascade.detectMultiScale(
                gray, scaleFactor=1.1, minNeighbors=5, minSize=self.min_face_size
            )
            profile_faces = self.profile_cascade.detectMultiScale(
                gray, scaleFactor=1.1, minNeighbors=5, minSize=self.min_face_size
            )
            
            all_faces = list(frontal_faces) + list(profile_faces)
            
            if len(all_faces) == 0:
                logger.warning("No face detected in document")
                return {
                    'face_detected': False,
                    'face_count': 0,
                    'error': 'No face found in document image',
                    'quality_score': 0.0
                }
            
            # Use the largest face (likely the ID photo)
            best_face = max(all_faces, key=lambda x: x[2] * x[3])
            x, y, w, h = best_face
            
            # Calculate face area ratio
            img_area = image.shape[0] * image.shape[1]
            face_area = w * h
            face_area_ratio = face_area / img_area
            
            # Extract face region for analysis
            face_region = gray[y:y+h, x:x+w]
            face_color = image[y:y+h, x:x+w]
            
            # Analyze face quality
            quality_metrics = self._analyze_document_face_quality(face_region, face_color)
            
            # Document face validation score
            validation_score = 0.0
            
            # Face size check (should be reasonable size for ID photo)
            if face_area_ratio >= self.min_face_area_ratio:
                validation_score += 0.3
            
            # Face quality checks
            validation_score += quality_metrics['quality_score'] * 0.4
            
            # Eye detection in document photo
            eyes = self.eye_cascade.detectMultiScale(face_region, scaleFactor=1.1, minNeighbors=3)
            if len(eyes) >= 2:
                validation_score += 0.3
            elif len(eyes) == 1:
                validation_score += 0.15
            
            return {
                'face_detected': True,
                'face_count': len(all_faces),
                'face_area_ratio': face_area_ratio,
                'face_dimensions': {'width': w, 'height': h},
                'eyes_detected': len(eyes),
                'quality_metrics': quality_metrics,
                'validation_score': min(validation_score, 1.0),
                'passed': validation_score >= 0.6
            }
            
        except Exception as e:
            logger.exception(f"Document face validation failed: {e}")
            return {'face_detected': False, 'error': str(e)}
    
    def _validate_selfie_liveness(self, selfie_path: str) -> Dict[str, any]:
        """
        Enhanced selfie liveness detection with anti-spoofing
        """
        logger.debug("Validating selfie liveness...")
        
        try:
            image = cv2.imread(selfie_path)
            if image is None:
                return {'face_detected': False, 'error': 'Could not load selfie image'}
            
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            faces = self.face_cascade.detectMultiScale(
                gray, scaleFactor=1.1, minNeighbors=5, minSize=self.min_face_size
            )
            
            if len(faces) == 0:
                logger.warning("No face detected in selfie")
                return {
                    'face_detected': False,
                    'error': 'No face found in selfie',
                    'liveness_score': 0.0
                }
            
            # Check for multiple faces (potential spoofing)
            if len(faces) > 1:
                logger.warning(f"Multiple faces detected in selfie: {len(faces)}")
                return {
                    'face_detected': False,
                    'error': f'Multiple faces detected ({len(faces)}), possible spoofing attempt',
                    'liveness_score': 0.0
                }
            
            # Use the detected face
            face = faces[0]
            x, y, w, h = face
            
            # Calculate face area ratio
            img_area = image.shape[0] * image.shape[1]
            face_area = w * h
            face_area_ratio = face_area / img_area
            
            # Face should be prominent in selfie
            if face_area_ratio < self.min_face_area_ratio:
                logger.warning(f"Face too small in selfie: {face_area_ratio:.3f}")
                return {
                    'face_detected': True,
                    'error': 'Face too small in selfie, possible distant/fake image',
                    'face_area_ratio': face_area_ratio,
                    'liveness_score': 0.0
                }
            
            # Extract face region
            face_region = gray[y:y+h, x:x+w]
            face_color = image[y:y+h, x:x+w]
            
            # Enhanced liveness checks
            liveness_metrics = self._enhanced_liveness_analysis(face_region, face_color, gray)
            
            return {
                'face_detected': True,
                'face_area_ratio': face_area_ratio,
                'face_dimensions': {'width': w, 'height': h},
                'liveness_metrics': liveness_metrics,
                'liveness_score': liveness_metrics['composite_score'],
                'passed': liveness_metrics['composite_score'] >= self.liveness_threshold
            }
            
        except Exception as e:
            logger.exception(f"Selfie liveness validation failed: {e}")
            return {'face_detected': False, 'error': str(e)}
    
    def _analyze_document_face_quality(self, face_gray: np.ndarray, face_color: np.ndarray) -> Dict[str, float]:
        """
        Analyze the quality of face in document photo
        """
        # Sharpness (Laplacian variance)
        laplacian_var = cv2.Laplacian(face_gray, cv2.CV_64F).var()
        sharpness_score = min(laplacian_var / 500.0, 1.0)
        
        # Brightness analysis
        mean_brightness = np.mean(face_gray)
        brightness_score = 1.0 - abs(mean_brightness - 128) / 128.0  # Optimal around 128
        
        # Contrast analysis
        contrast = np.std(face_gray)
        contrast_score = min(contrast / 50.0, 1.0)
        
        # Overall quality score
        quality_score = (sharpness_score * 0.4) + (brightness_score * 0.3) + (contrast_score * 0.3)
        
        return {
            'sharpness': sharpness_score,
            'brightness': brightness_score,
            'contrast': contrast_score,
            'quality_score': quality_score
        }
    
    def _enhanced_liveness_analysis(self, face_gray: np.ndarray, face_color: np.ndarray, full_gray: np.ndarray) -> Dict[str, float]:
        """
        Enhanced liveness analysis with multiple anti-spoofing techniques
        """
        scores = {}
        
        # 1. Eye Detection (Critical for liveness)
        eyes = self.eye_cascade.detectMultiScale(face_gray, scaleFactor=1.1, minNeighbors=3, minSize=(10, 10))
        eye_score = 0.0
        if len(eyes) >= 2:
            eye_score = 1.0
            # Analyze eye regions for naturalness
            for (ex, ey, ew, eh) in eyes[:2]:  # Use first 2 eyes
                eye_region = face_gray[ey:ey+eh, ex:ex+ew]
                eye_contrast = np.std(eye_region)
                if eye_contrast > 15:  # Good contrast indicates real eyes
                    eye_score = min(eye_score + 0.1, 1.0)
        elif len(eyes) == 1:
            eye_score = 0.3
        
        scores['eye_detection'] = eye_score
        
        # 2. Texture Analysis (LBP for natural skin texture)
        texture_score = self._calculate_texture_naturalness(face_gray)
        scores['texture_naturalness'] = texture_score
        
        # 3. Color Analysis (Natural skin tones)
        color_score = self._analyze_skin_color_naturalness(face_color)
        scores['color_naturalness'] = color_score
        
        # 4. Screen Detection (Look for screen refresh patterns)
        screen_score = self._detect_screen_artifacts(face_gray, full_gray)
        scores['screen_detection'] = screen_score
        
        # 5. Motion Blur Analysis (Natural faces have some motion blur)
        blur_score = self._analyze_motion_blur(face_gray)
        scores['motion_blur'] = blur_score
        
        # Calculate composite score with strict weights
        weights = {
            'eye_detection': 0.35,      # Most important
            'texture_naturalness': 0.25,
            'color_naturalness': 0.20,
            'screen_detection': 0.15,   # Anti-spoofing
            'motion_blur': 0.05
        }
        
        composite_score = sum(scores[key] * weights[key] for key in weights.keys())
        scores['composite_score'] = composite_score
        
        return scores
    
    def _calculate_texture_naturalness(self, face_gray: np.ndarray) -> float:
        """
        Calculate texture naturalness using Local Binary Patterns
        """
        try:
            # Simple LBP calculation
            height, width = face_gray.shape
            lbp = np.zeros_like(face_gray)
            
            for i in range(1, height - 1):
                for j in range(1, width - 1):
                    center = face_gray[i, j]
                    binary_pattern = 0
                    
                    # 8-neighbor LBP
                    neighbors = [
                        face_gray[i-1, j-1], face_gray[i-1, j], face_gray[i-1, j+1],
                        face_gray[i, j+1], face_gray[i+1, j+1], face_gray[i+1, j],
                        face_gray[i+1, j-1], face_gray[i, j-1]
                    ]
                    
                    for k, neighbor in enumerate(neighbors):
                        if neighbor >= center:
                            binary_pattern |= (1 << k)
                    
                    lbp[i, j] = binary_pattern
            
            # Calculate uniformity (natural faces have varied but structured texture)
            texture_variance = np.var(lbp)
            texture_score = min(texture_variance / 2000.0, 1.0)
            
            return texture_score
        except:
            return 0.5  # Neutral score on error
    
    def _analyze_skin_color_naturalness(self, face_color: np.ndarray) -> float:
        """
        Analyze if the face has natural skin color distribution
        """
        try:
            # Convert to different color spaces for analysis
            hsv = cv2.cvtColor(face_color, cv2.COLOR_BGR2HSV)
            
            # Analyze hue distribution (skin typically in certain ranges)
            h_channel = hsv[:, :, 0]
            s_channel = hsv[:, :, 1]
            v_channel = hsv[:, :, 2]
            
            # Skin hue ranges (adjusted for different skin tones)
            skin_pixels = 0
            total_pixels = h_channel.size
            
            for i in range(h_channel.shape[0]):
                for j in range(h_channel.shape[1]):
                    h, s, v = h_channel[i, j], s_channel[i, j], v_channel[i, j]
                    
                    # Check if pixel falls in skin color range
                    if ((h <= 25 or h >= 160) and s >= 30 and v >= 50):  # Reddish tones
                        skin_pixels += 1
                    elif (25 < h <= 40 and s >= 20 and v >= 40):  # Yellowish tones
                        skin_pixels += 1
            
            skin_ratio = skin_pixels / total_pixels
            color_score = min(skin_ratio * 2.0, 1.0)  # At least 50% skin-like pixels
            
            return color_score
        except:
            return 0.5  # Neutral score on error
    
    def _detect_screen_artifacts(self, face_gray: np.ndarray, full_gray: np.ndarray) -> float:
        """
        Detect screen artifacts that might indicate photo of screen
        """
        try:
            # Look for periodic patterns (screen refresh lines)
            # Calculate horizontal gradients
            grad_x = cv2.Sobel(face_gray, cv2.CV_64F, 1, 0, ksize=3)
            
            # Look for regular patterns in gradients
            grad_variance = np.var(grad_x)
            
            # Screen artifacts typically show high frequency patterns
            # Natural faces have smoother gradients
            if grad_variance > 1000:  # High gradient variance might indicate screen
                return 0.3
            else:
                return 1.0  # Good score for natural gradients
        except:
            return 0.8  # Default to good score on error
    
    def _analyze_motion_blur(self, face_gray: np.ndarray) -> float:
        """
        Analyze motion blur - real selfies typically have some natural blur
        """
        try:
            # Calculate Laplacian to detect blur
            laplacian_var = cv2.Laplacian(face_gray, cv2.CV_64F).var()
            
            # Natural selfies have moderate sharpness (not too sharp, not too blurry)
            if 100 < laplacian_var < 2000:
                return 1.0  # Good range for natural selfie
            elif laplacian_var > 2000:
                return 0.7  # Very sharp (might be photo of photo)
            else:
                return 0.4  # Too blurry
        except:
            return 0.6  # Neutral score on error
    
    def _cross_validate_faces(self, document_path: str, selfie_path: str) -> Dict[str, any]:
        """
        Cross-validate that the faces in document and selfie match
        """
        logger.debug("Cross-validating faces...")
        
        try:
            # Load both images
            doc_img = cv2.imread(document_path)
            selfie_img = cv2.imread(selfie_path)
            
            if doc_img is None or selfie_img is None:
                return {
                    'faces_match': False,
                    'similarity_score': 0.0,
                    'error': 'Could not load images for face matching'
                }
            
            # Convert to grayscale
            doc_gray = cv2.cvtColor(doc_img, cv2.COLOR_BGR2GRAY)
            selfie_gray = cv2.cvtColor(selfie_img, cv2.COLOR_BGR2GRAY)
            
            # Detect faces in both images
            doc_faces = self.face_cascade.detectMultiScale(doc_gray, scaleFactor=1.1, minNeighbors=5)
            selfie_faces = self.face_cascade.detectMultiScale(selfie_gray, scaleFactor=1.1, minNeighbors=5)
            
            if len(doc_faces) == 0 or len(selfie_faces) == 0:
                return {
                    'faces_match': False,
                    'similarity_score': 0.0,
                    'error': 'Face not found in one or both images'
                }
            
            # Use largest faces
            doc_face = max(doc_faces, key=lambda x: x[2] * x[3])
            selfie_face = max(selfie_faces, key=lambda x: x[2] * x[3])
            
            # Extract and normalize face regions
            doc_face_region = self._extract_normalized_face(doc_gray, doc_face)
            selfie_face_region = self._extract_normalized_face(selfie_gray, selfie_face)
            
            # Calculate similarity using template matching and histogram comparison
            similarity_score = self._calculate_face_similarity(doc_face_region, selfie_face_region)
            
            faces_match = similarity_score >= self.face_match_threshold
            
            return {
                'faces_match': faces_match,
                'similarity_score': similarity_score,
                'method': 'enhanced_opencv_matching',
                'threshold_used': self.face_match_threshold
            }
            
        except Exception as e:
            logger.exception(f"Face cross-validation failed: {e}")
            return {
                'faces_match': False,
                'similarity_score': 0.0,
                'error': str(e)
            }
    
    def _extract_normalized_face(self, gray_img: np.ndarray, face_box: tuple, size: tuple = (100, 100)) -> np.ndarray:
        """
        Extract and normalize face region for comparison
        """
        x, y, w, h = face_box
        face_region = gray_img[y:y+h, x:x+w]
        
        # Resize to standard size
        resized = cv2.resize(face_region, size)
        
        # Normalize histogram
        normalized = cv2.equalizeHist(resized)
        
        return normalized.astype(np.float32)
    
    def _calculate_face_similarity(self, face1: np.ndarray, face2: np.ndarray) -> float:
        """
        Calculate similarity between two face regions using multiple methods
        """
        try:
            # Method 1: Normalized Cross-Correlation
            correlation = cv2.matchTemplate(face1, face2, cv2.TM_CCOEFF_NORMED)[0, 0]
            correlation_score = max(0, correlation)
            
            # Method 2: Histogram Correlation
            hist1 = cv2.calcHist([face1.astype(np.uint8)], [0], None, [256], [0, 256])
            hist2 = cv2.calcHist([face2.astype(np.uint8)], [0], None, [256], [0, 256])
            hist_correlation = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)
            
            # Method 3: Structural Similarity (simplified)
            mse = np.mean((face1 - face2) ** 2)
            max_val = max(np.max(face1), np.max(face2))
            if max_val == 0:
                structural_sim = 1.0
            else:
                structural_sim = 1.0 - (mse / (max_val ** 2))
            
            # Combine scores with weights
            combined_score = (
                correlation_score * 0.4 + 
                hist_correlation * 0.3 + 
                structural_sim * 0.3
            )
            
            return max(0.0, min(1.0, combined_score))
        except:
            return 0.0
    
    def _anti_spoofing_analysis(self, selfie_path: str) -> Dict[str, any]:
        """
        Additional anti-spoofing checks
        """
        try:
            image = cv2.imread(selfie_path)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            checks = {}
            
            # 1. Check for screen reflections
            bright_pixels = np.sum(gray > 240)
            total_pixels = gray.size
            reflection_ratio = bright_pixels / total_pixels
            checks['reflection_check'] = {
                'reflection_ratio': reflection_ratio,
                'passed': reflection_ratio < 0.1  # Less than 10% very bright pixels
            }
            
            # 2. Check for image compression artifacts
            # JPEGs from screens often have different compression patterns
            # This is a simplified check
            edges = cv2.Canny(gray, 50, 150)
            edge_density = np.sum(edges > 0) / total_pixels
            checks['edge_density'] = {
                'edge_density': edge_density,
                'passed': 0.05 < edge_density < 0.3  # Natural range for selfies
            }
            
            # 3. Check for unnatural uniformity (printed photos)
            local_std = cv2.Laplacian(gray, cv2.CV_64F).var()
            checks['texture_uniformity'] = {
                'texture_variance': local_std,
                'passed': local_std > 100  # Natural faces have texture variation
            }
            
            # Calculate overall anti-spoofing score
            passed_checks = sum(1 for check in checks.values() if check['passed'])
            total_checks = len(checks)
            spoofing_score = passed_checks / total_checks
            
            return {
                'spoofing_score': spoofing_score,
                'passed': spoofing_score >= 0.66,  # At least 2/3 checks must pass
                'individual_checks': checks
            }
            
        except Exception as e:
            logger.exception(f"Anti-spoofing analysis failed: {e}")
            return {
                'spoofing_score': 0.0,
                'passed': False,
                'error': str(e)
            }
    
    def _calculate_enhanced_score(self, document_val: Dict, selfie_val: Dict, 
                                face_matching: Dict, anti_spoofing: Dict) -> Dict[str, any]:
        """
        Calculate final enhanced liveness score with strict requirements
        """
        # All stages must pass for overall success
        stages_passed = 0
        total_stages = 4
        
        # Stage 1: Document must have valid face
        document_passed = document_val.get('passed', False)
        if document_passed:
            stages_passed += 1
        
        # Stage 2: Selfie must pass liveness
        selfie_passed = selfie_val.get('passed', False)
        if selfie_passed:
            stages_passed += 1
        
        # Stage 3: Faces must match
        faces_match = face_matching.get('faces_match', False)
        if faces_match:
            stages_passed += 1
        
        # Stage 4: Anti-spoofing must pass
        anti_spoofing_passed = anti_spoofing.get('passed', False)
        if anti_spoofing_passed:
            stages_passed += 1
        
        # Calculate weighted score
        document_score = document_val.get('validation_score', 0.0)
        selfie_score = selfie_val.get('liveness_score', 0.0)
        matching_score = face_matching.get('similarity_score', 0.0)
        spoofing_score = anti_spoofing.get('spoofing_score', 0.0)
        
        # Enhanced scoring with stricter requirements
        composite_score = (
            document_score * 0.25 +
            selfie_score * 0.35 +
            matching_score * 0.25 +
            spoofing_score * 0.15
        )
        
        # Apply stage gate: All stages must pass for overall pass
        overall_passed = (stages_passed == total_stages) and (composite_score >= self.liveness_threshold)
        
        # Generate detailed explanation
        failure_reasons = []
        if not document_passed:
            failure_reasons.append("Document does not contain valid face photo")
        if not selfie_passed:
            failure_reasons.append("Selfie failed liveness detection")
        if not faces_match:
            failure_reasons.append("Faces in document and selfie do not match")
        if not anti_spoofing_passed:
            failure_reasons.append("Anti-spoofing checks failed")
        
        return {
            'liveness_score': round(composite_score, 3),
            'passed': overall_passed,
            'stages_passed': f"{stages_passed}/{total_stages}",
            'individual_scores': {
                'document_validation': document_score,
                'selfie_liveness': selfie_score,
                'face_matching': matching_score,
                'anti_spoofing': spoofing_score
            },
            'failure_reasons': failure_reasons if failure_reasons else None,
            'security_assessment': 'STRICT' if overall_passed else 'FAILED'
        }

# Global enhanced liveness detector instance
enhanced_liveness_detector = EnhancedLivenessDetector()
