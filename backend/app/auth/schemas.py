from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field, ConfigDict

class UserRegisterRequest(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=50, pattern=r'^[a-zA-Z0-9_]+$')
    password: str = Field(min_length=8, max_length=72)

class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(max_length=72)

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class TokenRefreshRequest(BaseModel):
    refresh_token: str

class UserMeResponse(BaseModel):
    id: UUID
    email: str
    username: str
    is_active: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
