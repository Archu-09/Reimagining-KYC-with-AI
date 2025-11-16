import os
from dotenv import load_dotenv

load_dotenv()

AWS_S3_BUCKET = os.getenv('AWS_S3_BUCKET', '')
AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY', '')
AWS_SECRET_KEY = os.getenv('AWS_SECRET_KEY', '')
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:password@postgres:5432/kyc_db')
ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY', '')
ADMIN_TOKEN = os.getenv('ADMIN_TOKEN', 'secret-admin-token')
