# ClearClause

Scans loan documents and subscription terms to surface hidden fees, penalty
clauses, auto-renew traps, weak consent, and unclear pricing — with a risk
score, plain-English explanations, and a downloadable report.

Free, local-first stack: Next.js · FastAPI · PostgreSQL · Redis · Tesseract OCR
· Celery worker · OpenTelemetry/Grafana observability.

> Full README (architecture, screenshots, trade-offs) is completed in Phase 15.
> See `docs/PROGRESS.md` for phase status and `ClearClause-Claude.md` for the spec.

## Quick start

```bash
cp .env.example .env
docker compose up --build
# backend migrations (once db is up):
docker compose exec backend alembic upgrade head
```

| Service | URL |
|---|---|
| Frontend | http://localhost:3000 |
| API docs | http://localhost:8000/docs |
| API health | http://localhost:8000/health |
