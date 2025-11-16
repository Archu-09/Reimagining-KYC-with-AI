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
        try:
            emb1 = _get_embedding(id_image_path)
            emb2 = _get_embedding(selfie_path)
            if emb1 is None or emb2 is None:
                return {"similarity": 0.0, "match": False, "method": "facenet", "note": "face not found"}
            sim = _cosine_similarity(emb1, emb2)
            # threshold typical values: 0.6-0.8 (tune in production)
            match = sim >= 0.6
            return {"similarity": round(sim, 4), "match": bool(match), "method": "facenet"}
        except Exception as e:
            logger.exception("Facenet matching failed: %s", e)
            return {"similarity": 0.0, "match": False, "method": "facenet", "error": str(e)}

    def liveness_check(selfie_path: str) -> Dict[str, object]:
        """Placeholder liveness detection stub. Keep interface for later integration.

        Real liveness should run a dedicated model (video or multi-frame) and return a score.
        """
        # Keep a high score by default; integrators must replace with real model.
        return {"liveness_score": 0.95, "passed": True, "method": "placeholder"}

except Exception:
    # facenet/torch not available: keep placeholder implementations
    logger.warning("facenet-pytorch or torch not available; using placeholders for face matching")

    def match_faces(id_image_path: str, selfie_path: str) -> Dict[str, object]:
        return {"similarity": 0.88, "match": True, "method": "placeholder"}

    def liveness_check(selfie_path: str) -> Dict[str, object]:
        return {"liveness_score": 0.95, "passed": True, "method": "placeholder"}
