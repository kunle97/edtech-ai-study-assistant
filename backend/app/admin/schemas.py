import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr

from app.auth.models import UserRole


class AdminUserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: EmailStr
    role: UserRole
    is_suspended: bool
    suspended_at: datetime | None
    created_at: datetime


class UserListResponse(BaseModel):
    users: list[AdminUserResponse]
    total: int


class AdminChatSessionResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    user_email: EmailStr
    title: str | None
    start_time: datetime
    message_count: int
