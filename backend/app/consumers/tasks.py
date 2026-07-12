from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.consumers.models import AnalyticsEvent, ComplianceEvent
from app.db.session import SessionLocal
from app.worker.celery_app import celery_app


@celery_app.task(
    name="analytics.consume_chat_interaction",
    queue="analytics",
    ignore_result=True,
)
def consume_analytics_event(
    interaction_id: str,
    payload: dict,
) -> dict[str, str]:
    with SessionLocal() as db:
        existing = db.scalar(
            select(AnalyticsEvent).where(
                AnalyticsEvent.interaction_id == interaction_id
            )
        )

        if existing is not None:
            return {"status": "duplicate"}

        db.add(
            AnalyticsEvent(
                interaction_id=interaction_id,
                payload=payload,
            )
        )

        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            return {"status": "duplicate"}

    return {"status": "consumed"}


@celery_app.task(
    name="compliance.consume_chat_interaction",
    queue="compliance",
    ignore_result=True,
)
def consume_compliance_event(
    interaction_id: str,
    payload: dict,
) -> dict[str, str]:
    with SessionLocal() as db:
        existing = db.scalar(
            select(ComplianceEvent).where(
                ComplianceEvent.interaction_id == interaction_id
            )
        )

        if existing is not None:
            return {"status": "duplicate"}

        db.add(
            ComplianceEvent(
                interaction_id=interaction_id,
                payload=payload,
            )
        )

        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            return {"status": "duplicate"}

    return {"status": "consumed"}
