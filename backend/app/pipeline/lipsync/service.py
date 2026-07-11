import sys
import logging
import asyncio
import subprocess
import os
import tempfile
import cv2
import numpy as np
import torch
from pathlib import Path
from uuid import uuid4
from app.config import settings

sys.path.insert(0, str(settings.wav2lip_dir))
try:
    from models.wav2lip import Wav2Lip
    import face_detection
except ImportError:
    Wav2Lip = None
    face_detection = None

logger = logging.getLogger(__name__)

class LipSyncService:
    _model = None

    def load(self):
        wav2lip_dir = settings.wav2lip_dir
        if not wav2lip_dir.exists():
            logger.warning(f"Wav2Lip directory not found at {wav2lip_dir}. Wav2Lip disabled.")
            return
        if Wav2Lip is None or face_detection is None:
            logger.warning("Wav2Lip models or face_detection not available.")
            return
        try:
            checkpoint_path = wav2lip_dir / "checkpoints" / settings.wav2lip_checkpoint
            if not checkpoint_path.exists():
                logger.warning(f"Wav2Lip checkpoint not found at {checkpoint_path}")
                return
            checkpoint = torch.load(str(checkpoint_path), map_location="cuda")
            if isinstance(checkpoint, dict):
                state_dict = checkpoint.get("state_dict", checkpoint)
            elif hasattr(checkpoint, "state_dict"):
                state_dict = checkpoint.state_dict()
            else:
                state_dict = checkpoint
            self._model = Wav2Lip()
            self._model.load_state_dict(state_dict)
            self._model = self._model.half().cuda().eval()
            logger.info("Wav2Lip model loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load Wav2Lip: {e}")

    def _run_inference(self, image_path: str, audio_path: str, output_path: str):
        if not self._model:
            raise ValueError("Wav2Lip model is not loaded.")
        frame = cv2.imread(image_path)
        if frame is None:
            raise ValueError(f"Cannot read image: {image_path}")
        h, w = frame.shape[:2]
        scale = min(480 / h, 480 / w, 1.0)
        resized_path = image_path
        tmp_file = None
        if scale < 1.0:
            frame = cv2.resize(frame, (int(w * scale), int(h * scale)))
            tmp_file = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
            cv2.imwrite(tmp_file.name, frame)
            resized_path = tmp_file.name
        inference_script = settings.wav2lip_dir / "inference.py"
        checkpoint_path = settings.wav2lip_dir / "checkpoints" / settings.wav2lip_checkpoint
        cmd = [
            sys.executable, str(inference_script),
            "--checkpoint_path", str(checkpoint_path),
            "--face", resized_path,
            "--audio", audio_path,
            "--outfile", output_path,
            "--static", "True",
            "--wav2lip_batch_size", str(settings.wav2lip_batch_size)
        ]
        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as e:
            logger.error(f"Wav2Lip error: {e.stderr}")
            if "out of memory" in e.stderr.lower():
                torch.cuda.empty_cache()
                raise MemoryError("Wav2Lip OOM")
            raise ValueError("Wav2Lip inference failed")
        finally:
            if tmp_file:
                try:
                    os.unlink(tmp_file.name)
                except Exception:
                    pass

    async def animate(self, image_path: str, audio_path: str, output_dir: Path) -> str | None:
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = str(output_dir / f"{uuid4()}.mp4")
        try:
            await asyncio.to_thread(self._run_inference, image_path, audio_path, output_path)
            return output_path
        except MemoryError:
            logger.error("Wav2Lip OOM — returning None (audio still available)")
            return None
        except Exception as e:
            logger.warning(f"Wav2Lip skipped: {e}")
            return None

lipsync_service = LipSyncService()
