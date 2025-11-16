from typing import Dict, Any, Tuple

def compute_score(fields: Dict[str, Any], face_match: Dict[str, Any], liveness: Dict[str, Any], validations: Dict[str, Any]) -> Tuple[float, str, Dict[str, Any]]:
    """Compute a weighted risk score and return an explainability dict (stub).

    Weights (example): face_match 40%, liveness 20%, validations 30%, OCR consistency 10%.
    """
    face_weight = 0.4
    live_weight = 0.2
    val_weight = 0.3
    ocr_weight = 0.1

    face_score = face_match.get('similarity', 0)
    live_score = liveness.get('liveness_score', 0)

    val_score = 0
    if validations:
        ok = sum(1 for v in validations.values() if v)
        val_score = ok / max(1, len(validations))

    # OCR consistency: does name/doc no exist
    ocr_score = 0.0
    if fields.get('name'):
        ocr_score += 0.6
    if fields.get('document_number'):
        ocr_score += 0.4

    total = (face_score * face_weight + live_score * live_weight + val_score * val_weight + ocr_score * ocr_weight) * 100

    # risk mapping
    if total >= 75:
        risk = 'Low'
    elif total >= 40:
        risk = 'Medium'
    else:
        risk = 'High'

    explain = {
        'face_component': face_score * face_weight * 100,
        'liveness_component': live_score * live_weight * 100,
        'validation_component': val_score * val_weight * 100,
        'ocr_component': ocr_score * ocr_weight * 100,
    }

    return round(total, 2), risk, explain
