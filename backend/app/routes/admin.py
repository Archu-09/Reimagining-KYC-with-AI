from fastapi import APIRouter, Header, HTTPException, Response, Query
from typing import Optional
from app.db import SessionLocal, VerificationJob
from app.config import ADMIN_TOKEN
from datetime import datetime
from app.services.orchestrator import run_verification
from app.services import forgery
from fastapi.responses import StreamingResponse
import io

router = APIRouter()


def _check_admin(token: Optional[str]):
    if token != ADMIN_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized")


@router.get("/jobs")
def list_jobs(status: Optional[str] = None, x_admin_token: Optional[str] = Header(None)):
    _check_admin(x_admin_token)
    db = SessionLocal()
    q = db.query(VerificationJob)
    if status:
        q = q.filter(VerificationJob.status == status)
    jobs = q.order_by(VerificationJob.created_at.desc()).all()
    return [j.as_dict() for j in jobs]


@router.get("/jobs/{job_id}")
def get_job(job_id: int, x_admin_token: Optional[str] = Header(None)):
    _check_admin(x_admin_token)
    db = SessionLocal()
    job = db.query(VerificationJob).filter(VerificationJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job.as_dict()


@router.post("/jobs/{job_id}/review")
def review_job(job_id: int, approve: bool = True, comments: Optional[str] = None, x_admin_token: Optional[str] = Header(None)):
    _check_admin(x_admin_token)
    db = SessionLocal()
    job = db.query(VerificationJob).filter(VerificationJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    job.manual_review = True
    job.reviewer = 'admin'
    job.review_comments = comments or ''
    job.status = 'approved' if approve else 'rejected'
    job.updated_at = datetime.utcnow().isoformat()
    db.add(job)
    db.commit()
    return {"job_id": job.id, "status": job.status}


@router.post("/jobs/{job_id}/reverify")
def reverify_job(job_id: int, x_admin_token: Optional[str] = Header(None)):
    _check_admin(x_admin_token)
    db = SessionLocal()
    job = db.query(VerificationJob).filter(VerificationJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # run re-verification synchronously for now
    job.status = 'processing'
    db.add(job)
    db.commit()

    id_path = None
    selfie_path = None
    try:
        meta = job.meta or {}
        id_path = meta.get('id_path')
        selfie_path = meta.get('selfie_path')
        if not id_path or not selfie_path:
            raise HTTPException(status_code=400, detail='Missing stored file paths')

        result = run_verification(id_path, selfie_path)
        job.result = result
        job.status = 'completed'
        job.updated_at = datetime.utcnow().isoformat()
        db.add(job)
        db.commit()
        return {"job_id": job.id, "status": job.status, "result": result}
    except HTTPException:
        raise
    except Exception as e:
        job.status = 'error'
        job.updated_at = datetime.utcnow().isoformat()
        db.add(job)
        db.commit()
        raise HTTPException(status_code=500, detail=str(e))



@router.get("/forgery/ela/{job_id}")
def get_ela_image(job_id: int, as_base64: bool = Query(False), x_admin_token: Optional[str] = Header(None)):
    _check_admin(x_admin_token)
    db = SessionLocal()
    job = db.query(VerificationJob).filter(VerificationJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    meta = job.meta or {}
    id_path = meta.get('id_path')
    if not id_path:
        raise HTTPException(status_code=400, detail='No id_path stored for job')

    try:
        ela_img = forgery.ela_image(forgery._open_image(id_path))
        buf = io.BytesIO()
        ela_img.save(buf, format='PNG')
        buf.seek(0)
        if as_base64:
            import base64
            b64 = base64.b64encode(buf.read()).decode('utf-8')
            return {"job_id": job_id, "ela_base64": b64}
        return StreamingResponse(buf, media_type='image/png')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
