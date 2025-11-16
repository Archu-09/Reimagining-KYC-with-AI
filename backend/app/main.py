from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import sys

from app.routes import verify
from app.routes import async_routes
from app.routes import admin
from app.routes import auth as auth_routes

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout,
)

app = FastAPI(title="Reimagining KYC with AI - Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(verify.router, prefix="/api")
app.include_router(async_routes.router, prefix="/api")
app.include_router(admin.router, prefix="/api/admin")
app.include_router(auth_routes.router, prefix="/api/auth")

@app.get("/")
def root():
    return {"message": "Reimagining KYC with AI backend. See /api/verify"}
