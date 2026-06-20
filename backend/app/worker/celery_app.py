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

# Daily stale-file cleanup. Runs via embedded beat (worker started with -B).
# ponytail: embedded beat is fine for one worker; use a separate beat service if scaled out.
celery_app.conf.beat_schedule = {
    "cleanup-stale-files": {
        "task": "cleanup_stale_files",
        "schedule": 86400.0,
    }
}


@worker_process_init.connect
def _init_worker_telemetry(**_kwargs):
    # Only worker processes set up worker-side telemetry (not the API importing this).
    from app.core.logredact import install_redaction
    from app.telemetry import instrument_celery, instrument_redis, setup_telemetry

    setup_telemetry("clearclause-worker")
    install_redaction()
    instrument_celery()
    instrument_redis()
