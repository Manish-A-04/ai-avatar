from datetime import datetime
from uuid import UUID, uuid4
from sqlalchemy import String, Text, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base

class PipelineJob(Base):
    __tablename__ = "pipeline_jobs"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    conversation_id: Mapped[UUID] = mapped_column(ForeignKey("conversations.id"))
    turn_id: Mapped[UUID | None] = mapped_column(ForeignKey("turns.id"), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    audio_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    video_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    user_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    ai_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
