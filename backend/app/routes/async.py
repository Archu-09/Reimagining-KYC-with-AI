from fastapi import APIRouter, UploadFile, File, BackgroundTasks, HTTPException
from app.services.orchestrator import run_verification
from app.db import SessionLocal, VerificationJob
from datetime import datetime
import shutil
import tempfile
import requests

router = APIRouter()


def _post_callback(url: str, payload: dict):
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception:
        # ignore callback failures here; could add retry logic
        pass


def _process_and_callback(job_id: int, id_path: str, selfie_path: str, callback_url: str | None):
    result = run_verification(id_path, selfie_path)

    # update job in DB
    try:
        db = SessionLocal()
        job = db.query(VerificationJob).filter(VerificationJob.id == job_id).first()
        if job:
            job.status = 'completed'
            job.result = result
            job.updated_at = datetime.utcnow().isoformat()
            db.add(job)
            db.commit()
    except Exception:
        pass

    if callback_url:
        _post_callback(callback_url, {"job_id": job_id, "result": result})


@router.post("/verify_async")
async def verify_async(background_tasks: BackgroundTasks, id_image: UploadFile = File(...), selfie: UploadFile = File(...), callback_url: str | None = None):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix="_id") as f_id:
            shutil.copyfileobj(id_image.file, f_id)
            id_path = f_id.name

        with tempfile.NamedTemporaryFile(delete=False, suffix="_selfie") as f_sf:
            shutil.copyfileobj(selfie.file, f_sf)
            selfie_path = f_sf.name

        db = SessionLocal()
        job = VerificationJob(
            status='pending',
            callback_url=callback_url,
            created_at=datetime.utcnow().isoformat(),
            updated_at=datetime.utcnow().isoformat(),
            meta={'id_path': id_path, 'selfie_path': selfie_path},
        )
        db.add(job)
        db.commit()
        db.refresh(job)

        # schedule background processing
        background_tasks.add_task(_process_and_callback, job.id, id_path, selfie_path, callback_url)

        return {"job_id": job.id, "status": "scheduled"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/verify_batch")
async def verify_batch(background_tasks: BackgroundTasks, id_images: list[UploadFile] = File(...), selfies: list[UploadFile] = File(...), callback_url: str | None = None):
    if len(id_images) != len(selfies):
        raise HTTPException(status_code=400, detail="id_images and selfies must have same length")

    job_ids = []
    try:
        for id_file, sf_file in zip(id_images, selfies):
            with tempfile.NamedTemporaryFile(delete=False, suffix="_id") as f_id:
                shutil.copyfileobj(id_file.file, f_id)
                id_path = f_id.name

            with tempfile.NamedTemporaryFile(delete=False, suffix="_selfie") as f_sf:
                shutil.copyfileobj(sf_file.file, f_sf)
                selfie_path = f_sf.name

            db = SessionLocal()
            job = VerificationJob(
                status='pending',
                callback_url=callback_url,
                created_at=datetime.utcnow().isoformat(),
                updated_at=datetime.utcnow().isoformat(),
                meta={'id_path': id_path, 'selfie_path': selfie_path},
            )
            db.add(job)
            db.commit()
            db.refresh(job)
            job_ids.append(job.id)
            background_tasks.add_task(_process_and_callback, job.id, id_path, selfie_path, callback_url)

        return {"scheduled_jobs": job_ids}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
