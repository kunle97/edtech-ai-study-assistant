import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins import TimestampMixin


class OutboxEvent(Base, TimestampMixin):
    __tablename__ = "outbox_events"
    __table_args__ = (
        Index(
            "ix_outbox_events_unpublished",
            "published_at",
            "created_at",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    event_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    aggregate_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    aggregate_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    payload: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
    )

    published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    publish_attempts: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )

    last_error: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
