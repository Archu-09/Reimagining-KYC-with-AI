from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
import shutil
import tempfile
from typing import Any, Dict

from app.services import classifier, ocr_service, face_service, validators, scoring
from app.services.orchestrator import run_verification
from app.db import SessionLocal, VerificationJob
from datetime import datetime
import json
from sqlalchemy.exc import SQLAlchemyError

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
async def verify(id_image: UploadFile = File(...), selfie: UploadFile = File(...)):
    # save uploads to temp files
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix="_id") as f_id:
            shutil.copyfileobj(id_image.file, f_id)
            id_path = f_id.name

        with tempfile.NamedTemporaryFile(delete=False, suffix="_selfie") as f_sf:
            shutil.copyfileobj(selfie.file, f_sf)
            selfie_path = f_sf.name

        # Use orchestrator to run full pipeline
        result = run_verification(id_path, selfie_path)

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
                },
            )
            db.add(job)
            db.commit()
            db.refresh(job)
        except SQLAlchemyError:
            # If DB fails, ignore for now but continue to return result
            pass

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
