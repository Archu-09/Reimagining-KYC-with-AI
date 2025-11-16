"""Optional Celery app and task definitions.

If `celery` is installed and `BROKER_URL` is provided, tasks can be enqueued
from the API; otherwise the system falls back to FastAPI BackgroundTasks.
"""
import os
from typing import Any

_CELERY_AVAILABLE = False
celery_app = None
process_job = None

try:
    from celery import Celery
    _CELERY_AVAILABLE = True
except Exception:
    Celery = None
    _CELERY_AVAILABLE = False

if _CELERY_AVAILABLE:
    BROKER = os.getenv('BROKER_URL', 'redis://redis:6379/0')
    celery_app = Celery('kyc', broker=BROKER)

    @celery_app.task(name='kyc.process_job')
    def process_job(job_id: int, id_path: str, selfie_path: str, callback_url: str | None):
        # Import here to avoid heavy imports at module load
        from app.services.orchestrator import run_verification
        from app.db import SessionLocal, VerificationJob
        import requests
        from datetime import datetime

        result = run_verification(id_path, selfie_path)
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
            try:
                requests.post(callback_url, json={'job_id': job_id, 'result': result}, timeout=10)
            except Exception:
                pass

    def enqueue_process_job(job_id: int, id_path: str, selfie_path: str, callback_url: str | None) -> Any:
        return process_job.apply_async((job_id, id_path, selfie_path, callback_url))
else:
    def enqueue_process_job(job_id: int, id_path: str, selfie_path: str, callback_url: str | None) -> None:
        raise RuntimeError('Celery not available')
