from uuid import UUID
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from sqlalchemy.orm import selectinload
from app.conversations.models import Conversation, Turn
from app.conversations.schemas import ConversationCreate, ConversationUpdate

class ConversationService:
    async def create(self, db: AsyncSession, user_id: UUID, data: ConversationCreate) -> Conversation:
        conv = Conversation(
            user_id=user_id,
            title=data.title,
            system_prompt=data.system_prompt
        )
        db.add(conv)
        await db.commit()
        await db.refresh(conv)
        return conv

    async def get_by_id(self, db: AsyncSession, conv_id: UUID, user_id: UUID = None) -> Conversation:
        stmt = select(Conversation).where(Conversation.id == conv_id).options(selectinload(Conversation.turns))
        result = await db.execute(stmt)
        conv = result.scalar_one_or_none()
        if not conv:
            raise HTTPException(status_code=404, detail="Conversation not found")
        if user_id and conv.user_id != user_id:
            raise HTTPException(status_code=403, detail="Not authorized to access this conversation")
        return conv

    async def list_for_user(self, db: AsyncSession, user_id: UUID, page: int = 1, page_size: int = 20) -> tuple[list[Conversation], int]:
        count_stmt = select(func.count(Conversation.id)).where(Conversation.user_id == user_id)
        total_result = await db.execute(count_stmt)
        total = total_result.scalar_one()
        stmt = select(Conversation).where(Conversation.user_id == user_id).order_by(Conversation.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
        result = await db.execute(stmt)
        conversations = list(result.scalars().all())
        return conversations, total

    async def update(self, db: AsyncSession, conv_id: UUID, user_id: UUID, data: ConversationUpdate) -> Conversation:
        conv = await self.get_by_id(db, conv_id, user_id)
        if data.title is not None:
            conv.title = data.title
        if data.system_prompt is not None:
            conv.system_prompt = data.system_prompt
        await db.commit()
        await db.refresh(conv)
        return conv

    async def delete(self, db: AsyncSession, conv_id: UUID, user_id: UUID):
        conv = await self.get_by_id(db, conv_id, user_id)
        await db.delete(conv)
        await db.commit()

    async def add_turn(
        self, 
        db: AsyncSession, 
        conv_id: UUID, 
        role: str, 
        text: str, 
        input_mode: str,
        audio_path: str | None = None,
        video_path: str | None = None
    ) -> Turn:
        turn = Turn(
            conversation_id=conv_id,
            role=role,
            text_content=text,
            input_mode=input_mode,
            audio_path=audio_path,
            video_path=video_path
        )
        db.add(turn)
        await db.commit()
        await db.refresh(turn)
        return turn

    async def get_gemini_history(self, db: AsyncSession, conv_id: UUID, limit: int = 20) -> list[dict]:
        conv = await self.get_by_id(db, conv_id)
        turns = conv.turns[-limit:] if len(conv.turns) > limit else conv.turns
        history = []
        for turn in turns:
            history.append({
                "role": "user" if turn.role == "user" else "model",
                "parts": [{"text": turn.text_content}]
            })
        return history

conversation_service = ConversationService()
