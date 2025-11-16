from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from pydantic import BaseModel
import shutil
import tempfile
from typing import Any, Dict
import logging

from app.services import classifier, ocr_service, face_service, validators, scoring
from app.services.orchestrator import run_verification
from app.db import SessionLocal, VerificationJob
from datetime import datetime
import json
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

router = APIRouter()


class VerificationResult(BaseModel):
    document_type: str
    extracted_fields: Dict[str, Any]
    face_match: Dict[str, Any]
    liveness: Dict[str, Any]
    validations: Dict[str, Any]
    score: float
    risk_level: str
    explainability: Dict[str, Any]


@router.post("/verify", response_model=VerificationResult)
async def verify(id_image: UploadFile = File(...), selfie: UploadFile = File(...), liveness_attestation: str = Form(None)):
    logger.info("=" * 60)
    logger.info("[VERIFY] Request received")
    logger.info(f"  ID Image: {id_image.filename} ({id_image.content_type})")
    logger.info(f"  Selfie: {selfie.filename} ({selfie.content_type})")
    logger.info(f"  Liveness Attestation: {'Present' if liveness_attestation else 'Missing'}")
    # save uploads to temp files
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix="_id") as f_id:
            shutil.copyfileobj(id_image.file, f_id)
            id_path = f_id.name
        logger.info(f"[VERIFY] ID image saved to {id_path}")

        with tempfile.NamedTemporaryFile(delete=False, suffix="_selfie") as f_sf:
            shutil.copyfileobj(selfie.file, f_sf)
            selfie_path = f_sf.name
        logger.info(f"[VERIFY] Selfie saved to {selfie_path}")

        # Use orchestrator to run full pipeline
        logger.info("[VERIFY] Starting verification pipeline...")
        result = run_verification(id_path, selfie_path)
        logger.info("[VERIFY] Pipeline completed successfully")

        # attach liveness attestation (if provided) to the result/meta
        attestation_obj = None
        if liveness_attestation:
            try:
                attestation_obj = json.loads(liveness_attestation)
                logger.info(f"[VERIFY] Attestation parsed: {attestation_obj}")
                # include into result under liveness.attestation for transparency
                if isinstance(result, dict):
                    result.setdefault('liveness', {})
                    result['liveness']['attestation'] = attestation_obj
            except Exception as e:
                # ignore malformed attestation but continue
                logger.error(f"[VERIFY] Failed to parse attestation: {e}")
                attestation_obj = None

        # persist job record (sync response does not create a job by default)
        try:
            db = SessionLocal()
            job = VerificationJob(
                status='completed',
                created_at=datetime.utcnow().isoformat(),
                updated_at=datetime.utcnow().isoformat(),
                result=result,
                meta={
                    'id_path': id_path,
                    'selfie_path': selfie_path,
                    'liveness_attestation': attestation_obj,
                },
            )
            db.add(job)
            db.commit()
            db.refresh(job)
            logger.info(f"[VERIFY] Job persisted with ID: {job.id}")
        except SQLAlchemyError as e:
            # If DB fails, ignore for now but continue to return result
            logger.warning(f"[VERIFY] Database error (non-blocking): {e}")
            pass

        logger.info("=" * 60)
        return result

    except Exception as e:
        logger.error(f"[VERIFY] FAILED: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
