from celery import Celery

from app.core.config import settings


celery_app = Celery(
    "learnpath",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["app.worker.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,

    # A task is acknowledged only after it finishes.
    task_acks_late=True,

    # Requeue a task if a worker disappears while processing it.
    task_reject_on_worker_lost=True,

    # Avoid a worker reserving many long-running AI tasks at once.
    worker_prefetch_multiplier=1,

    broker_connection_retry_on_startup=True,
)
