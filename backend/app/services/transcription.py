"""
Transcription Service
Handles video download, audio extraction, and speech-to-text using Whisper
"""

import os
import uuid
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime

import yt_dlp
import whisper
from sqlalchemy.orm import Session

from app.models.database import TranscriptionJob, JobStatus
from app.core.config import settings


class TranscriptionService:
    """Service for handling video transcription pipeline"""
    
    def __init__(self, db: Session):
        self.db = db
        self.whisper_model = None
    
    def _get_whisper_model(self, model_name: str = "base"):
        """Lazy load Whisper model"""
        if self.whisper_model is None or self.whisper_model_name != model_name:
            self.whisper_model = whisper.load_model(model_name)
            self.whisper_model_name = model_name
        return self.whisper_model
    
    def download_video(self, url: str, job_id: str) -> tuple[str, str, dict]:
        """
        Download video using yt-dlp
        Returns: (video_path, audio_path, video_info)
        """
        job_dir = Path(settings.UPLOAD_DIR) / job_id
        job_dir.mkdir(parents=True, exist_ok=True)
        
        video_path = job_dir / "video.mp4"
        audio_path = job_dir / "audio.wav"
        
        # yt-dlp options
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'outtmpl': str(video_path),
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
        
        # Extract audio using ffmpeg
        self._extract_audio(str(video_path), str(audio_path))
        
        video_info = {
            'title': info.get('title', 'Unknown'),
            'duration': info.get('duration', 0),
            'thumbnail': info.get('thumbnail', ''),
            'platform': info.get('extractor_key', '').replace('IE', '').lower(),
        }
        
        return str(video_path), str(audio_path), video_info
    
    def _extract_audio(self, video_path: str, audio_path: str) -> None:
        """Extract audio from video using ffmpeg"""
        cmd = [
            'ffmpeg', '-y', '-i', video_path,
            '-vn', '-acodec', 'pcm_s16le', '-ar', '16000', '-ac', '1',
            audio_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"Audio extraction failed: {result.stderr}")
    
    def transcribe_audio(self, audio_path: str, language: str = "auto", model: str = "base") -> Dict[str, Any]:
        """Transcribe audio using Whisper"""
        model = self._get_whisper_model(model)
        
        # Whisper language code mapping
        lang = None if language == "auto" else language
        
        result = model.transcribe(
            audio_path,
            language=lang,
            word_timestamps=True,
            verbose=False
        )
        
        # Format segments
        segments = []
        for seg in result.get('segments', []):
            segments.append({
                'start': seg['start'],
                'end': seg['end'],
                'text': seg['text'].strip(),
                'confidence': seg.get('avg_logprob', 0.0)
            })
        
        return {
            'text': result['text'].strip(),
            'segments': segments,
            'language': result.get('language', 'unknown')
        }
    
    def process_job(self, job_id: str) -> None:
        """Process a transcription job (called by background worker)"""
        job = self.db.query(TranscriptionJob).filter(TranscriptionJob.id == job_id).first()
        if not job:
            raise ValueError(f"Job {job_id} not found")
        
        try:
            # Update status to processing
            job.status = JobStatus.PROCESSING
            job.started_at = datetime.utcnow()
            self.db.commit()
            
            # Download video and extract audio
            video_path, audio_path, video_info = self.download_video(job.url, job_id)
            
            job.video_path = video_path
            job.audio_path = audio_path
            job.title = video_info['title']
            job.duration = video_info['duration']
            job.thumbnail = video_info['thumbnail']
            job.platform = video_info['platform']
            self.db.commit()
            
            # Transcribe
            result = self.transcribe_audio(audio_path, job.language, job.model)
            
            job.transcript = result['text']
            job.segments = result['segments']
            job.status = JobStatus.COMPLETED
            job.completed_at = datetime.utcnow()
            self.db.commit()
            
        except Exception as e:
            job.status = JobStatus.FAILED
            job.error = str(e)
            job.completed_at = datetime.utcnow()
            self.db.commit()
            raise


def create_transcription_job(
    db: Session,
    url: str,
    language: str = "auto",
    model: str = "base"
) -> TranscriptionJob:
    """Create a new transcription job"""
    job = TranscriptionJob(
        url=url,
        language=language,
        model=model,
        status=JobStatus.PENDING
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job