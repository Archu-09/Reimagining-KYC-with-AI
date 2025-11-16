"""Optional Vision-Transformer based forgery detector (placeholder).

If `timm` and `torch` are available, a simple pretrained ViT backbone will be
loaded and a tiny head applied to produce a heuristic score. For now this is a
lightweight optional component; the rest of the system works without it.
"""
from typing import Dict, Any

try:
    import torch
    import timm
    _DL_AVAILABLE = True
except Exception:
    torch = None
    timm = None
    _DL_AVAILABLE = False


def detect_pasted_with_vit(path: str) -> Dict[str, Any]:
    """Return a placeholder dict with `score` and `suspicious`.

    If DL libs are missing, return `available: False` and a conservative score.
    """
    if not _DL_AVAILABLE:
        return {"available": False, "score": 0.0, "suspicious": False}

    # Minimal placeholder: load a pretrained vit and run a tiny forward pass on a
    # resized image. In production this should be replaced with a tuned classifier.
    try:
        model = timm.create_model('vit_base_patch16_224', pretrained=True)
        model.eval()
        from PIL import Image
        import numpy as np

        img = Image.open(path).convert('RGB').resize((224, 224))
        arr = (np.array(img) / 255.0).astype('float32')
        tensor = torch.from_numpy(arr).permute(2, 0, 1).unsqueeze(0)
        with torch.no_grad():
            out = model.forward_features(tensor)
        # simple score: mean activation magnitude
        score = float(out.abs().mean().item())
        suspicious = score > 0.3
        return {"available": True, "score": score, "suspicious": suspicious}
    except Exception:
        return {"available": False, "score": 0.0, "suspicious": False}
