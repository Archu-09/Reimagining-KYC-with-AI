import os
from sqlalchemy import create_engine, Column, Integer, String, Float, JSON, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:password@postgres:5432/kyc_db')

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class KYCRecord(Base):
    __tablename__ = 'kyc_records'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=True)
    document_type = Column(String, nullable=True)
    document_number = Column(String, nullable=True)
    score = Column(Float, nullable=True)
    risk_level = Column(String, nullable=True)
    meta = Column(JSON)

    def as_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'document_type': self.document_type,
            'document_number': self.document_number,
            'score': self.score,
            'risk_level': self.risk_level,
            'meta': self.meta,
        }


class VerificationJob(Base):
    __tablename__ = 'verification_jobs'
    id = Column(Integer, primary_key=True, index=True)
    status = Column(String, default='pending')
    callback_url = Column(String, nullable=True)
    result = Column(JSON, nullable=True)
    created_at = Column(String, nullable=True)
    updated_at = Column(String, nullable=True)
    manual_review = Column(String, nullable=True)
    reviewer = Column(String, nullable=True)
    review_comments = Column(String, nullable=True)
    meta = Column(JSON, nullable=True)

    def as_dict(self):
        return {
            'id': self.id,
            'status': self.status,
            'callback_url': self.callback_url,
            'result': self.result,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'manual_review': self.manual_review,
            'reviewer': self.reviewer,
            'review_comments': self.review_comments,
            'meta': self.meta,
        }


class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    provider = Column(String, nullable=True)  # google, github, email
    provider_id = Column(String, nullable=True)  # OAuth provider user ID
    picture = Column(String, nullable=True)  # Profile picture URL
    verified_email = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def as_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'provider': self.provider,
            'picture': self.picture,
            'verified_email': self.verified_email,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
