import os
from uuid import UUID
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update
from app.config import settings
from app.avatars.models import Avatar
from app.avatars.schemas import SystemAvatarResponse

class AvatarService:
    def __init__(self):
        self.system_avatars_dir = settings.media_dir / "system_avatars"
        self.system_avatars_dir.mkdir(parents=True, exist_ok=True)

    def list_system_avatars(self) -> list[SystemAvatarResponse]:
        avatars = []
        if self.system_avatars_dir.exists():
            for file in os.listdir(self.system_avatars_dir):
                if file.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                    avatars.append(SystemAvatarResponse(
                        name=file,
                        image_url=f"/media/system_avatars/{file}"
                    ))
        return avatars

    async def get_user_avatars(self, db: AsyncSession, user_id: UUID) -> list[Avatar]:
        result = await db.execute(select(Avatar).where(Avatar.user_id == user_id))
        return list(result.scalars().all())

    async def get_active_avatar(self, db: AsyncSession, user_id: UUID) -> Avatar | None:
        result = await db.execute(select(Avatar).where(Avatar.user_id == user_id, Avatar.is_active == True))
        return result.scalar_one_or_none()

    async def select_system_avatar(self, db: AsyncSession, user_id: UUID, system_avatar_name: str) -> Avatar:
        avatar_path = self.system_avatars_dir / system_avatar_name
        if not avatar_path.exists():
            raise HTTPException(status_code=404, detail="System avatar not found")
        await db.execute(
            update(Avatar).where(Avatar.user_id == user_id).values(is_active=False)
        )
        result = await db.execute(
            select(Avatar).where(Avatar.user_id == user_id, Avatar.name == system_avatar_name)
        )
        avatar = result.scalar_one_or_none()
        if avatar:
            avatar.is_active = True
        else:
            avatar = Avatar(
                user_id=user_id,
                name=system_avatar_name,
                image_path=str(avatar_path),
                is_active=True
            )
            db.add(avatar)
        await db.commit()
        await db.refresh(avatar)
        return avatar

avatar_service = AvatarService()
