import os
import shutil
import tempfile
from datetime import datetime
from typing import Dict, Any

from app.services import classifier, ocr_service, face_service, validators, scoring, forgery


def run_verification(id_path: str, selfie_path: str) -> Dict[str, Any]:
    """Run the standard verification pipeline and return a serializable dict."""
    # 1. Document classification
    doc_type = classifier.classify_document(id_path)

    # 2. OCR extraction
    fields = ocr_service.extract_fields(id_path, doc_type)

    # 3. Face matching
    face_match = face_service.match_faces(id_path, selfie_path)

    # 4. Liveness
    liveness = face_service.liveness_check(selfie_path)

    # 5. Validators
    validations = validators.run_validations(id_path, doc_type, fields)

    # 6. Forgery detection (document-level)
    forgery_report = forgery.run_forgery_checks(id_path)

    # 6. Scoring
    score, risk_level, explainability = scoring.compute_score(fields, face_match, liveness, validations)

    result = {
        "document_type": doc_type,
        "extracted_fields": fields,
        "face_match": face_match,
        "liveness": liveness,
        "validations": validations,
        "forgery": forgery_report,
        "score": score,
        "risk_level": risk_level,
        "explainability": explainability,
        "timestamp": datetime.utcnow().isoformat(),
    }

    return result
