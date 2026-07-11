from uuid import UUID
from pydantic import BaseModel, Field

class ProcessVoiceRequest(BaseModel):
    conversation_id: UUID
    generate_lipsync: bool = True

class ProcessTextRequest(BaseModel):
    conversation_id: UUID
    text: str = Field(min_length=1, max_length=4000)
    generate_lipsync: bool = True

class JobSubmitResponse(BaseModel):
    job_id: UUID
    status: str = "pending"
    message: str = "Processing started. Poll /pipeline/status/{job_id} for updates."

class JobStatusResponse(BaseModel):
    job_id: UUID
    status: str
    user_text: str | None
    ai_text: str | None
    audio_url: str | None
    video_url: str | None
    error: str | None
    processing_time_ms: int | None

class TranscriptionResult(BaseModel):
    text: str
    language: str
    confidence: float | None
