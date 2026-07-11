import os
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse

from app.config import settings
from app.auth.dependencies import get_current_user
from app.auth.models import User

router = APIRouter(prefix="/media", tags=["media"])

@router.get("/audio/{filename}")
async def get_audio(filename: str):
    file_path = settings.media_dir / "audio" / filename
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="Audio file not found")
    return FileResponse(path=file_path, media_type="audio/wav")

@router.get("/videos/{filename}")
async def get_video(filename: str):
    file_path = settings.media_dir / "videos" / filename
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="Video file not found")
    return FileResponse(path=file_path, media_type="video/mp4")

@router.get("/system_avatars/{filename}")
async def get_system_avatar(filename: str):
    file_path = settings.media_dir / "system_avatars" / filename
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="Avatar image not found")
    
    ext = os.path.splitext(filename)[1].lower()
    media_type = "image/jpeg"
    if ext == ".png":
        media_type = "image/png"
    elif ext == ".webp":
        media_type = "image/webp"
        
    return FileResponse(path=file_path, media_type=media_type)
