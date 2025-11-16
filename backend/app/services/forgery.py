"""Forgery detection helpers.

Implements a set of research-backed but lightweight heuristics and placeholders:
- Error Level Analysis (ELA)
- Heuristic placeholder for pasted signatures / altered numbers (ViT placeholder)
- Microtext detection using OCR bounding boxes
- Hologram / iridescence heuristics
- Preprocessing helpers for denoising and illumination normalization

These are intentionally modular so heavy DL models (Vision Transformers) can be plugged
in later; for now heuristics provide reasonable signals for scoring and manual review.
"""
from __future__ import annotations

import io
import math
from typing import Dict, Any

from PIL import Image, ImageChops, ImageEnhance, ImageFilter
import numpy as np
try:
    import cv2
    _CV2_AVAILABLE = True
except Exception:
    cv2 = None
    _CV2_AVAILABLE = False

try:
    import easyocr
    _EASY_OCR_AVAILABLE = True
except Exception:
    _EASY_OCR_AVAILABLE = False

try:
    import torch
    import timm
    _DL_AVAILABLE = True
except Exception:
    _DL_AVAILABLE = False


def _open_image(path: str) -> Image.Image:
    return Image.open(path).convert("RGB")


def ela_image(img: Image.Image, quality: int = 90) -> Image.Image:
    """Compute an ELA image by re-saving at given JPEG quality and subtracting.

    Returns a PIL Image showing amplified differences.
    """
    with io.BytesIO() as buffer:
        img.save(buffer, 'JPEG', quality=quality)
        buffer.seek(0)
        recompressed = Image.open(buffer).convert('RGB')

    diff = ImageChops.difference(img, recompressed)
    # amplify
    extrema = diff.getextrema()
    max_diff = max([e[1] for e in extrema]) or 1
    scale = 255.0 / max_diff
    ela = ImageEnhance.Brightness(diff).enhance(scale)
    return ela


def ela_score(path: str, quality: int = 90) -> float:
    """Return a simple numeric ELA anomaly score (mean of ELA intensity).

    Higher means more suspicious. This is a heuristic; thresholds should be calibrated.
    """
    img = _open_image(path)
    ela = ela_image(img, quality=quality)
    gray = ela.convert('L')
    arr = np.array(gray).astype(np.float32)
    return float(arr.mean())


def detect_pasted_regions_heurstic(path: str, window: int = 64) -> Dict[str, Any]:
    """Heuristic detector for pasted regions (signatures, numbers).

    Approach: compute local noise/blur variance across sliding windows and flag
    windows whose local statistical profile deviates from neighbors (possible paste).
    Returns a dict with `suspiciousness` score and simple map stats.
    """
    if _CV2_AVAILABLE:
        img = cv2.imread(path)
        if img is None:
            return {"suspiciousness": 0.0, "method": "error_read"}

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        h, w = gray.shape
        scores = []
        for y in range(0, h, window):
            for x in range(0, w, window):
                patch = gray[y:y+window, x:x+window]
                if patch.size == 0:
                    continue
                # local Laplacian variance indicates texture/noise
                lap = cv2.Laplacian(patch, cv2.CV_64F)
                var = float(lap.var())
                scores.append(var)

        if not scores:
            return {"suspiciousness": 0.0, "method": "empty"}

        global_median = float(np.median(scores))
        outlier_fraction = float((np.array(scores) > (global_median * 3)).sum()) / max(1, len(scores))
        suspiciousness = min(1.0, outlier_fraction * 3.0)
        return {"suspiciousness": suspiciousness, "outlier_fraction": outlier_fraction, "method": "laplacian_variance"}
    else:
        # Fallback: use PIL-based block variance heuristic
        try:
            img = Image.open(path).convert('L')
            arr = np.array(img)
            h, w = arr.shape
            scores = []
            for y in range(0, h, window):
                for x in range(0, w, window):
                    patch = arr[y:y+window, x:x+window]
                    if patch.size == 0:
                        continue
                    var = float(patch.var())
                    scores.append(var)
            if not scores:
                return {"suspiciousness": 0.0, "method": "empty_fallback"}
            global_median = float(np.median(scores))
            outlier_fraction = float((np.array(scores) > (global_median * 3)).sum()) / max(1, len(scores))
            suspiciousness = min(1.0, outlier_fraction * 3.0)
            return {"suspiciousness": suspiciousness, "outlier_fraction": outlier_fraction, "method": "pil_variance_fallback"}
        except Exception:
            return {"suspiciousness": 0.0, "method": "fallback_error"}


def detect_microtext(path: str, min_height_px: int = 6) -> Dict[str, Any]:
    """Detect presence of very small text (microtext) via OCR bounding boxes.

    Returns dict with flag and stats. Requires `easyocr` for best results.
    """
    if not _EASY_OCR_AVAILABLE:
        return {"microtext": False, "method": "easyocr_missing"}

    reader = easyocr.Reader(['en'])
    results = reader.readtext(path, detail=1)
    small_boxes = 0
    total_boxes = 0
    for (bbox, text, conf) in results:
        total_boxes += 1
        # bbox is 4 points; compute height
        ys = [pt[1] for pt in bbox]
        height = max(ys) - min(ys)
        if height <= min_height_px:
            small_boxes += 1

    if total_boxes == 0:
        return {"microtext": False, "total_boxes": 0}

    fraction = small_boxes / total_boxes
    return {"microtext": fraction > 0.1, "fraction": fraction, "total_boxes": total_boxes, "method": "easyocr"}


