import os
from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.auth.dependencies import get_current_user
from app.auth.models import User
from app.conversations.schemas import (
    ConversationCreate, 
    ConversationUpdate, 
    ConversationResponse, 
    ConversationDetailResponse, 
    ConversationListResponse,
    TurnResponse
)
from app.conversations.service import conversation_service

router = APIRouter(prefix="/conversations", tags=["conversations"])

def _build_media_url(path: str | None, media_type: str) -> str | None:
    if not path:
        return None
    filename = os.path.basename(path)
    return f"/media/{media_type}/{filename}"

@router.post("", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    data: ConversationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    conv = await conversation_service.create(db, current_user.id, data)
    return conv

@router.get("", response_model=ConversationListResponse)
async def list_conversations(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    conversations, total = await conversation_service.list_for_user(db, current_user.id, page, page_size)
    return ConversationListResponse(
        conversations=conversations,
        total=total,
        page=page,
        page_size=page_size
    )

@router.get("/{conv_id}", response_model=ConversationDetailResponse)
async def get_conversation(
    conv_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    conv = await conversation_service.get_by_id(db, conv_id, current_user.id)
    turns_resp = []
    for turn in conv.turns:
        t_dict = {
            "id": turn.id,
            "role": turn.role,
            "text_content": turn.text_content,
            "input_mode": turn.input_mode,
            "created_at": turn.created_at,
            "audio_url": _build_media_url(turn.audio_path, "audio"),
            "video_url": _build_media_url(turn.video_path, "video")
        }
        turns_resp.append(TurnResponse.model_validate(t_dict))
    return ConversationDetailResponse(
        id=conv.id,
        title=conv.title,
        system_prompt=conv.system_prompt,
        created_at=conv.created_at,
        updated_at=conv.updated_at,
        turns=turns_resp
    )

@router.patch("/{conv_id}", response_model=ConversationResponse)
async def update_conversation(
    conv_id: UUID,
    data: ConversationUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    conv = await conversation_service.update(db, conv_id, current_user.id, data)
    return conv

@router.delete("/{conv_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    conv_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    await conversation_service.delete(db, conv_id, current_user.id)
