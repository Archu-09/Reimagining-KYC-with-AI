#!/usr/bin/env python3
"""
Simple FastAPI server for testing the KYC frontend
Runs without Docker for quick development testing
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional
import json
import os
from pathlib import Path

try:
    from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Depends, status, Query
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
    from fastapi.responses import JSONResponse
    from jose import JWTError, jwt
    import uvicorn
except ImportError:
    print("❌ Missing dependencies. Install with:")
    print("pip3 install fastapi uvicorn python-jose[cryptography] python-multipart --break-system-packages")
    exit(1)

# Configuration
SECRET_KEY = "test-secret-key-for-development"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
ALGORITHM = "HS256"

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(title="KYC Test Backend", description="Simple test backend for KYC frontend")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OAuth2 setup
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")

# Fake user database
fake_users_db = {
    "demo@kyc.com": {
        "email": "demo@kyc.com",
        "name": "Demo User",
        "role": "user"
    },
    "admin@kyc.com": {
        "email": "admin@kyc.com", 
        "name": "Admin User",
        "role": "admin"
    }
}

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme)):
    """Get current user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        role: str = payload.get("role", "user")
        if email is None:
            raise credentials_exception
        return {"email": email, "role": role}
    except JWTError:
        raise credentials_exception

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "KYC Test Backend - Running Successfully! 🚀"}

