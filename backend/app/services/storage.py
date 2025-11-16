"""Storage helpers with optional S3 support.

Provides `persist_file` which will attempt to upload to S3 (if `boto3` and AWS
env vars are available) and otherwise return a local `file://` URI.
"""
import os
from typing import Tuple

try:
    import boto3
    from botocore.exceptions import BotoCoreError, NoCredentialsError
    _BOTO3_AVAILABLE = True
except Exception:
    boto3 = None
    _BOTO3_AVAILABLE = False


def _local_uri(path: str) -> str:
    return f"file://{os.path.abspath(path)}"


def upload_file_to_s3(path: str, key: str) -> str | None:
    """Upload `path` to S3 under `key`. Returns S3 URI or None on failure.

    Expects `AWS_S3_BUCKET` env var to be set.
    """
    if not _BOTO3_AVAILABLE:
        return None

    bucket = os.getenv('AWS_S3_BUCKET')
    if not bucket:
        return None

    # Support custom endpoint (MinIO) and explicit credentials for local dev
    endpoint = os.getenv('AWS_S3_ENDPOINT_URL')
    access_key = os.getenv('AWS_ACCESS_KEY_ID') or os.getenv('AWS_ACCESS_KEY')
    secret_key = os.getenv('AWS_SECRET_ACCESS_KEY') or os.getenv('AWS_SECRET_KEY')

    try:
        client_kwargs = {}
        if endpoint:
            client_kwargs['endpoint_url'] = endpoint
        if access_key and secret_key:
            client_kwargs['aws_access_key_id'] = access_key
            client_kwargs['aws_secret_access_key'] = secret_key

        s3 = boto3.client('s3', **client_kwargs)

        # ensure bucket exists (safe for MinIO/local dev)
        try:
            existing = s3.list_buckets()
            names = [b['Name'] for b in existing.get('Buckets', [])]
            if bucket not in names:
                s3.create_bucket(Bucket=bucket)
        except Exception:
            # ignore bucket creation failures; attempt upload anyway
            pass

        s3.upload_file(path, bucket, key)
        return f"s3://{bucket}/{key}"
    except (BotoCoreError, NoCredentialsError, Exception):
        return None


def persist_file(path: str, key: str) -> str:
    """Persist file and return a URI (s3://... or file://...)."""
    uri = upload_file_to_s3(path, key)
    if uri:
        return uri
    return _local_uri(path)
