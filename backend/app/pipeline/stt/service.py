import tempfile
import os
import asyncio
from faster_whisper import WhisperModel
from app.config import settings
from app.pipeline.schemas import TranscriptionResult

class STTService:
    _model = None

    def load(self):
        self._model = WhisperModel(
            model_size_or_path=settings.whisper_model_size,
            device=settings.whisper_device,
            compute_type=settings.whisper_compute_type,
            download_root=str(settings.models_dir / "whisper"),
            num_workers=1,
        )

    async def transcribe(self, audio_bytes: bytes) -> TranscriptionResult:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            f.write(audio_bytes)
            tmp = f.name
        try:
            segments, info = await asyncio.to_thread(
                self._model.transcribe,
                tmp,
                beam_size=5,
                language=None,
                vad_filter=True,
            )
            text = " ".join(seg.text.strip() for seg in segments)
            return TranscriptionResult(
                text=text,
                language=info.language,
                confidence=info.language_probability
            )
        finally:
            os.unlink(tmp)

stt_service = STTService()
