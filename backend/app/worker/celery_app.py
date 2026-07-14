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

# One document must not hold the queue forever
celery_app.conf.task_soft_time_limit = 540  # 9 min, raises inside the task
celery_app.conf.task_time_limit = 600       # 10 min, SIGKILL backstop

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

# ponytail: embedded beat; separate service if scaled out
celery_app.conf.beat_schedule = {
    "cleanup-stale-files": {
        "task": "cleanup_stale_files",
        "schedule": 86400.0,
    }
}


@worker_process_init.connect
def _init_worker_telemetry(**_kwargs):
    # Worker processes only, not the API importing this
    from app.core.logredact import install_redaction
    from app.telemetry import instrument_celery, instrument_redis, setup_telemetry

    setup_telemetry("clearclause-worker")
    install_redaction()
    instrument_celery()
    instrument_redis()
