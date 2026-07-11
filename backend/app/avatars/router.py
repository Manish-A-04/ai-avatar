from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database import get_db
from app.auth.dependencies import get_current_user
from app.auth.models import User
from app.avatars.schemas import SystemAvatarResponse, AvatarResponse, AvatarSelectRequest
from app.avatars.service import avatar_service

router = APIRouter(prefix="/avatars", tags=["avatars"])

@router.get("/system", response_model=List[SystemAvatarResponse])
async def list_system_avatars(current_user: User = Depends(get_current_user)):
    return avatar_service.list_system_avatars()

@router.get("/me", response_model=List[AvatarResponse])
async def get_my_avatars(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    avatars = await avatar_service.get_user_avatars(db, current_user.id)
    result = []
    for av in avatars:
        result.append(AvatarResponse(
            id=av.id,
            name=av.name,
            image_url=f"/media/system_avatars/{av.name}",
            is_active=av.is_active,
            created_at=av.created_at
        ))
    return result

@router.post("/select", response_model=AvatarResponse)
async def select_avatar(
    data: AvatarSelectRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    avatar = await avatar_service.select_system_avatar(db, current_user.id, data.system_avatar_name)
    return AvatarResponse(
        id=avatar.id,
        name=avatar.name,
        image_url=f"/media/system_avatars/{avatar.name}",
        is_active=avatar.is_active,
        created_at=avatar.created_at
    )
