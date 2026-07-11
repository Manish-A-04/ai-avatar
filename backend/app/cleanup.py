import time
import asyncio
import logging
from app.config import settings

logger = logging.getLogger(__name__)

async def cleanup_expired_media():
    while True:
        try:
            logger.info("Running periodic media cleanup...")
            now = time.time()
            audio_dir = settings.media_dir / "audio"
            video_dir = settings.media_dir / "videos"
            if audio_dir.exists():
                for f in audio_dir.iterdir():
                    if f.is_file() and (now - f.stat().st_mtime) > settings.audio_retention_hours * 3600:
                        try:
                            f.unlink()
                            logger.info(f"Deleted expired audio file: {f.name}")
                        except Exception as e:
                            logger.error(f"Failed to delete {f.name}: {e}")
            if video_dir.exists():
                for f in video_dir.iterdir():
                    if f.is_file() and (now - f.stat().st_mtime) > settings.video_retention_hours * 3600:
                        try:
                            f.unlink()
                            logger.info(f"Deleted expired video file: {f.name}")
                        except Exception as e:
                            logger.error(f"Failed to delete {f.name}: {e}")
        except Exception as e:
            logger.error(f"Error in cleanup task: {e}")
        await asyncio.sleep(30 * 60)
