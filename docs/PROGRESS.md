# ClearClause — Implementation Progress

Source of truth: `ClearClause-Claude.md`. One row per phase; checked when its
Definition of Done is met.

| Phase | Title | Status | Notes |
|---|---|---|---|
| 0 | Product framing | ✅ done | Scope/taxonomy frozen in spec; samples land in Phase 13/15 |
| 1 | Repo & local infra | ✅ code done | Runtime `docker compose up` check is user-run |
| 2 | Auth & access control | ✅ done | JWT + bcrypt; register/login/refresh + /me; security tests pass |
| 3 | Document ingestion | ✅ done | Upload/list/get/delete verified live; magic-byte validation; uuid storage |
| 4 | OCR pipeline | ✅ done | OCRProvider+Tesseract+Paddle placeholder; blocks persisted & verified live |
| 5 | Clause segmentation | ✅ done | normalize + split + section + classify; clauses persisted, verified live |
| 6 | Detection engine | ✅ done | 11 clause rules + doc-level missing-disclosure; findings API; live DoD passed |
| 7 | Risk scoring & true-cost | ✅ done | weighted score+bands+summary, cost extraction; /score API; live DoD passed |
| 8 | Report generation | ✅ done | summary_json + Jinja2 HTML, saved path, /report download; live DoD passed |
| 9 | Frontend experience | ✅ code done | All screens+components render 200, typecheck clean, CORS wired; browser click-through is user-run |
| 10 | Background jobs / worker | ✅ done | Celery task, 202 enqueue, status flow, retries+failure verified live |
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

## Phase 4 checklist
- [x] `OCRProvider` ABC (extract -> list of page/order/text/bbox blocks)
- [x] `TesseractOCRProvider` (images + PDF page rasterization via pdf2image)
- [x] `PaddleOCRProvider` placeholder (raises NotImplementedError)
- [x] `get_ocr_provider()` factory driven by OCR_PROVIDER setting
- [x] `extracted_blocks` table + migration 0003 (index on document_id)
- [x] OCRService persists blocks (CPU work offloaded via asyncio.to_thread)
- [x] Verified live: image OCR -> blocks in DB linked to document/page; 8 unit tests pass

## Phase 5 checklist
- [x] Normalizer: NFKC, unicode quotes/dashes, strip non-printable OCR junk, collapse space/repeat-punct
- [x] Heading detection (carries section_name forward)
- [x] Clause splitter (sentence terminators + bullets, drops fragments)
- [x] Coarse clause_type classifier (penalty>renewal>cancellation>consent>add_on>fee, priority-ordered)
- [x] `clauses` table + migration 0004; SegmentationService blocks->clauses
- [x] Verified live: OCR->segment->clauses in DB with section/page/type; 13 unit tests pass

## Note for Phase 6
OCR output can have spacing/char artifacts. Rules engine must match on
normalized text (Phase 5) and tolerate minor spacing, not exact strings.

## Phase 9 checklist
- [x] Screens: landing, login, register, dashboard (upload+history), document detail
- [x] Components: UploadDropzone, Stepper, RiskBadge, FindingCard, ClauseDrawer, TrueCostCard, DownloadReportButton
- [x] `lib/api.ts` fetch client (JWT in localStorage)
- [x] Backend: POST /analyze (sync pipeline; Phase 10 makes async), findings enriched with clause_text
- [x] CORS middleware (CORS_ORIGINS), preflight verified
- [x] Tailwind v3 (v4 native scanner had version-skew bug); pages render 200, tsc clean
- [ ] DoD: browser click-through (upload→analyze→read results) — run at http://localhost:3000

## Phase 10 checklist
- [x] Celery task run_analysis (Redis broker); /analyze returns 202 in ~3ms
- [x] Worker drives document status: uploaded->ocr_*->analysis_*->report_ready
- [x] jobs row per attempt (running->done/failed, timestamps, error_message)
- [x] Retries: autoretry_for=Exception, max_retries=2 (3 attempts verified on failure)
- [x] Failure sets document status=failed; frontend polls + shows failed state
- [x] Fresh async engine per task (asyncpg pool bound to task's event loop)

## Open items for later phases
- Phase 12 cleanup: deleting a document removes its upload file but not its
  report HTML file (reports row cascades in DB, file orphans). Handle in the
  auto-cleanup job or extend DocumentService.delete to remove the report file.
- Markdown export (Phase 8 "optional") skipped — add if a user needs non-HTML.

## Deviations from spec (deliberate, ponytail)
- `docker-compose.yml` at repo root, not `infra/`, so the spec's documented
  `docker compose up` works without `-f`. `infra/` holds observability config.
- Worker reuses the backend image (one Dockerfile) instead of a separate
  package dir — fewer files, shared models. Split later if it grows.
