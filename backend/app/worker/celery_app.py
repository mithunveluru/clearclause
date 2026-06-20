from celery import Celery

from app.core.config import settings

# Redis as broker + result backend. Tasks are registered in Phase 10.
celery_app = Celery(
    "clearclause",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)
celery_app.conf.task_track_started = True
