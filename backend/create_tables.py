"""Simple helper to create DB tables for local development.

Usage:
    python create_tables.py

This will use the same `DATABASE_URL` from `app.config`/environment and call
`Base.metadata.create_all(engine)` to create tables locally. For production,
use Alembic migrations instead.
"""
from app.db import Base, engine
from app.config import DATABASE_URL
import os

def main():
    print("DATABASE_URL:", DATABASE_URL or os.environ.get('DATABASE_URL'))
    print("Creating database tables (development only)...")
    Base.metadata.create_all(bind=engine)
    print("Done.")

if __name__ == '__main__':
    main()
