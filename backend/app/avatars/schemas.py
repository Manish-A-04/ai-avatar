from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict

class SystemAvatarResponse(BaseModel):
    name: str
    image_url: str

class AvatarResponse(BaseModel):
    id: UUID
    name: str
    image_url: str
    is_active: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class AvatarSelectRequest(BaseModel):
    system_avatar_name: str
