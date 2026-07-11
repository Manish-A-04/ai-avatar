import time
import os
import asyncio
import logging
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import AsyncSessionLocal
from app.auth.models import User
from app.conversations.service import conversation_service
from app.avatars.service import avatar_service
from app.pipeline.models import PipelineJob
from app.pipeline.stt.service import stt_service
from app.pipeline.llm.service import llm_service
from app.pipeline.tts.service import tts_service
from app.pipeline.lipsync.service import lipsync_service
from app.config import settings

logger = logging.getLogger(__name__)

class PipelineError(Exception):
    pass

class PipelineOrchestrator:
    async def submit_voice(self, audio_bytes: bytes, conversation_id: UUID, user: User, generate_lipsync: bool, db: AsyncSession) -> PipelineJob:
        job = PipelineJob(
            user_id=user.id,
            conversation_id=conversation_id,
            status="pending"
        )
        db.add(job)
        await db.commit()
        await db.refresh(job)
        asyncio.create_task(self._run_voice_pipeline(job.id, audio_bytes, conversation_id, user, generate_lipsync))
        return job

    async def submit_text(self, text: str, conversation_id: UUID, user: User, generate_lipsync: bool, db: AsyncSession) -> PipelineJob:
        job = PipelineJob(
            user_id=user.id,
            conversation_id=conversation_id,
            status="pending"
        )
        db.add(job)
        await db.commit()
        await db.refresh(job)
        asyncio.create_task(self._run_text_pipeline(job.id, text, conversation_id, user, generate_lipsync))
        return job

    async def _run_voice_pipeline(self, job_id: UUID, audio_bytes: bytes, conversation_id: UUID, user: User, generate_lipsync: bool):
        async with AsyncSessionLocal() as db:
            job = await db.get(PipelineJob, job_id)
            job.status = "processing"
            await db.commit()
            try:
                start = time.perf_counter()
                transcription = await stt_service.transcribe(audio_bytes)
                if not transcription.text.strip():
                    raise PipelineError("No speech detected in audio")
                await self._process_text_core(job, db, transcription.text, "audio", conversation_id, user, generate_lipsync, start)
            except Exception as e:
                logger.error(f"Pipeline job {job_id} failed: {e}")
                job.status = "failed"
                job.error_message = str(e)
                await db.commit()

    async def _run_text_pipeline(self, job_id: UUID, text: str, conversation_id: UUID, user: User, generate_lipsync: bool):
        async with AsyncSessionLocal() as db:
            job = await db.get(PipelineJob, job_id)
            job.status = "processing"
            await db.commit()
            try:
                start = time.perf_counter()
                await self._process_text_core(job, db, text, "text", conversation_id, user, generate_lipsync, start)
            except Exception as e:
                logger.error(f"Pipeline job {job_id} failed: {e}")
                job.status = "failed"
                job.error_message = str(e)
                await db.commit()

    async def _process_text_core(self, job: PipelineJob, db: AsyncSession, user_text: str, input_mode: str, conversation_id: UUID, user: User, generate_lipsync: bool, start_time: float):
        user_turn = await conversation_service.add_turn(
            db, conversation_id, role="user", text=user_text, input_mode=input_mode
        )
        history = await conversation_service.get_gemini_history(db, conversation_id, limit=settings.max_history_turns)
        conv = await conversation_service.get_by_id(db, conversation_id)
        ai_text = await llm_service.generate(
            user_message=user_text,
            history=history,
            system_prompt=conv.system_prompt
        )
        audio_path = await tts_service.synthesize(
            text=ai_text,
            output_dir=settings.media_dir / "audio"
        )
        video_path = None
        if generate_lipsync and settings.wav2lip_enabled:
            avatar = await avatar_service.get_active_avatar(db, user.id)
            if avatar:
                video_path = await lipsync_service.animate(
                    image_path=avatar.image_path,
                    audio_path=audio_path,
                    output_dir=settings.media_dir / "videos"
                )
        ai_turn = await conversation_service.add_turn(
            db, conversation_id, role="model", text=ai_text, input_mode="audio"
        )
        elapsed_ms = int((time.perf_counter() - start_time) * 1000)
        job.status = "done"
        job.turn_id = ai_turn.id
        job.user_text = user_text
        job.ai_text = ai_text
        def _build_url(path, media_type):
            if not path: return None
            return f"/media/{media_type}/{os.path.basename(path)}"
        job.audio_url = _build_url(audio_path, "audio")
        job.video_url = _build_url(video_path, "videos")
        job.processing_time_ms = elapsed_ms
        await db.commit()

pipeline_orchestrator = PipelineOrchestrator()
