import re
import asyncio
from pathlib import Path
from uuid import uuid4
import numpy as np
import soundfile as sf
from kokoro import KPipeline
from app.config import settings

class TTSService:
    _pipeline = None

    def load(self):
        self._pipeline = KPipeline(lang_code=settings.kokoro_lang_code, device=settings.kokoro_device)

    async def synthesize(self, text: str, output_dir: Path, voice: str = settings.kokoro_voice) -> str:
        clean_text = re.sub(r'<[^>]+>', '', text)[:settings.max_tts_chars]
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"{uuid4()}.wav"
        def _run():
            chunks = []
            for _, _, audio in self._pipeline(clean_text, voice=voice):
                chunks.append(audio)
            combined = np.concatenate(chunks)
            sf.write(str(output_path), combined, 24000)
        await asyncio.to_thread(_run)
        return str(output_path)

tts_service = TTSService()
