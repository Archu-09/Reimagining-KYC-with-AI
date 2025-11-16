from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import verify
from app.routes import async_routes
from app.routes import admin

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

@app.get("/")
def root():
    return {"message": "Reimagining KYC with AI backend. See /api/verify"}
