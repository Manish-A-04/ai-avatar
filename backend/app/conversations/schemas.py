from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict

class ConversationCreate(BaseModel):
    title: str | None = Field(None, max_length=200)
    system_prompt: str | None = Field(None, max_length=2000)

class ConversationUpdate(BaseModel):
    title: str | None = Field(None, max_length=200)
    system_prompt: str | None = Field(None, max_length=2000)

class TurnResponse(BaseModel):
    id: UUID
    role: str
    text_content: str
    audio_url: str | None
    video_url: str | None
    input_mode: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class ConversationResponse(BaseModel):
    id: UUID
    title: str | None
    system_prompt: str | None
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class ConversationDetailResponse(ConversationResponse):
    turns: list[TurnResponse]

class ConversationListResponse(BaseModel):
    conversations: list[ConversationResponse]
    total: int
    page: int
    page_size: int
