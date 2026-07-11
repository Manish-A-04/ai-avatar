from uuid import UUID
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.auth.dependencies import get_current_user
from app.auth.models import User
from app.pipeline.schemas import ProcessVoiceRequest, ProcessTextRequest, JobSubmitResponse, JobStatusResponse
from app.pipeline.service import pipeline_orchestrator
from app.pipeline.models import PipelineJob
from app.config import settings

router = APIRouter(prefix="/pipeline", tags=["pipeline"])

@router.post("/voice", response_model=JobSubmitResponse, status_code=status.HTTP_202_ACCEPTED)
async def process_voice(
    audio_file: UploadFile = File(...),
    conversation_id: UUID = Form(...),
    generate_lipsync: bool = Form(True),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if audio_file.size > settings.max_audio_size_mb * 1024 * 1024:
        raise HTTPException(status_code=413, detail=f"Audio file too large. Max {settings.max_audio_size_mb}MB")
        
    audio_bytes = await audio_file.read()
    job = await pipeline_orchestrator.submit_voice(audio_bytes, conversation_id, current_user, generate_lipsync, db)
    
    return JobSubmitResponse(
        job_id=job.id,
        status=job.status
    )

@router.post("/text", response_model=JobSubmitResponse, status_code=status.HTTP_202_ACCEPTED)
async def process_text(
    data: ProcessTextRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    job = await pipeline_orchestrator.submit_text(data.text, data.conversation_id, current_user, data.generate_lipsync, db)
    return JobSubmitResponse(
        job_id=job.id,
        status=job.status
    )

@router.get("/status/{job_id}", response_model=JobStatusResponse)
async def get_job_status(
    job_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    job = await db.get(PipelineJob, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    processing_time = None
    if job.updated_at and job.created_at:
        processing_time = int((job.updated_at - job.created_at).total_seconds() * 1000)

    return JobStatusResponse(
        job_id=job.id,
        status=job.status,
        user_text=job.user_text,
        ai_text=job.ai_text,
        audio_url=job.audio_url,
        video_url=job.video_url,
        error=job.error_message,
        processing_time_ms=processing_time
    )
