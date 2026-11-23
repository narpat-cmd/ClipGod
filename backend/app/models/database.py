"""
ClipGod Database Models
SQLAlchemy models for persistence
"""

from sqlalchemy import Column, String, Float, DateTime, Text, Integer, Enum as SQLEnum, ForeignKey
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime
import uuid
import enum


Base = declarative_base()


class JobStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class TranscriptionJob(Base):
    """Video transcription job"""
    __tablename__ = "transcription_jobs"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    url = Column(String(500), nullable=False)
    title = Column(String(500), nullable=True)
    duration = Column(Float, nullable=True)
    thumbnail = Column(String(500), nullable=True)
    platform = Column(String(50), nullable=True)
    language = Column(String(10), default="auto")
    model = Column(String(20), default="base")
    status = Column(SQLEnum(JobStatus), default=JobStatus.PENDING)
    transcript = Column(Text, nullable=True)
    segments = Column(JSON, nullable=True)  # List of {start, end, text, confidence}
    error = Column(Text, nullable=True)
    video_path = Column(String(500), nullable=True)  # Local path to downloaded video
    audio_path = Column(String(500), nullable=True)  # Local path to extracted audio
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationship
    clips = relationship("ClipJob", back_populates="transcription_job", cascade="all, delete-orphan")


class ClipJob(Base):
    """Video clip generation job"""
    __tablename__ = "clip_jobs"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    transcription_job_id = Column(String(36), ForeignKey("transcription_jobs.id"), nullable=False)
    start_time = Column(Float, nullable=False)
    end_time = Column(Float, nullable=False)
    template = Column(String(50), default="hormozi")
    caption_style = Column(String(50), default="default")
    output_format = Column(String(10), default="mp4")
    aspect_ratio = Column(String(10), default="9:16")
    status = Column(SQLEnum(JobStatus), default=JobStatus.PENDING)
    output_path = Column(String(500), nullable=True)
    file_size = Column(Integer, nullable=True)
    duration = Column(Float, nullable=True)
    error = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationship
    transcription_job = relationship("TranscriptionJob", back_populates="clips")


class ViralClipSuggestion(Base):
    """AI-suggested viral clip from analysis"""
    __tablename__ = "viral_clip_suggestions"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    transcription_job_id = Column(String(36), ForeignKey("transcription_jobs.id"), nullable=False)
    start_time = Column(Float, nullable=False)
    end_time = Column(Float, nullable=True)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    viral_score = Column(Integer, nullable=False)  # 1-100
    reason = Column(Text, nullable=True)
    keywords = Column(JSON, nullable=True)  # List of strings
    created_at = Column(DateTime, default=datetime.utcnow)