@app.post("/api/auth/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """Traditional login endpoint"""
    username = form_data.username
    password = form_data.password
    
    if not username or not password:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    
    # Simple auth - accept any non-empty credentials
    role = "admin" if username.lower() == "admin@kyc.com" else "user"
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": username, "role": role}, 
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token, 
        "token_type": "bearer", 
        "role": role
    }

@app.get("/api/auth/me")
async def read_users_me(current_user: dict = Depends(get_current_user)):
    """Get current user information"""
    return current_user

@app.get("/api/auth/oauth/{provider}")
async def oauth_login(provider: str):
    """Mock OAuth initiation - directly simulate successful login"""
    if provider not in ['google', 'github']:
        raise HTTPException(400, f"Unsupported provider: {provider}")
    
    logger.info(f"🔑 Mock OAuth login initiated for {provider}")
    
    # For testing, directly simulate a successful OAuth flow
    # Instead of redirecting to external provider, redirect directly to our callback
    callback_url = f"http://localhost:8000/api/auth/oauth/{provider}/callback?code=mock_code&state=mock_state"
    
    return {
        "authorization_url": callback_url,
        "state": "mock_state",
        "provider": provider,
        "note": "Mock OAuth - redirecting directly to callback for testing"
    }

@app.post("/api/auth/oauth/{provider}/mock-login")
async def oauth_mock_login(provider: str):
    """Direct OAuth mock login for testing - bypasses redirect flow"""
    if provider not in ['google', 'github']:
        raise HTTPException(400, f"Unsupported provider: {provider}")
    
    # Mock user data for each provider
    mock_users = {
        'google': {
            'email': 'demo.user@gmail.com',
            'name': 'Demo Google User',
            'picture': 'https://via.placeholder.com/150',
            'provider': 'google'
        },
        'github': {
            'email': 'demo.user@github.com',
            'name': 'Demo GitHub User', 
            'avatar_url': 'https://via.placeholder.com/150',
            'provider': 'github'
        }
    }
    
    user_data = mock_users[provider]
    
    # Create JWT token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user_data['email'], "role": "user", "provider": provider},
        expires_delta=access_token_expires
    )
    
    logger.info(f"🔑 Mock {provider} OAuth login successful for {user_data['email']}")
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "email": user_data['email'],
            "name": user_data['name'],
            "provider": provider,
            "role": "user"
        },
        "message": f"Mock {provider} login successful"
    }

@app.get("/api/auth/oauth/{provider}/callback")
async def oauth_callback(
    provider: str,
    code: str = Query(...),
    state: str = Query(...)
):
    """Mock OAuth callback"""
    # Mock successful OAuth
    mock_user_data = {
        'google': {
            'email': 'user@gmail.com',
            'name': 'Google User',
            'provider': 'google'
        },
        'github': {
            'email': 'user@github.com', 
            'name': 'GitHub User',
            'provider': 'github'
        }
    }
    
    if provider not in mock_user_data:
        raise HTTPException(400, "Invalid provider")
    
    user_data = mock_user_data[provider]
    
    # Create JWT token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user_data['email'], "role": "user", "provider": provider},
        expires_delta=access_token_expires
    )
    
    # Redirect to frontend with token
    from fastapi.responses import RedirectResponse
    return RedirectResponse(f"http://localhost:3000/auth/success?token={access_token}")

@app.post("/api/verify")
async def verify_kyc(
    id_image: UploadFile = File(...),
    selfie: UploadFile = File(...),
    document_type: str = Form(default="aadhaar"),
    liveness_attestation: str = Form(default=None)
):
    """Mock KYC verification endpoint"""
    
    # Debug logging
    logger.info(f"🔍 Received verification request:")
    logger.info(f"  - ID Image: {id_image.filename} ({id_image.size} bytes, {id_image.content_type})")
    logger.info(f"  - Selfie: {selfie.filename} ({selfie.size} bytes, {selfie.content_type})")
    logger.info(f"  - Document Type: {document_type}")
    logger.info(f"  - Liveness Attestation: {liveness_attestation}")
    
    # Simulate processing delay
    await asyncio.sleep(2)
    
    # Parse liveness attestation if provided
    liveness_data = {}
    if liveness_attestation:
        try:
            liveness_data = json.loads(liveness_attestation)
        except:
            liveness_data = {"method": "unknown"}
    
    # Mock verification result
    result = {
        "verification_id": f"kyc_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "status": "completed",
        "timestamp": datetime.now().isoformat(),
        "document": {
            "type": document_type,
            "classification_confidence": 0.98,
            "extracted_data": {
                "name": "Demo User",
                "document_number": "1234-5678-9012",
                "date_of_birth": "1990-01-01",
                "address": "123 Demo Street, Test City"
            },
            "validation": {
                "format_valid": True,
                "checksum_valid": True,
                "expiry_valid": True
            }
        },
        "biometric": {
            "face_match": {
                "similarity": 0.89,
                "match": True,
                "confidence": 0.92
            },
            "liveness": {
                "score": liveness_data.get("attestation_score", 0.85),
                "passed": True,
                "method": liveness_data.get("method", "basic"),
                "details": liveness_data
            }
        },
        "risk_assessment": {
            "overall_score": 0.91,
            "risk_level": "low",
            "factors": {
                "document_authenticity": 0.95,
                "biometric_match": 0.89,
                "liveness_confidence": liveness_data.get("attestation_score", 0.85),
                "data_consistency": 0.92
            }
        },
        "explainability": {
            "decision_factors": [
                "Document format and security features verified",
                "High face matching confidence (89%)",
                f"Liveness detection passed ({liveness_data.get('method', 'basic')} method)",
                "All extracted data consistent and valid"
            ],
            "confidence_breakdown": {
                "document_processing": 95,
                "biometric_verification": 89,
                "anti_fraud_checks": 88,
                "overall_confidence": 91
            }
        }
    }
    
    logger.info(f"Mock KYC verification completed: {result['verification_id']}")
    return result

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "test-1.0.0"
    }

# Admin Panel Endpoints
@app.get("/api/admin/jobs")
async def get_admin_jobs():
    """Mock admin jobs endpoint"""
    mock_jobs = [
        {
            "id": "kyc_test_20251116_210010",
            "status": "completed",
            "created_at": "2025-11-16T20:00:10Z",
            "user_email": "user@example.com",
            "document_type": "aadhaar",
            "result": {
                "score": 91,
                "risk_level": "low",
                "face_match": True,
                "liveness_passed": True
            },
            "files": {
                "id_image": "screenshot.png",
                "selfie": "selfie.jpg"
            }
        },
        {
            "id": "kyc_test_20251116_210124", 
            "status": "completed",
            "created_at": "2025-11-16T20:01:24Z",
            "user_email": "demo@kyc.com",
            "document_type": "passport",
            "result": {
                "score": 89,
                "risk_level": "low", 
                "face_match": True,
                "liveness_passed": True
            },
            "files": {
                "id_image": "id_demo.jpg",
                "selfie": "selfie_demo.jpg"
            }
        },
        {
            "id": "kyc_test_20251116_210241",
            "status": "completed", 
            "created_at": "2025-11-16T20:02:41Z",
            "user_email": "test@user.com",
            "document_type": "aadhaar",
            "result": {
                "score": 85,
                "risk_level": "medium",
                "face_match": True,
                "liveness_passed": False
            },
            "files": {
                "id_image": "screenshot.png", 
                "selfie": "selfie.jpg"
            }
        },
        {
            "id": "kyc_test_20251116_210952",
            "status": "pending_review",
            "created_at": "2025-11-16T20:09:52Z", 
            "user_email": "pending@example.com",
            "document_type": "passport",
            "result": {
                "score": 65,
                "risk_level": "high",
                "face_match": False,
                "liveness_passed": True
            },
            "files": {
                "id_image": "id_demo.jpg",
                "selfie": "selfie_demo.jpg"
            }
        }
    ]
    
    logger.info(f"📋 Admin: Returning {len(mock_jobs)} jobs")
    return mock_jobs

@app.get("/api/admin/jobs/{job_id}")
async def get_admin_job_details(job_id: str):
    """Mock admin job details endpoint"""
    mock_job_detail = {
        "id": job_id,
        "status": "completed", 
        "created_at": "2025-11-16T20:00:10Z",
        "updated_at": "2025-11-16T20:02:15Z",
        "user_email": "user@example.com",
        "document_type": "aadhaar",
        "processing_time_ms": 2150,
        "result": {
            "verification_id": job_id,
            "status": "completed",
            "timestamp": "2025-11-16T20:02:15Z",
            "document": {
                "type": "aadhaar",
                "classification_confidence": 0.98,
                "extracted_data": {
                    "name": "Demo User",
                    "document_number": "1234-5678-9012", 
                    "date_of_birth": "1990-01-01",
                    "address": "123 Demo Street, Test City"
                },
                "validation": {
                    "format_valid": True,
                    "checksum_valid": True,
                    "expiry_valid": True
                }
            },
            "biometric": {
                "face_match": {
                    "similarity": 0.89,
                    "match": True,
                    "confidence": 0.92
                },
                "liveness": {
                    "score": 0.85,
                    "passed": True,
                    "method": "advanced",
                    "details": {}
                }
            },
            "risk_assessment": {
                "overall_score": 0.91,
                "risk_level": "low",
                "factors": {
                    "document_authenticity": 0.95,
                    "biometric_match": 0.89,
                    "liveness_confidence": 0.85,
                    "data_consistency": 0.92
                }
            },
            "explainability": {
                "decision_factors": [
                    "Document format and security features verified",
                    "High face matching confidence (89%)",
                    "Liveness detection passed successfully", 
                    "All extracted data consistent and valid"
                ],
                "confidence_breakdown": {
                    "document_processing": 95,
                    "biometric_verification": 89,
                    "anti_fraud_checks": 88,
                    "overall_confidence": 91
                }
            }
        },
        "files": {
            "id_image": "screenshot.png",
            "selfie": "selfie.jpg"
        },
        "audit_log": [
            {
                "timestamp": "2025-11-16T20:00:10Z",
                "action": "job_created",
                "user": "system",
                "details": "KYC verification job created"
            },
            {
                "timestamp": "2025-11-16T20:00:12Z",
                "action": "processing_started", 
                "user": "system",
                "details": "Document and biometric processing initiated"
            },
            {
                "timestamp": "2025-11-16T20:02:15Z",
                "action": "processing_completed",
                "user": "system", 
                "details": "Verification completed successfully"
            }
        ]
    }
    
    logger.info(f"📄 Admin: Returning job details for {job_id}")
    return mock_job_detail

@app.post("/api/admin/jobs/{job_id}/review")
async def admin_review_job(job_id: str, review_data: dict):
    """Mock admin job review endpoint"""
    logger.info(f"👨‍💼 Admin: Review submitted for {job_id}: {review_data}")
    
    return {
        "success": True,
        "job_id": job_id,
        "action": review_data.get("action", "approved"),
        "comments": review_data.get("comments", ""),
        "reviewed_by": "admin@kyc.com",
        "reviewed_at": "2025-11-16T21:15:00Z"
    }

@app.get("/api/admin/forgery/ela/{job_id}")
async def get_ela_analysis(job_id: str):
    """Mock ELA (Error Level Analysis) endpoint for forgery detection"""
    logger.info(f"🔍 Admin: ELA analysis requested for {job_id}")
    
    # Return mock ELA analysis data
    return {
        "job_id": job_id,
        "ela_analysis": {
            "forgery_probability": 0.15,
            "suspicious_regions": [
                {
                    "x": 120, "y": 80, "width": 50, "height": 30,
                    "confidence": 0.23,
                    "description": "Slight compression artifacts"
                }
            ],
            "overall_assessment": "authentic",
            "technical_details": {
                "compression_quality": 85,
                "metadata_intact": True,
                "pixel_consistency": 0.92
            }
        },
        "ela_image_url": "/mock-ela-image.jpg"  # Mock URL for ELA visualization
    }

if __name__ == "__main__":
    print("🚀 Starting KYC Test Backend...")
    print("📋 Available endpoints:")
    print("   • Frontend: http://localhost:3000")
    print("   • Backend: http://localhost:8000")
    print("   • Health: http://localhost:8000/health")
    print("   • API Docs: http://localhost:8000/docs")
    print("")
    print("🔐 Test Credentials:")
    print("   • Email: demo@kyc.com, Password: any")
    print("   • Email: admin@kyc.com, Password: any")
    print("")
    print("⚠️  This is a test server - use real OAuth for production!")
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        log_level="info"
    )
