from celery import Celery
from celery.signals import worker_process_init

from app.core.config import settings

celery_app = Celery(
    "clearclause",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.worker.tasks", "app.worker.pipeline"],
)
celery_app.conf.task_track_started = True

# No task may run forever: a pathological document must not hold the shared queue.
# Soft limit raises inside the task (stage marks the doc failed); hard limit kills it.
celery_app.conf.task_soft_time_limit = 540  # 9 min
celery_app.conf.task_time_limit = 600       # 10 min, SIGKILL backstop

# Staged pipeline routing (PIPELINE=staged). Worker consumes all of these queues.
celery_app.conf.task_routes = {
    "stage.ocr": {"queue": "ocr_queue"},
    "stage.classify": {"queue": "analysis_queue"},
    "stage.segment": {"queue": "analysis_queue"},
    "stage.analyze": {"queue": "analysis_queue"},
    "stage.score": {"queue": "analysis_queue"},
    "stage.report": {"queue": "report_queue"},
    "stage.chunk": {"queue": "ai_queue"},
    "stage.embed": {"queue": "ai_queue"},
    "stage.ai_summary": {"queue": "ai_queue"},
}

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
