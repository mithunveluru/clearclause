# ClearClause — Implementation Progress

Source of truth: `ClearClause-Claude.md`. One row per phase; checked when its
Definition of Done is met.

| Phase | Title | Status | Notes |
|---|---|---|---|
| 0 | Product framing | ✅ done | Scope/taxonomy frozen in spec; samples land in Phase 13/15 |
| 1 | Repo & local infra | 🟡 in progress | Compose + health endpoints + Alembic wired |
| 2 | Auth & access control | ⬜ todo | |
| 3 | Document ingestion | ⬜ todo | |
| 4 | OCR pipeline | ⬜ todo | |
| 5 | Clause segmentation | ⬜ todo | |
| 6 | Detection engine | ⬜ todo | |
| 7 | Risk scoring & true-cost | ⬜ todo | |
| 8 | Report generation | ⬜ todo | |
| 9 | Frontend experience | ⬜ todo | |
| 10 | Background jobs / worker | ⬜ todo | |
| 11 | Observability | ⬜ todo | |
| 12 | Security & privacy | ⬜ todo | |
| 13 | Testing | ⬜ todo | |
| 14 | CI/CD | ⬜ todo | |
| 15 | Demo readiness | ⬜ todo | |

## Phase 1 checklist
- [x] Monorepo structure (frontend/backend/storage/infra/sample-data/docs/scripts)
- [x] Dockerfiles (frontend, backend; worker shares backend image)
- [x] Root docker-compose.yml (db, redis, backend, worker, frontend)
- [x] Postgres + Redis containers with healthchecks
- [x] Local upload/report dirs
- [x] Next.js app initialized
- [x] FastAPI app initialized
- [x] Worker package (Celery app)
- [x] Alembic wired (env.py targets Base.metadata)
- [x] .env.example
- [ ] DoD: `docker compose up` runs all core services; FE+BE /health respond
      (requires Docker — run locally to confirm)

## Deviations from spec (deliberate, ponytail)
- `docker-compose.yml` at repo root, not `infra/`, so the spec's documented
  `docker compose up` works without `-f`. `infra/` holds observability config.
- Worker reuses the backend image (one Dockerfile) instead of a separate
  package dir — fewer files, shared models. Split later if it grows.
