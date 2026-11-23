"""
ClipGod API Router
Main API router for video transcription, clip generation, and processing
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.db.session import get_db
from app.models.database import TranscriptionJob, ClipJob, JobStatus, ViralClipSuggestion
from app.models.schemas import (
    HealthResponse,
    VideoInfo,
    TranscriptionRequest,
    TranscriptionSegment,
    TranscriptionResponse,
    ClipRequest,
    ClipResponse,
    ViralClipSuggestion as ViralClipSuggestionSchema,
    AnalyzeResponse,
)
from app.services.transcription import TranscriptionService, create_transcription_job
from app.services.clipping import ClippingService, create_clip_job

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def api_health_check():
    return HealthResponse(status="healthy", service="clipgod-api")


@router.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe_video(
    request: TranscriptionRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Start a video transcription job"""
    # Create job
    job = create_transcription_job(
        db=db,
        url=str(request.url),
        language=request.language,
        model=request.model
    )
    
    # Process in background
    background_tasks.add_task(process_transcription, job.id)
    
    return TranscriptionResponse(
        job_id=job.id,
        status=job.status,
        message="Transcription job started"
    )


@router.get("/transcribe/{job_id}", response_model=TranscriptionResponse)
async def get_transcription_status(job_id: str, db: Session = Depends(get_db)):
    """Get transcription job status and results"""
    job = db.query(TranscriptionJob).filter(TranscriptionJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    segments = None
    if job.segments:
        segments = [
            TranscriptionSegment(
                start=s['start'],
                end=s['end'],
                text=s['text'],
                confidence=s.get('confidence', 0.0)
            )
            for s in job.segments
        ]
    
    return TranscriptionResponse(
        job_id=job.id,
        status=job.status,
        title=job.title,
        duration=job.duration,
        thumbnail=job.thumbnail,
        platform=job.platform,
        transcript=job.transcript,
        segments=segments,
        error=job.error,
        created_at=job.created_at,
        completed_at=job.completed_at
    )


@router.post("/clip", response_model=ClipResponse)
async def create_clip(
    request: ClipRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Create a video clip from a transcribed video"""
    # Verify transcription job exists and is completed
    trans_job = db.query(TranscriptionJob).filter(
        TranscriptionJob.id == request.transcription_job_id
    ).first()
    
    if not trans_job:
        raise HTTPException(status_code=404, detail="Transcription job not found")
    
    if trans_job.status != JobStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Transcription not completed yet")
    
    # Create clip job
    job = create_clip_job(
        db=db,
        transcription_job_id=request.transcription_job_id,
        start_time=request.start_time,
        end_time=request.end_time,
        template=request.template,
        add_captions=request.add_captions,
        caption_style=request.caption_style
    )
    
    # Process in background
    background_tasks.add_task(process_clip, job.id)
    
    return ClipResponse(
        clip_id=job.id,
        status=job.status,
        message="Clip generation started"
    )


@router.get("/clip/{clip_id}", response_model=ClipResponse)
async def get_clip_status(clip_id: str, db: Session = Depends(get_db)):
    """Get clip generation job status"""
    job = db.query(ClipJob).filter(ClipJob.id == clip_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Clip job not found")
    
    return ClipResponse(
        clip_id=job.id,
        status=job.status,
        output_path=job.output_path,
        error=job.error,
        created_at=job.created_at,
        completed_at=job.completed_at
    )


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_for_viral_clips(
    transcription_job_id: str,
    db: Session = Depends(get_db)
):
    """Analyze transcription and suggest viral clip segments"""
    job = db.query(TranscriptionJob).filter(
        TranscriptionJob.id == transcription_job_id
    ).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Transcription job not found")
    
    if job.status != JobStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Transcription not completed yet")
    
    # Simple heuristic: find segments with high engagement keywords
    suggestions = suggest_viral_clips(job.segments, job.duration)
    
    # Save suggestions
    for sug in suggestions:
        db_sug = ViralClipSuggestion(
            transcription_job_id=transcription_job_id,
            start_time=sug['start_time'],
            end_time=sug['end_time'],
            reason=sug['reason'],
            score=sug['score']
        )
        db.add(db_sug)
    db.commit()
    
    return AnalyzeResponse(
        transcription_job_id=transcription_job_id,
        suggestions=[
            ViralClipSuggestionSchema(
                start_time=s['start_time'],
                end_time=s['end_time'],
                reason=s['reason'],
                score=s['score']
            )
            for s in suggestions
        ]
    )


def process_transcription(job_id: str):
    """Background task to process transcription"""
    from app.db.session import SessionLocal
    db = SessionLocal()
    try:
        service = TranscriptionService(db)
        service.process_job(job_id)
    finally:
        db.close()


def process_clip(job_id: str):
    """Background task to process clip generation"""
    from app.db.session import SessionLocal
    db = SessionLocal()
    try:
        service = ClippingService(db)
        service.process_job(job_id)
    finally:
        db.close()


def suggest_viral_clips(segments: List[dict], duration: float) -> List[dict]:
    """Simple heuristic to suggest viral clip segments"""
    if not segments:
        return []
    
    suggestions = []
    
    # Keywords that often indicate engaging content
    viral_keywords = [
        'secret', 'trick', 'hack', 'tip', 'mistake', 'wrong', 'never',
        'always', 'best', 'worst', 'shocking', 'amazing', 'incredible',
        'unbelievable', 'must', 'need', 'stop', 'wait', 'watch',
        'learn', 'discover', 'reveal', 'expose', 'truth', 'lie'
    ]
    
    for i, seg in enumerate(segments):
        text = seg['text'].lower()
        score = 0
        reasons = []
        
        # Check for viral keywords
        for kw in viral_keywords:
            if kw in text:
                score += 10
                reasons.append(f"Contains '{kw}'")
        
        # Prefer segments 15-60 seconds long
        seg_duration = seg['end'] - seg['start']
        if 15 <= seg_duration <= 60:
            score += 20
            reasons.append("Optimal duration (15-60s)")
        elif 10 <= seg_duration < 15:
            score += 10
            reasons.append("Good duration (10-15s)")
        
        # Prefer segments in first half (hook)
        if seg['start'] < duration * 0.5:
            score += 15
            reasons.append("Early in video (hook)")
        
        # Check for questions or exclamations
        if '?' in seg['text'] or '!' in seg['text']:
            score += 10
            reasons.append("Question or exclamation")
        
        if score > 20:
            suggestions.append({
                'start_time': seg['start'],
                'end_time': min(seg['end'], seg['start'] + 60),  # Cap at 60s
                'reason': '; '.join(reasons),
                'score': score
            })
    
    # Sort by score and return top 5
    suggestions.sort(key=lambda x: x['score'], reverse=True)
    return suggestions[:5]