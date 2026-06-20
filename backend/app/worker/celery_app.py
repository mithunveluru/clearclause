from celery import Celery
from celery.signals import worker_process_init

from app.core.config import settings

# Redis as broker + result backend.
celery_app = Celery(
    "clearclause",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.worker.tasks"],
)
celery_app.conf.task_track_started = True


@worker_process_init.connect
def _init_worker_telemetry(**_kwargs):
    # Only worker processes set up worker-side telemetry (not the API importing this).
    from app.telemetry import instrument_celery, instrument_redis, setup_telemetry

    setup_telemetry("clearclause-worker")
    instrument_celery()
    instrument_redis()
