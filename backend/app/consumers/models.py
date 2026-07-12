import uuid
from typing import Any

from sqlalchemy import JSON, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins import TimestampMixin


class AnalyticsEvent(Base, TimestampMixin):
    __tablename__ = "analytics_events"
    __table_args__ = (
        UniqueConstraint(
            "interaction_id",
            name="uq_analytics_events_interaction_id",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    interaction_id: Mapped[str] = mapped_column(String(100), nullable=False)
    payload: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)


class ComplianceEvent(Base, TimestampMixin):
    __tablename__ = "compliance_events"
    __table_args__ = (
        UniqueConstraint(
            "interaction_id",
            name="uq_compliance_events_interaction_id",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    interaction_id: Mapped[str] = mapped_column(String(100), nullable=False)
    payload: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)