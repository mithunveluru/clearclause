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
| 9 | Frontend experience | ✅ redesigned | Full premium rebuild (see Frontend Redesign note); all routes 200, tsc clean |
| 10 | Background jobs / worker | ✅ done | Celery task, 202 enqueue, status flow, retries+failure verified live |
| 11 | Observability | ✅ done | OTel traces+logs->Collector->Tempo/Loki, Prom /metrics, Grafana; failed-doc debuggable across all 3 |
| 12 | Security & privacy | ✅ done | Redis rate limit, log redaction, stale-file cleanup + report-orphan fix; verified live |
| 13 | Testing | ✅ done | 38 tests: unit + pipeline/DB/OCR integration + 6 sample e2e; all green in container |
| 14 | CI/CD | ✅ done | GH Actions CI (lint+test+build) & Release (GHCR+compose); gates verified green locally |
| 15 | Demo readiness | ✅ done | README + mermaid arch + seed script (verified) + DEMO.md + screenshot slots |

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

## Phase 11 checklist
- [x] OTel SDK in API + worker (traces + logs via OTLP), no-op unless OTEL endpoint set
- [x] Auto-instrument FastAPI + SQLAlchemy + Celery (producer+consumer) + Redis
- [x] Manual spans per pipeline step (ocr/segmentation/detection/scoring/report)
- [x] OTel Collector (otlp -> Tempo traces, Prometheus metrics, Loki logs)
- [x] Prometheus scrapes /metrics (request count, latency, errors) + collector
- [x] Grafana provisioned: 3 datasources + overview dashboard
- [x] Verified live: Prom series, Tempo api+worker traces, Loki logs, failed-doc error
      visible in logs+traces (DoD met)

### Phase 11 deviations (deliberate)
- Collector pinned to 0.111.0: the 0.116.0 images (core & contrib) fail to exec
  on this host (base-image/runc change). 0.111.0 runs clean.
- Pipeline-duration metrics (OCR/analysis/report time, queue wait) are captured as
  trace spans (Tempo), not Prometheus counters — debuggable per the DoD without
  custom metric plumbing across the separate worker process. Add OTel meters later
  if metric-level aggregation is needed.
- One overview Grafana dashboard (API + logs) instead of 5 separate ones; datasources
  for all 3 signals are wired so the others are quick to add.

## Phase 12 checklist
- [x] Redis fixed-window rate limit on register(5/m)/login(10/m)/upload(30/m) -> 429
- [x] Log redaction filter (email + bearer token) on root + handlers (incl. OTLP->Loki)
- [x] Report file removed on document delete (orphan fix from Phase 8 — CLOSED)
- [x] cleanup_stale_files task: delete docs past FILE_RETENTION_DAYS + sweep orphan files
- [x] Daily schedule via embedded celery beat (worker --beat)
- [x] Already in place: bcrypt, JWT, file type/size validation, uuid paths, per-user 404
- [x] Verified live: rate limit 429, delete removes report file, orphan sweep

## Frontend Redesign (premium rebuild)
Full first-principles redesign for an Apple/Stripe-grade feel. One cohesive system.
- Stack: Tailwind design tokens + custom primitives + Framer Motion + Lucide.
  Deliberately NOT MUI (Material fights the Apple aesthetic) and NOT shadcn-on-top
  (avoids mixing two systems, which the brief forbade). Said so to the user.
- Design system: lib/ui.ts (severity/band/label maps), tailwind tokens (ink scale,
  hairlines, soft shadows, Inter via next/font self-hosted), typography scale in globals.css.
- Primitives: Button, Surface/Container, Logo, TopBar, PageTransition.
- Components: UploadDropzone (premium), AnalysisProgress, RiskMeter, Severity,
  FindingsTimeline, ClauseInspectionPanel (slide-over), CostBreakdown, CategoryBreakdown.
- Screens: landing (Apple hero), login, register, dashboard (document workspace),
  documents/[id] (audit experience), /sample (static sample report for landing CTA).
- Removed superseded components: Stepper, RiskBadge, FindingCard, ClauseDrawer, TrueCostCard.
- Motion used sparingly (page transitions, upload, findings reveal, clause panel).

## Phase 13 checklist (38 tests, all green in container)
- [x] Unit: OCR grouping (mock), rules engine, scoring, report, security, files,
      segmentation, log redaction, cleanup sweep
- [x] Integration: full pipeline segment->detect->score->report (pure, deterministic)
- [x] Integration: DocumentRepository CRUD + ownership against real Postgres (skips if unreachable)
- [x] Integration: real Tesseract OCR on rendered image (skips without tesseract)
- [x] E2E: 6 seeded sample docs -> expected findings/band (risky x2, clean x2, subscription, bundled)
- [x] Test data: sample-data/*.txt (mounted into backend/worker at /sample-data)
- [x] pytest.ini: asyncio_mode=auto

## Product Experience Elevation (post-Phase-13)
- Auto-analyze: upload enqueues analysis automatically; no Analyze button. Dashboard
  upload routes straight to the live processing view.
- Processing experience: AnalysisProgress shows pipeline stages + cycling investigative
  lines ("Identifying fee clauses…", etc.) with Framer motion.
- Findings depth: `impact` is now first-class data (rules -> engine -> findings table ->
  API -> UI + PDF). Each finding shows what/why-it-matters/where/action. Severity is
  typographic (colored label) instead of filled chips.
- Real PDF report (ReportLab, purpose-built — NOT html2pdf): cover, exec summary, risk
  overview, key findings, clause analysis, cost impact, recommended actions, appendix,
  running header/footer + page numbers. /report serves application/pdf. Verified: 5-page
  valid PDF with all sections + impact.
- Landing: how-it-works (3 steps), trust band (explainable / private / rule-based),
  privacy line, footer disclaimer.
- Migration 0008: findings.impact, reports.pdf_path, reports.html_path nullable.
- Removed dead Severity.tsx. 38 backend tests green; frontend tsc clean.

## Phase 14 checklist
- [x] .github/workflows/ci.yml — on PR + push to main:
      backend (Postgres+Redis services, tesseract/poppler, ruff, alembic, pytest),
      frontend (npm install, next lint, tsc, next build), docker build + Trivy (non-blocking)
- [x] .github/workflows/release.yml — on push main/tags: validate compose, build+push
      backend & frontend to GHCR (matrix) with gha cache
- [x] .github/dependabot.yml (pip, npm, actions, docker, weekly)
- [x] .pre-commit-config.yaml (hygiene hooks + ruff)
- [x] Made gates green-by-construction: fixed main.py import order (ruff E402),
      added frontend .eslintrc.json; verified locally: ruff clean, 38 tests pass,
      next lint clean, next build succeeds (9 routes), compose config valid
- Note: frontend CI uses `npm install` (no committed lockfile); add package-lock.json
  later for `npm ci` reproducibility.

## Open items for later phases
- Markdown export (Phase 8 "optional") skipped — add if a user needs non-HTML.
- Per-step job rows (Phase 10) — one analysis job row per run for now.

## Deviations from spec (deliberate, ponytail)
- `docker-compose.yml` at repo root, not `infra/`, so the spec's documented
  `docker compose up` works without `-f`. `infra/` holds observability config.
- Worker reuses the backend image (one Dockerfile) instead of a separate
  package dir — fewer files, shared models. Split later if it grows.
