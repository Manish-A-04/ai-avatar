import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from app.auth.router import router as auth_router
from app.avatars.router import router as avatars_router
from app.cleanup import cleanup_expired_media
from app.config import settings
from app.conversations.router import router as conversations_router
from app.media.router import router as media_router
from app.pipeline.lipsync.service import lipsync_service
from app.pipeline.router import router as pipeline_router
from app.pipeline.stt.service import stt_service
from app.pipeline.tts.service import tts_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("═══ AI Avatar Backend Starting ═══")
    stt_service.load()
    logger.info("      ✓ STT ready")
    tts_service.load()
    logger.info("      ✓ TTS ready")
    if settings.wav2lip_enabled:
        lipsync_service.load()
        logger.info("      ✓ Wav2Lip ready")
    logger.info("═══ All models loaded. Server ready. ═══")
    cleanup_task = asyncio.create_task(cleanup_expired_media())
    yield
    logger.info("Shutting down gracefully...")
    cleanup_task.cancel()

app = FastAPI(
    title="AI Avatar API",
    description="AI avatar assistant with speech, LLM, and lip-sync",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(auth_router)
app.include_router(conversations_router)
app.include_router(avatars_router)
app.include_router(pipeline_router)
app.include_router(media_router)

class ErrorResponse(BaseModel):
    error: str
    detail: str | None = None
    status_code: int

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.detail, status_code=exc.status_code
        ).model_dump()
    )

@app.exception_handler(RequestValidationError)
async def validation_error_handler(request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content=ErrorResponse(
            error="Validation Error",
            detail=str(exc.errors()),
            status_code=422
        ).model_dump()
    )

@app.get("/health")
def health_check():
    return {"status": "ok"}
