"""
ClipGod Backend - Main Application
A FastAPI backend for video transcription and clip generation
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import init_db, get_db
from app.routers.api import router as api_router
from app.models.database import TranscriptionJob, ClipJob, JobStatus


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_db()
    # Create upload directories
    settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    settings.CLIPS_DIR.mkdir(parents=True, exist_ok=True)
    yield
    # Shutdown
    pass


app = FastAPI(
    title="ClipGod API",
    description="Automated video clipping with AI transcription",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files for clips
app.mount("/clips", StaticFiles(directory=settings.CLIPS_DIR), name="clips")
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# Include routers
app.include_router(api_router, prefix="/api")


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "clipgod"}


@app.get("/")
async def root():
    return {
        "message": "ClipGod API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }