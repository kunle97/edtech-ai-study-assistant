import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.chat.models import MessageRole, MessageStatus


class ChatSessionCreate(BaseModel):
    title: str | None = Field(
        default=None,
        max_length=200,
    )


class ChatMessageCreate(BaseModel):
    content: str = Field(
        min_length=1,
        max_length=10_000,
    )


class ChatMessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    session_id: uuid.UUID
    role: MessageRole
    status: MessageStatus
    content: str
    error_message: str | None
    created_at: datetime


class ChatSessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str | None
    created_at: datetime
    updated_at: datetime


class ChatSessionDetail(ChatSessionResponse):
    messages: list[ChatMessageResponse]
