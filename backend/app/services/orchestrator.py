import os
import shutil
import tempfile
from datetime import datetime
from typing import Dict, Any
import logging

from app.services import classifier, ocr_service, face_service, validators, scoring, forgery

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def run_verification(id_path: str, selfie_path: str) -> Dict[str, Any]:
    """Run the standard verification pipeline and return a serializable dict."""
    logger.debug("[ORCHESTRATOR] Starting pipeline")
    
    # 1. Document classification
    logger.debug("[ORCHESTRATOR] Step 1: Classifying document...")
    doc_type = classifier.classify_document(id_path)
    logger.info(f"  → Document type: {doc_type}")

    # 2. OCR extraction
    logger.debug("[ORCHESTRATOR] Step 2: Extracting fields via OCR...")
    fields = ocr_service.extract_fields(id_path, doc_type)
    logger.info(f"  → Extracted {len(fields)} fields")

    # 3. Face matching
    logger.debug("[ORCHESTRATOR] Step 3: Matching faces...")
    face_match = face_service.match_faces(id_path, selfie_path)
    logger.info(f"  → Face match: {face_match.get('match', False)}, Score: {face_match.get('score', 0):.2f}")

    # 4. Liveness
    logger.debug("[ORCHESTRATOR] Step 4: Checking liveness...")
    liveness = face_service.liveness_check(selfie_path)
    logger.info(f"  → Liveness passed: {liveness.get('passed', False)}, Score: {liveness.get('score', 0):.2f}")

    # 5. Validators
    logger.debug("[ORCHESTRATOR] Step 5: Running validations...")
    validations = validators.run_validations(id_path, doc_type, fields)
    logger.info(f"  → Validation results: {validations}")

    # 6. Forgery detection (document-level)
    logger.debug("[ORCHESTRATOR] Step 6: Checking for forgery...")
    forgery_report = forgery.run_forgery_checks(id_path)
    logger.info(f"  → Forgery check: {forgery_report}")

    # 7. Scoring
    logger.debug("[ORCHESTRATOR] Step 7: Computing score...")
    score, risk_level, explainability = scoring.compute_score(fields, face_match, liveness, validations)
    logger.info(f"  → Score: {score:.2f}, Risk Level: {risk_level}")

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

    logger.debug("[ORCHESTRATOR] Pipeline completed")
    return result
