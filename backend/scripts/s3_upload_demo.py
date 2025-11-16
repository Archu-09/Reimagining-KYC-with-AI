"""Demo script to validate S3/MinIO uploads using `app.services.storage.persist_file`.

Usage (from repository root):
  PYTHONPATH=backend python backend/scripts/s3_upload_demo.py

Set env vars for MinIO/local dev if desired:
  export AWS_S3_BUCKET=test-bucket
  export AWS_S3_ENDPOINT_URL=http://localhost:9000
  export AWS_ACCESS_KEY_ID=minioadmin
  export AWS_SECRET_ACCESS_KEY=minioadmin

"""
import tempfile
import os
from app.services.storage import persist_file


def main():
    with tempfile.NamedTemporaryFile(delete=False, suffix='.txt') as f:
        f.write(b'Demo upload from KYC repo')
        path = f.name

    key = f"demo_uploads/{os.path.basename(path)}"
    uri = persist_file(path, key)
    print('Uploaded URI:', uri)


if __name__ == '__main__':
    main()
