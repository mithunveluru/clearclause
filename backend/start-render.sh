#!/usr/bin/env sh
# Render free tier has no background-worker service type, so the Celery worker rides
# along in the web container. They share one 512MB instance: if OCR OOMs, it takes the
# API with it. The upgrade is a real Render Background Worker running the same command.
set -e

alembic upgrade head

celery -A app.worker.celery_app worker --beat \
  -Q ocr_queue,analysis_queue,report_queue,ai_queue,celery \
  --concurrency=1 --loglevel=info &

exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
