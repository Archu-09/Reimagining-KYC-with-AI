from fastapi import APIRouter, HTTPException, Response, Query, Depends
from typing import Optional
from app.db import SessionLocal, VerificationJob, KYCRecord
from app.auth import ensure_admin
from datetime import datetime
from app.services.orchestrator import run_verification
from app.services import forgery
from fastapi.responses import StreamingResponse
import io
import json

router = APIRouter()


@router.get("/jobs")
def list_jobs(status: Optional[str] = None):
    db = SessionLocal()
    q = db.query(VerificationJob)
    if status:
        q = q.filter(VerificationJob.status == status)
    jobs = q.order_by(VerificationJob.created_at.desc()).all()
    return [j.as_dict() for j in jobs]


@router.get("/jobs/{job_id}")
def get_job(job_id: int):
    db = SessionLocal()
    job = db.query(VerificationJob).filter(VerificationJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job.as_dict()


@router.post("/jobs/{job_id}/review")
def review_job(job_id: int, approve: bool = True, comments: Optional[str] = None):
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
def reverify_job(job_id: int):
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
def get_ela_image(job_id: int, as_base64: bool = Query(False)):
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


# KYC Records endpoints
@router.get("/records")
def list_records(limit: int = Query(50, le=500), offset: int = Query(0, ge=0)):
    """List all KYC records with pagination"""
    db = SessionLocal()
    try:
        records = db.query(KYCRecord).offset(offset).limit(limit).all()
        total = db.query(KYCRecord).count()
        return {
            "records": [r.as_dict() for r in records],
            "total": total,
            "limit": limit,
            "offset": offset
        }
    finally:
        db.close()


@router.get("/records/{record_id}")
def get_record(record_id: int):
    """Get a specific KYC record"""
    db = SessionLocal()
    try:
        record = db.query(KYCRecord).filter(KYCRecord.id == record_id).first()
        if not record:
            raise HTTPException(status_code=404, detail="Record not found")
        return record.as_dict()
    finally:
        db.close()


@router.get("/stats")
def get_stats():
    """Get admin dashboard statistics"""
    db = SessionLocal()
    try:
        # Job statistics
        total_jobs = db.query(VerificationJob).count()
        pending_jobs = db.query(VerificationJob).filter(VerificationJob.status == 'pending').count()
        completed_jobs = db.query(VerificationJob).filter(VerificationJob.status == 'completed').count()
        failed_jobs = db.query(VerificationJob).filter(VerificationJob.status == 'failed').count()
        approved_jobs = db.query(VerificationJob).filter(VerificationJob.status == 'approved').count()
        rejected_jobs = db.query(VerificationJob).filter(VerificationJob.status == 'rejected').count()
        
        # KYC record statistics
        total_records = db.query(KYCRecord).count()
        low_risk = db.query(KYCRecord).filter(KYCRecord.risk_level == 'LOW').count()
        medium_risk = db.query(KYCRecord).filter(KYCRecord.risk_level == 'MEDIUM').count()
        high_risk = db.query(KYCRecord).filter(KYCRecord.risk_level == 'HIGH').count()
        
        # Average score
        from sqlalchemy import func
        avg_score = db.query(func.avg(KYCRecord.score)).scalar() or 0
        
        return {
            "jobs": {
                "total": total_jobs,
                "pending": pending_jobs,
                "completed": completed_jobs,
                "failed": failed_jobs,
                "approved": approved_jobs,
                "rejected": rejected_jobs
            },
            "records": {
                "total": total_records,
                "low_risk": low_risk,
                "medium_risk": medium_risk,
                "high_risk": high_risk,
                "average_score": round(float(avg_score), 3)
            }
        }
    finally:
        db.close()


@router.delete("/records/{record_id}")
def delete_record(record_id: int):
    """Delete a KYC record"""
    db = SessionLocal()
    try:
        record = db.query(KYCRecord).filter(KYCRecord.id == record_id).first()
        if not record:
            raise HTTPException(status_code=404, detail="Record not found")
        
        db.delete(record)
        db.commit()
        return {"message": f"Record {record_id} deleted successfully"}
    finally:
        db.close()
