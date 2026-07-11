import uuid
from typing import Any

from sqlalchemy.orm import Session

from app.events.models import OutboxEvent


CHAT_MESSAGE_QUEUED = "chat.message.queued"


def add_outbox_event(
    db: Session,
    *,
    event_type: str,
    aggregate_type: str,
    aggregate_id: uuid.UUID | str,
    payload: dict[str, Any],
) -> OutboxEvent:
    event = OutboxEvent(
        event_type=event_type,
        aggregate_type=aggregate_type,
        aggregate_id=str(aggregate_id),
        payload=payload,
    )

    db.add(event)
    return event
