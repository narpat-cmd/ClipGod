"""
Clipping Service
Handles video clip generation using ffmpeg
"""

import os
import uuid
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

from sqlalchemy.orm import Session

from app.models.database import ClipJob, TranscriptionJob, JobStatus
from app.core.config import settings


class ClippingService:
    """Service for generating video clips"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def generate_clip(
        self,
        job_id: str,
        transcription_job_id: str,
        start_time: float,
        end_time: float,
        template: str = "vertical",
        add_captions: bool = True,
        caption_style: str = "default"
    ) -> str:
        """
        Generate a video clip from the source video
        Returns: output clip path
        """
        # Get transcription job for video path
        trans_job = self.db.query(TranscriptionJob).filter(
            TranscriptionJob.id == transcription_job_id
        ).first()
        
        if not trans_job or not trans_job.video_path:
            raise ValueError("Source video not found")
        
        if not os.path.exists(trans_job.video_path):
            raise ValueError("Source video file missing")
        
        # Create output directory
        clip_dir = Path(settings.CLIPS_DIR) / job_id
        clip_dir.mkdir(parents=True, exist_ok=True)
        
        output_path = clip_dir / f"clip_{job_id}.mp4"
        
        # Build ffmpeg command based on template
        cmd = self._build_ffmpeg_command(
            input_path=trans_job.video_path,
            output_path=str(output_path),
            start_time=start_time,
            end_time=end_time,
            template=template,
            add_captions=add_captions,
            caption_style=caption_style,
            segments=trans_job.segments
        )
        
        # Run ffmpeg
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"Clip generation failed: {result.stderr}")
        
        return str(output_path)
    
    def _build_ffmpeg_command(
        self,
        input_path: str,
        output_path: str,
        start_time: float,
        end_time: float,
        template: str,
        add_captions: bool,
        caption_style: str,
        segments: List[Dict[str, Any]]
    ) -> List[str]:
        """Build ffmpeg command for clip generation"""
        
        duration = end_time - start_time
        
        # Base command
        cmd = [
            'ffmpeg', '-y',
            '-ss', str(start_time),
            '-t', str(duration),
            '-i', input_path,
        ]
        
        # Template-specific filters
        if template == "vertical":
            # 9:16 aspect ratio for TikTok/Reels/Shorts
            cmd.extend([
                '-vf', (
                    "scale=1080:1920:force_original_aspect_ratio=decrease,"
                    "pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=black"
                )
            ])
        elif template == "square":
            # 1:1 aspect ratio
            cmd.extend([
                '-vf', (
                    "scale=1080:1080:force_original_aspect_ratio=decrease,"
                    "pad=1080:1080:(ow-iw)/2:(oh-ih)/2:color=black"
                )
            ])
        elif template == "landscape":
            # 16:9 aspect ratio
            cmd.extend([
                '-vf', (
                    "scale=1920:1080:force_original_aspect_ratio=decrease,"
                    "pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=black"
                )
            ])
        
        # Add captions if requested
        if add_captions and segments:
            # Filter segments that fall within our clip time range
            clip_segments = [
                s for s in segments
                if s['end'] > start_time and s['start'] < end_time
            ]
            
            if clip_segments:
                # Create subtitle file
                srt_path = self._create_srt_file(clip_segments, start_time, output_path.replace('.mp4', '.srt'))
                cmd.extend(['-vf', f"subtitles={srt_path}:force_style='FontSize=24,PrimaryColour=&HFFFFFF,OutlineColour=&H000000,Outline=2'"])
        
        # Output settings
        cmd.extend([
            '-c:v', 'libx264',
            '-preset', 'medium',
            '-crf', '23',
            '-c:a', 'aac',
            '-b:a', '128k',
            '-movflags', '+faststart',
            output_path
        ])
        
        return cmd
    
    def _create_srt_file(
        self,
        segments: List[Dict[str, Any]],
        clip_start: float,
        srt_path: str
    ) -> str:
        """Create SRT subtitle file for the clip"""
        with open(srt_path, 'w', encoding='utf-8') as f:
            for i, seg in enumerate(segments, 1):
                # Adjust times relative to clip start
                start = max(0, seg['start'] - clip_start)
                end = max(0, seg['end'] - clip_start)
                
                f.write(f"{i}\n")
                f.write(f"{self._format_time(start)} --> {self._format_time(end)}\n")
                f.write(f"{seg['text']}\n\n")
        return srt_path
    
    def _format_time(self, seconds: float) -> str:
        """Format seconds as SRT time (HH:MM:SS,mmm)"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds - int(seconds)) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
    
    def process_job(self, job_id: str) -> None:
        """Process a clip generation job"""
        job = self.db.query(ClipJob).filter(ClipJob.id == job_id).first()
        if not job:
            raise ValueError(f"Clip job {job_id} not found")
        
        try:
            job.status = JobStatus.PROCESSING
            job.started_at = datetime.utcnow()
            self.db.commit()
            
            output_path = self.generate_clip(
                job_id=job.id,
                transcription_job_id=job.transcription_job_id,
                start_time=job.start_time,
                end_time=job.end_time,
                template=job.template,
                add_captions=job.add_captions,
                caption_style=job.caption_style
            )
            
            job.output_path = output_path
            job.status = JobStatus.COMPLETED
            job.completed_at = datetime.utcnow()
            self.db.commit()
            
        except Exception as e:
            job.status = JobStatus.FAILED
            job.error = str(e)
            job.completed_at = datetime.utcnow()
            self.db.commit()
            raise


def create_clip_job(
    db: Session,
    transcription_job_id: str,
    start_time: float,
    end_time: float,
    template: str = "vertical",
    add_captions: bool = True,
    caption_style: str = "default"
) -> ClipJob:
    """Create a new clip generation job"""
    job = ClipJob(
        transcription_job_id=transcription_job_id,
        start_time=start_time,
        end_time=end_time,
        template=template,
        add_captions=add_captions,
        caption_style=caption_style,
        status=JobStatus.PENDING
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job