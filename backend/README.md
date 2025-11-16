# Reimagining KYC with AI — Backend

This directory contains a prototype FastAPI backend that demonstrates the KYC pipeline described in the project concept.

What is included:
- `app/main.py`: FastAPI application entrypoint
- `app/routes/verify.py`: `/api/verify` endpoint that accepts `id_image` and `selfie` uploads
- `app/services/*`: modular service stubs for document classification, OCR (EasyOCR), face matching, validators, and scoring
- `app/db.py`: SQLAlchemy model placeholder for KYC records
- `Dockerfile` and top-level `docker-compose.yml` to run the backend and a Postgres DB locally

Quick start (local, development):

1) Build & start with docker-compose:

```bash
docker compose up --build
```

2) The API will be available at `http://localhost:8000` and the verification endpoint at `POST /api/verify`.

Example `curl` request (multipart form):

```bash
curl -X POST "http://localhost:8000/api/verify" \
  -F "id_image=@/path/to/id.jpg" \
  -F "selfie=@/path/to/selfie.jpg"
```

Notes & next steps:
- Replace placeholder services with production models: a trained CNN for document classification, EasyOCR templates and post-processing, FaceNet/facenet-pytorch for embeddings, and a liveness model.
- Add SHAP explainability integration at the model-level to record feature attributions for decisions.
- Harden security: use AES-GCM for PII at rest, RBAC, audit trails, rate limiting, and validate images before saving.
