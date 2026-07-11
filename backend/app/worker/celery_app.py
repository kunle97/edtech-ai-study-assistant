from celery import Celery

from app.core.config import settings


celery_app = Celery(
    "learnpath",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=[
        "app.worker.tasks",
        "app.events.tasks",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    worker_prefetch_multiplier=1,
    broker_connection_retry_on_startup=True,
    beat_schedule={
        "publish-pending-outbox-events": {
            "task": "events.publish_outbox",
            "schedule": 2.0,
        },
    },
)