def detect_hologram(path: str) -> Dict[str, Any]:
    """Heuristic detection for holograms / iridescent security features.

    Detects low correlation between color channels and presence of specular highlights
    across small regions. This is a heuristic and will produce false positives.
    """
    if _CV2_AVAILABLE:
        img = cv2.imread(path)
        if img is None:
            return {"hologram": False, "method": "error_read"}

        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        # compute channel correlations
        r = img[:, :, 0].astype(np.float32).ravel()
        g = img[:, :, 1].astype(np.float32).ravel()
        b = img[:, :, 2].astype(np.float32).ravel()
        def corr(a, b):
            if a.size == 0 or b.size == 0:
                return 1.0
            a_mean = a.mean()
            b_mean = b.mean()
            num = ((a - a_mean) * (b - b_mean)).sum()
            den = math.sqrt(((a - a_mean)**2).sum() * ((b - b_mean)**2).sum())
            return float(num / (den + 1e-8))

        rg = corr(r, g)
        rb = corr(r, b)
        gb = corr(g, b)
        avg_corr = (abs(rg) + abs(rb) + abs(gb)) / 3.0

        # detect specular highlights
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        _, bright = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY)
        bright_fraction = float((bright > 0).sum()) / (bright.size + 1)
    else:
        # fallback using PIL
        try:
            pil = Image.open(path).convert('RGB')
            arr = np.array(pil)
            r = arr[:, :, 0].astype(np.float32).ravel()
            g = arr[:, :, 1].astype(np.float32).ravel()
            b = arr[:, :, 2].astype(np.float32).ravel()
            gray = np.array(pil.convert('L'))
            bright_fraction = float((gray > 240).sum()) / (gray.size + 1)
        except Exception:
            return {"hologram": False, "method": "fallback_error"}

    def corr(a, b):
        if a.size == 0 or b.size == 0:
            return 1.0
        a_mean = a.mean()
        b_mean = b.mean()
        num = ((a - a_mean) * (b - b_mean)).sum()
        den = math.sqrt(((a - a_mean)**2).sum() * ((b - b_mean)**2).sum())
        return float(num / (den + 1e-8))

    rg = corr(r, g)
    rb = corr(r, b)
    gb = corr(g, b)
    avg_corr = (abs(rg) + abs(rb) + abs(gb)) / 3.0

    hologram_score = max(0.0, (1.0 - avg_corr)) * (bright_fraction * 10.0)
    hologram_score = min(1.0, hologram_score)
    return {"hologram": hologram_score > 0.12, "score": hologram_score, "avg_corr": avg_corr, "bright_fraction": bright_fraction, "method": "channel_correlation"}


def preprocess_image(path: str, denoise: bool = True, normalize: bool = True) -> Image.Image:
    """Apply preprocessing steps: denoising, histogram equalization / CLAHE, and mild sharpening.

    Returns a PIL Image suitable for downstream forgery checks.
    """
    img = _open_image(path)
    arr = np.array(img)

    if denoise:
        if _CV2_AVAILABLE:
            # bilateral filter preserves edges
            arr = cv2.bilateralFilter(arr, d=9, sigmaColor=75, sigmaSpace=75)
        else:
            # mild PIL blur fallback
            pil = Image.fromarray(arr)
            pil = pil.filter(ImageFilter.MedianFilter(size=3))
            arr = np.array(pil)

    if normalize:
        if _CV2_AVAILABLE:
            lab = cv2.cvtColor(arr, cv2.COLOR_RGB2LAB)
            l, a, b = cv2.split(lab)
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
            cl = clahe.apply(l)
            merged = cv2.merge((cl,a,b))
            arr = cv2.cvtColor(merged, cv2.COLOR_LAB2RGB)
        else:
            try:
                pil = Image.fromarray(arr)
                pil = ImageEnhance.Contrast(pil).enhance(1.1)
                arr = np.array(pil)
            except Exception:
                pass

    img_out = Image.fromarray(arr)
    img_out = img_out.filter(ImageFilter.SHARPEN)
    return img_out


def run_forgery_checks(path: str) -> Dict[str, Any]:
    """Run the complete forgery detection suite and return a structured report.

    This function is deliberately conservative and returns a mix of heuristic signals
    and recommended next-steps (e.g., escalate to DL model/manual review) under `flags`.
    """
    # Preprocess
    pre = preprocess_image(path)
    # ELA
    ela_sc = ela_score(path)
    ela_img = ela_image(pre)

    # Pasted region heuristic
    paste = detect_pasted_regions_heurstic(path)

    # Microtext
    micro = detect_microtext(path)

    # Hologram
    holo = detect_hologram(path)

    # Signature/ViT placeholder
    # Vision Transformer detector (optional)
    try:
        from app.services.vit_detector import detect_pasted_with_vit
        vit_note = detect_pasted_with_vit(path)
    except Exception:
        vit_note = {"method": "heuristic_fallback", "available": False}

    report = {
        "ela_score": ela_sc,
        "paste_heuristic": paste,
        "microtext": micro,
        "hologram": holo,
        "vit": vit_note,
        "flags": {
            "ela_suspicious": ela_sc > 10.0,
            "pasted_regions": paste.get('suspiciousness', 0.0) > 0.3,
            "microtext_present": micro.get('microtext', False),
            "hologram_detected": holo.get('hologram', False),
        },
    }
    return report
