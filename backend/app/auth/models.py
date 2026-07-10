import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, Index, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins import TimestampMixin


class UserRole(str, enum.Enum):
    STUDENT = "student"
    ADMIN = "admin"


class User(Base, TimestampMixin):
    __tablename__ = "users"
    __table_args__ = (
        Index("ix_users_role", "role"),
        Index("ix_users_is_suspended", "is_suspended"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    email: Mapped[str] = mapped_column(
        String(320),
        unique=True,
        index=True,
        nullable=False,
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    role: Mapped[UserRole] = mapped_column(
        Enum(
            UserRole,
            name="user_role",
            native_enum=False,
            create_constraint=True,
            values_callable=lambda enum_type: [
                member.value for member in enum_type
            ],
        ),
        default=UserRole.STUDENT,
        nullable=False,
    )

    is_suspended: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default="false",
        nullable=False,
    )

    suspended_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )