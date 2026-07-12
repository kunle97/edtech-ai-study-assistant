from datetime import datetime, timezone

from sqlalchemy import select

from app.db.session import SessionLocal
from app.events.models import OutboxEvent
from app.events.service import (
    CHAT_INTERACTION_COMPLETED,
    CHAT_MESSAGE_QUEUED,
)
from app.worker.celery_app import celery_app


OUTBOX_BATCH_SIZE = 100


@celery_app.task(
    name="events.publish_outbox",
    ignore_result=True,
)
def publish_outbox_events() -> dict[str, int]:
    published = 0
    failed = 0

    with SessionLocal() as db:
        events = list(
            db.scalars(
                select(OutboxEvent)
                .where(OutboxEvent.published_at.is_(None))
                .order_by(OutboxEvent.created_at.asc())
                .limit(OUTBOX_BATCH_SIZE)
                .with_for_update(skip_locked=True)
            ).all()
        )

        for event in events:
            event.publish_attempts += 1

            try:
                if event.event_type == CHAT_MESSAGE_QUEUED:
                    celery_app.send_task(
                        "chat.process_message",
                        args=[event.payload["message_id"]],
                    )

                elif event.event_type == CHAT_INTERACTION_COMPLETED:
                    interaction_id = event.payload["interaction_id"]

                    celery_app.send_task(
                        "analytics.consume_chat_interaction",
                        args=[interaction_id, event.payload],
                        queue="analytics",
                    )

                    celery_app.send_task(
                        "compliance.consume_chat_interaction",
                        args=[interaction_id, event.payload],
                        queue="compliance",
                    )

                else:
                    raise ValueError(
                        f"Unsupported outbox event: {event.event_type}"
                    )

                event.published_at = datetime.now(timezone.utc)
                event.last_error = None
                published += 1

            except Exception as exc:
                event.last_error = str(exc)[:2000]
                failed += 1

        db.commit()

    return {
        "published": published,
        "failed": failed,
    }
