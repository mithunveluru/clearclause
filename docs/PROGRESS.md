# ClearClause — Implementation Progress

Source of truth: `ClearClause-Claude.md`. One row per phase; checked when its
Definition of Done is met.

| Phase | Title | Status | Notes |
|---|---|---|---|
| 0 | Product framing | ✅ done | Scope/taxonomy frozen in spec; samples land in Phase 13/15 |
| 1 | Repo & local infra | ✅ code done | Runtime `docker compose up` check is user-run |
| 2 | Auth & access control | ✅ done | JWT + bcrypt; register/login/refresh + /me; security tests pass |
| 3 | Document ingestion | ✅ done | Upload/list/get/delete verified live; magic-byte validation; uuid storage |
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

## Phase 2 checklist
- [x] `users` model + Alembic migration (0001), email unique index
- [x] bcrypt password hashing (spec allowed bcrypt or passlib; passlib dropped — unmaintained, breaks on modern bcrypt)
- [x] JWT access + refresh tokens (HS256)
- [x] register / login / refresh endpoints + service/repository separation
- [x] get_current_user dependency + protected /api/v1/me route
- [x] security unit tests pass (3/3)

## Phase 3 checklist
- [x] `documents` + `jobs` tables + migration 0002 (indexes: documents.user_id, documents.status, jobs.document_id)
- [x] Upload endpoint with bounded read + MAX_UPLOAD_MB (413) enforcement
- [x] File validation: extension allowlist + magic-byte content sniff (rejects disguised files)
- [x] UUID stored filenames; original filename never used in path
- [x] List / get / delete with per-user ownership (404 on others' docs)
- [x] Verified live: register→login→upload→list→get→delete, status=`uploaded`

## Deviations from spec (deliberate, ponytail)
- `docker-compose.yml` at repo root, not `infra/`, so the spec's documented
  `docker compose up` works without `-f`. `infra/` holds observability config.
- Worker reuses the backend image (one Dockerfile) instead of a separate
  package dir — fewer files, shared models. Split later if it grows.
