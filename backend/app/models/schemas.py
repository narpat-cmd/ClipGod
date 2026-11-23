"""
ClipGod API Schemas
Pydantic models for request/response validation
"""

from pydantic import BaseModel, HttpUrl, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class HealthResponse(BaseModel):
    """Health check response"""
    status: str = "healthy"
    service: str = "ClipGod API"
    timestamp: datetime


class VideoInfo(BaseModel):
    """Video metadata information"""
    title: str
    duration: float
    thumbnail: Optional[str] = None
    platform: str


class TranscriptionRequest(BaseModel):
    """Request to start transcription"""
    url: HttpUrl = Field(..., description="Video URL (YouTube, TikTok, Instagram, etc.)")
    language: Optional[str] = Field("auto", description="Language code or 'auto'")
    model: Optional[str] = Field("base", description="Whisper model size")


class TranscriptionSegment(BaseModel):
    """Single transcription segment with timing"""
    start: float
    end: float
    text: str
    confidence: Optional[float] = None


class TranscriptionResponse(BaseModel):
    """Transcription job response"""
    job_id: UUID
    status: str  # pending, processing, completed, failed
    video_info: Optional[VideoInfo] = None
    transcript: Optional[str] = None
    segments: Optional[List[TranscriptionSegment]] = None
    language: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    error: Optional[str] = None


class ClipRequest(BaseModel):
    """Request to generate a clip"""
    job_id: UUID = Field(..., description="Transcription job ID")
    start_time: float = Field(..., ge=0, description="Clip start time in seconds")
    end_time: float = Field(..., gt=0, description="Clip end time in seconds")
    template: Optional[str] = Field("hormozi", description="Template style: hormozi, podcast, gaming, minimal")
    caption_style: Optional[str] = Field("default", description="Caption style")
    output_format: Optional[str] = Field("mp4", description="Output format")


class ClipResponse(BaseModel):
    """Clip generation response"""
    clip_id: UUID
    status: str  # pending, processing, completed, failed
    output_path: Optional[str] = None
    download_url: Optional[str] = None
    duration: Optional[float] = None
    file_size: Optional[int] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    error: Optional[str] = None


class ViralClipSuggestion(BaseModel):
    """AI-suggested viral clip"""
    clip_id: UUID
    start_time: float
    end_time: float
    title: str
    description: str
    viral_score: int = Field(..., ge=1, le=100)
    reason: str
    keywords: List[str]


class AnalyzeResponse(BaseModel):
    """Video analysis response with viral clip suggestions"""
    job_id: UUID
    video_info: VideoInfo
    transcript: str
    segments: List[TranscriptionSegment]
    viral_clips: List[ViralClipSuggestion]
    created_at: datetime