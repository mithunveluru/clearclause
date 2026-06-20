# ClearClause — Claude.md

## Purpose

This document is the complete phase-by-phase implementation plan for **ClearClause**, a free-stack consumer-fintech product that scans loan documents, subscription terms, screenshots, and checkout flows to detect hidden fees, penalty clauses, auto-renew traps, bundled add-ons, weak consent, and unclear pricing disclosures.[cite:147][cite:148][cite:151][cite:154][cite:157]

The plan is optimized for a **solo developer**, a **one-week MVP**, and a **fully free local-first stack** using open-source tools and free developer infrastructure.[cite:203][cite:205][cite:193][cite:208]

---

## 1. Product Definition

### 1.1 Core Problem

Users regularly agree to financial terms they do not fully understand, especially in digital lending flows, subscription trials, and recurring payment mandates. Current regulatory and consumer-protection pressure in India increasingly emphasizes transparent fees, clear borrower disclosures, explicit consent, and reduced dark patterns, which makes this product timely and defensible.[cite:147][cite:148][cite:149][cite:154][cite:157]

### 1.2 Product Vision

ClearClause should help a user answer five questions before they commit to a loan or recurring payment:[cite:147][cite:152][cite:157]

- What am I actually agreeing to?
- What hidden or delayed costs exist?
- Which clauses are risky or manipulative?
- What is the likely true cost beyond the headline offer?
- What should I ask or do before accepting?

### 1.3 MVP Promise

A user uploads a PDF, image, screenshot, or pasted text and receives:[cite:147][cite:151][cite:152][cite:157]

- A risk score.
- Highlighted risky clauses.
- Plain-English explanations.
- A true-cost summary.
- Suggested next actions.
- A downloadable report.

### 1.4 Narrow MVP Scope

The MVP should support only two use cases:[cite:147][cite:151][cite:157]

- Personal loan agreements and lending disclosures.
- Subscription, free-trial, and AutoPay-style recurring payment terms.

That narrow scope keeps the project realistic for one week while still making the product differentiated and useful.

---

## 2. Product Goals

### 2.1 Functional Goals

The first version must:

- Accept PDF and image uploads.
- Extract text reliably enough for common typed documents.
- Detect 5 to 10 high-value issue types.
- Produce structured findings with severity and explanations.
- Estimate true cost when fees and penalties are available.
- Generate a clean HTML or Markdown report.
- Store a history of scans per user.

### 2.2 Non-Functional Goals

The MVP should aim for:

- Scan completion in under 15 seconds for common small files.
- Fully local development with Docker Compose.
- No paid OCR, cloud storage, or managed observability.
- Explainable rule-based findings rather than opaque model-only output.
- Clear separation between upload, OCR, analysis, scoring, and reporting.

### 2.3 What Not to Build Yet

Do not include in the MVP:

- Full legal compliance automation.
- Real lender integrations.
- Full browser extension support.
- SMS or email ingestion.
- Multi-language OCR.
- Paid LLM summarization.
- Marketplace or recommendation engine.

---

## 3. Free Stack

### 3.1 Application Stack

| Layer | Choice | Why |
|---|---|---|
| Frontend | Next.js + TypeScript + Tailwind | Modern product stack, strong hiring signal, fast UI delivery.[cite:191][cite:199] |
| Backend API | FastAPI | High velocity, clean async APIs, excellent for OCR and rules workflows.[cite:203][cite:202][cite:205] |
| Worker | FastAPI worker or Celery worker | Clean async processing without paying for Kafka or cloud queues.[cite:205] |
| Database | PostgreSQL | Production-standard relational storage.[cite:203][cite:202] |
| Cache / queue | Redis | Job queue, rate limits, caching, dedupe.[cite:202][cite:205] |
| OCR | Tesseract first, PaddleOCR adapter later | Tesseract is lighter and faster; PaddleOCR can improve hard-layout accuracy.[cite:179][cite:204][cite:192][cite:200] |
| File storage | Local filesystem first | Completely free and simple for MVP. |
| Local orchestration | Docker Compose | Best free local setup for multi-service dev.[cite:205][cite:193][cite:206][cite:208] |
| Observability | OpenTelemetry + Prometheus + Loki + Tempo + Grafana | Fully open-source logs, metrics, traces stack.[cite:193][cite:206][cite:208][cite:180][cite:63] |
| CI/CD | GitHub Actions | Free enough for personal project workflows. |

### 3.2 Why This Stack

This stack is the best free option because it avoids paid OCR APIs, paid queues, paid databases, and managed cloud infrastructure while still looking production-grade on GitHub. Open-source FastAPI templates, OCR comparisons, and Docker Compose observability setups all support this path as practical and maintainable for small teams or solo developers.[cite:203][cite:205][cite:179][cite:193][cite:208]

---

## 4. Architecture Strategy

### 4.1 System Shape

The correct architecture for the free MVP is a **modular monolith with a separate worker**, not full microservices. That keeps implementation cost and operational complexity low while preserving clean module boundaries that can be split later.[cite:203][cite:205][cite:202]

### 4.2 High-Level Architecture

```text
User
  │
  ▼
Next.js Frontend
  │
  ▼
FastAPI API
  ├── Auth
  ├── Upload
  ├── Documents
  ├── Findings
  ├── Reports
  └── Health / Metrics
  │
  ├── PostgreSQL
  ├── Redis
  └── Local File Storage
       │
       ▼
Worker Process
  ├── OCR
  ├── Clause Segmentation
  ├── Rules Engine
  ├── Risk Scoring
  └── Report Generation

Telemetry:
App + Worker → OTel Collector → Prometheus / Loki / Tempo → Grafana
```

The OpenTelemetry-to-Grafana pattern above is a standard open-source local observability architecture using Collector, Prometheus, Loki, Tempo, and Grafana.[cite:193][cite:206][cite:208][cite:180][cite:63]

### 4.3 Why Not Kafka Yet

Kafka is strong for event-driven systems, but it adds resource and operational overhead to a solo-developer free MVP. Redis-backed workers or Celery provide enough async structure for document processing while keeping the stack simple and free.[cite:205]

---

## 5. Core Features

### 5.1 User-Facing Features

- User registration and login.
- Secure file upload.
- Document processing status tracking.
- Scan history dashboard.
- Findings list with severity labels.
- Clause-by-clause explanations.
- True-cost summary card.
- Downloadable report.
- Demo documents for instant testing.

### 5.2 Risk Types to Detect

The first version should detect at least these issue types:[cite:147][cite:148][cite:151][cite:157]

- Hidden processing fees.
- Service or convenience fees.
- Vague pricing revision clauses.
- Late payment or penalty fee clauses.
- Foreclosure or prepayment charges.
- Auto-renew or recurring debit traps.
- Hard-to-cancel wording.
- Bundled insurance or add-ons.
- Weak or implied consent wording.
- Missing clear total-cost or APR-style disclosure.

---

## 6. Phase Plan

## Phase 0 — Product Framing

### Goals

- Finalize exact MVP scope.
- Freeze supported input formats.
- Freeze supported risk categories.
- Define success metrics.

### Deliverables

- 1-page product brief.
- Use-case list.
- Detection taxonomy.
- 6 sample documents.

### Decisions

- Supported input: PDF, PNG, JPG, pasted text.
- Supported domains: loans and subscription terms only.
- Output: risk score, findings, report.

---

## Phase 1 — Repo and Local Infrastructure

### Goals

Create the full development skeleton and make the project runnable locally with one command.[cite:205][cite:193][cite:208]

### Deliverables

- Monorepo structure.
- Dockerfiles for frontend, API, worker.
- Docker Compose file.
- PostgreSQL container.
- Redis container.
- Local upload and report directories.

### Folder Structure

```text
clearclause/
├── frontend/
├── backend/
├── storage/
│   ├── uploads/
│   └── reports/
├── infra/
│   ├── docker-compose.yml
│   ├── otel/
│   ├── grafana/
│   ├── prometheus/
│   ├── loki/
│   └── tempo/
├── sample-data/
├── docs/
└── scripts/
```

### Tasks

- Initialize Next.js app.
- Initialize FastAPI app.
- Add worker process package.
- Add Alembic for migrations.
- Add `.env.example`.
- Confirm all services start via Compose.

### Definition of Done

- `docker compose up` runs all core services successfully.
- Frontend and backend health endpoints respond.

---

## Phase 2 — Auth, Accounts, and Access Control

### Goals

Build the authentication baseline needed for per-user uploads and scan history.

### Deliverables

- Register endpoint.
- Login endpoint.
- JWT auth.
- Password hashing.
- Protected routes.

### Tech Notes

- Use JWT access tokens.
- Use bcrypt or passlib for password hashing.
- Start with roles: `user`, `admin`.

### Endpoints

- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/refresh`

### Definition of Done

- User can register, log in, and access protected document routes.

---

## Phase 3 — Document Ingestion

### Goals

Allow users to upload files, validate them, store metadata, and prepare them for processing.

### Deliverables

- Upload endpoint.
- File validation.
- Metadata persistence.
- File storage on local disk.
- Document status tracking.

### Rules

- Accept only PDF, PNG, JPG, JPEG.
- Apply upload size limit, for example 10 MB.
- Generate unique stored filenames.
- Never trust original filenames for path access.

### Tables

- `documents`
- `jobs`

### Endpoints

- `POST /api/v1/documents/upload`
- `GET /api/v1/documents`
- `GET /api/v1/documents/{id}`
- `DELETE /api/v1/documents/{id}`

### Definition of Done

- User uploads a file and sees it listed in the dashboard with status `uploaded`.

---

## Phase 4 — OCR Pipeline

### Goals

Extract text from uploaded documents using a fully free OCR pipeline.[cite:179][cite:204][cite:192][cite:200]

### Deliverables

- OCR provider abstraction.
- Tesseract implementation.
- PDF page conversion.
- Extracted text block storage.
- Page number metadata.

### Recommended Libraries

- `pytesseract`
- `pdf2image`
- `Pillow`
- `PyMuPDF` or `pdfplumber`

### OCR Provider Interface

```python
class OCRProvider:
    def extract(self, file_path: str) -> list[dict]:
        ...
```

### First Implementation

- `TesseractOCRProvider`
- `PaddleOCRProvider` placeholder only

### Why Tesseract First

Tesseract is a lighter, easier local-first option and can be significantly faster, which makes it better for a free CPU-only MVP, while PaddleOCR can be added later for harder layouts.[cite:179][cite:200][cite:204][cite:192]

### Tables

- `extracted_blocks`

### Definition of Done

- Uploaded PDF or image produces extracted text blocks linked to pages and stored in the database.

---

## Phase 5 — Clause Segmentation and Normalization

### Goals

Break extracted text into analyzable chunks and prepare it for rule matching.

### Deliverables

- Section splitter.
- Sentence or clause splitter.
- Normalized text cleaner.
- Candidate clause labeling.

### Processing Steps

- Remove OCR junk patterns.
- Normalize spacing and punctuation.
- Split by headings and bullet groups where possible.
- Classify likely clause type: fee, penalty, consent, renewal, cancellation, add-on.

### Tables

- `clauses`

### Definition of Done

- Every uploaded document has clause records ready for analysis.

---

## Phase 6 — Detection Engine

### Goals

Implement the explainable intelligence layer using rules, not expensive model-heavy inference.

### Deliverables

- Rules module.
- Issue taxonomy.
- Confidence scoring.
- Severity mapping.
- Action templates.

### Detection Categories

- Hidden fee.
- Processing fee.
- Service fee.
- Late fee.
- Prepayment penalty.
- Foreclosure charge.
- Auto-renew trap.
- Hard cancellation.
- Bundled add-on.
- Implied consent.
- Vague pricing revision.
- Missing clear cost disclosure.[cite:147][cite:148][cite:151][cite:157]

### Example Pattern Ideas

- `processing fee`
- `charges may be revised`
- `auto-renew`
- `unless cancelled`
- `non-refundable`
- `insurance included`
- `deemed consent`
- `late payment charge`

### Output Shape

Each finding should include:

- Issue type.
- Severity.
- Confidence.
- Exact clause text.
- Plain-English explanation.
- Suggested action.

### Tables

- `findings`

### Definition of Done

- A sample bad document consistently returns expected findings.

---

## Phase 7 — Risk Scoring and True-Cost Engine

### Goals

Turn raw findings into a usable decision summary.

### Deliverables

- Weighted risk score.
- Severity bands.
- True-cost calculator.
- Action summary.

### Suggested Weighting

| Category | Max score |
|---|---:|
| Fee opacity | 20 |
| Penalty severity | 15 |
| Auto-renew risk | 15 |
| Consent weakness | 15 |
| Cancellation friction | 10 |
| Bundling risk | 10 |
| Missing disclosure | 10 |
| Readability complexity | 5 |

### Risk Bands

- 0–24: Low
- 25–49: Moderate
- 50–74: High
- 75–100: Critical

### Example Outputs

- “This loan looks high risk because fees are not clearly disclosed.”
- “This subscription appears difficult to cancel before renewal.”
- “This offer may cost more than the headline rate suggests.”

### Tables

- `risk_scores`
- `cost_breakdowns`

### Definition of Done

- User receives a total score, category breakdown, and summary sentence.

---

## Phase 8 — Report Generation

### Goals

Generate a user-facing result artifact that is easy to read and export.

### Deliverables

- Summary JSON generator.
- HTML report template.
- Saved report path.
- Download endpoint.

### Report Contents

- Document name and type.
- Overall score.
- Top findings.
- Clause-by-clause analysis.
- True-cost section.
- Suggested questions to ask.
- Warning banner for high-risk items.

### Output Format

- HTML first.
- Optional Markdown export.
- PDF export only if time allows.

### Tables

- `reports`

### Definition of Done

- User can open or download a complete report for a processed document.

---

## Phase 9 — Frontend Product Experience

### Goals

Deliver a clean and trustworthy product UI.

### Required Screens

- Landing / upload page.
- Login and register pages.
- Dashboard / scan history.
- Document detail / findings page.
- Report view page.

### Required Components

- Upload dropzone.
- Progress stepper.
- Risk score badge.
- Finding cards.
- Clause detail drawer.
- True-cost summary card.
- Download report button.

### UX Rules

- Show plain-English meaning first.
- Show raw clause second.
- Use red/amber/green severity colors.
- Keep the design minimal and trust-focused.
- Make findings scannable in under 10 seconds.

### Definition of Done

- User can upload a file, wait for processing, and clearly understand results from the UI alone.

---

## Phase 10 — Background Jobs and Worker Flow

### Goals

Move OCR and analysis out of the request-response cycle to avoid blocking the API.

### Deliverables

- Redis-backed job queue.
- Worker process.
- Retry logic.
- Failure status updates.

### Recommended Approach

Use Celery or a lightweight Redis-backed worker because it is a proven free pattern for FastAPI projects needing async document workflows.[cite:205]

### Job Types

- OCR job.
- Clause segmentation job.
- Analysis job.
- Scoring job.
- Report generation job.

### Document Status Flow

- `uploaded`
- `ocr_processing`
- `ocr_done`
- `analysis_processing`
- `analysis_done`
- `report_ready`
- `failed`

### Definition of Done

- Upload returns quickly and processing continues asynchronously.

---

## Phase 11 — Observability

### Goals

Make the product debuggable and production-like using fully free observability tools.[cite:193][cite:206][cite:208][cite:180][cite:63]

### Deliverables

- OpenTelemetry instrumentation in API and worker.
- OTel Collector config.
- Prometheus metrics scraping.
- Loki log ingestion.
- Tempo trace ingestion.
- Grafana dashboards.

### Required Metrics

- Request count.
- API latency.
- Upload success/failure.
- OCR duration.
- Queue wait time.
- Analysis duration.
- Error count.
- Report generation time.

### Dashboards

1. API health dashboard.
2. OCR pipeline dashboard.
3. Queue and worker dashboard.
4. Findings-by-type dashboard.
5. Error dashboard.

### Definition of Done

- A single failed document can be debugged from logs, metrics, and traces.

---

## Phase 12 — Security and Privacy

### Goals

Implement minimum viable trust and safety for a consumer-fintech tool.

### Requirements

- Password hashing.
- JWT auth.
- File type validation.
- File size validation.
- Local path safety.
- Rate limiting via Redis.
- Mask sensitive content in logs.
- User ownership checks on document access.
- Delete endpoint for uploaded documents.
- Auto-cleanup job for stale files.

### Privacy Rules

- Do not log full document text in plaintext logs.
- Store files only as long as needed.
- Avoid sending raw content to paid external AI APIs.

### Definition of Done

- The product has a clear, reasonable local privacy posture for an MVP.

---

## Phase 13 — Testing

### Goals

Make the project credible and maintainable.

### Unit Tests

- OCR adapter tests.
- Rule engine tests.
- Scoring tests.
- Report generator tests.

### Integration Tests

- Upload to DB flow.
- Worker queue processing.
- OCR to findings pipeline.
- Findings to report pipeline.

### End-to-End Tests

- Upload sample loan PDF and assert expected findings.
- Upload subscription screenshot and assert auto-renew result.

### Test Data

Prepare at least six seeded files:

- Two clean loan documents.
- Two risky loan documents.
- One trial-renewal screenshot.
- One bundled add-on document.

### Definition of Done

- Core flows pass locally before demo or deployment.

---

## Phase 14 — CI/CD and Developer Workflow

### Goals

Automate quality checks and image builds.

### GitHub Actions Workflows

#### Pull Request Workflow

- Lint frontend.
- Lint backend.
- Run backend tests.
- Run frontend tests.
- Build Docker images.

#### Main Branch Workflow

- Re-run tests.
- Build production images.
- Push to GitHub Container Registry.
- Validate Docker Compose or deployment config.

### Nice-to-Haves

- Trivy image scan.
- Dependabot.
- Pre-commit hooks.

### Definition of Done

- Every pull request is automatically validated.

---

## Phase 15 — Demo Readiness

### Goals

Make the project interview-ready and GitHub-ready.

### Deliverables

- Strong README.
- Architecture diagram.
- Sample documents.
- Seed script.
- Demo script.
- Screenshots or GIF.

### README Must Include

- Problem statement.
- Why this matters now.
- Feature list.
- Architecture overview.
- Stack explanation.
- Local run instructions.
- Screenshots.
- Observability screenshots.
- Trade-offs and future roadmap.

### Definition of Done

- A reviewer can clone, run, test, and understand the system in under 10 minutes.

---

## 7. Database Plan

### Tables

```text
users
  id, email, password_hash, created_at

documents
  id, user_id, original_filename, file_path, source_type, doc_type, status, created_at

jobs
  id, document_id, job_type, status, error_message, started_at, finished_at

extracted_blocks
  id, document_id, page_number, block_order, text, bbox_json

clauses
  id, document_id, clause_type, raw_text, normalized_text, page_number, section_name

findings
  id, document_id, clause_id, issue_type, severity, confidence, explanation, action_text, created_at

risk_scores
  id, document_id, total_score, fee_opacity_score, penalty_score, consent_score, renewal_score, cancellation_score

cost_breakdowns
  id, document_id, headline_rate, processing_fee, late_fee, renewal_fee, foreclosure_charge, estimated_true_cost

reports
  id, document_id, summary_json, html_path, created_at
```

### Database Rules

- Add foreign keys for all dependent entities.
- Add index on `documents.user_id`.
- Add index on `documents.status`.
- Add index on `findings.document_id`.
- Add timestamps on all key entities.

---

## 8. API Plan

### Auth

- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/refresh`

### Documents

- `POST /api/v1/documents/upload`
- `GET /api/v1/documents`
- `GET /api/v1/documents/{id}`
- `DELETE /api/v1/documents/{id}`

### Analysis

- `POST /api/v1/documents/{id}/analyze`
- `GET /api/v1/documents/{id}/findings`
- `GET /api/v1/documents/{id}/score`
- `GET /api/v1/documents/{id}/report`

### System

- `GET /health`
- `GET /metrics`

---

## 9. Environment Variables

### Backend

```env
DATABASE_URL=
REDIS_URL=
JWT_SECRET=
UPLOAD_DIR=
REPORT_DIR=
OCR_PROVIDER=tesseract
OTEL_EXPORTER_OTLP_ENDPOINT=
MAX_UPLOAD_MB=10
```

### Frontend

```env
NEXT_PUBLIC_API_BASE_URL=
```

### Grafana / Observability

```env
GRAFANA_ADMIN_USER=
GRAFANA_ADMIN_PASSWORD=
```

---

## 10. Local Run Plan

### First-Time Setup

1. Clone repo.
2. Copy `.env.example` to `.env`.
3. Run `docker compose up --build`.
4. Run DB migrations.
5. Open frontend and Grafana.

### Core Local URLs

- Frontend: `http://localhost:3000`
- API docs: `http://localhost:8000/docs`
- Grafana: `http://localhost:3001`
- Prometheus: `http://localhost:9090`

---

## 11. 7-Day Execution Plan

### Day 1

- Create repo.
- Set up Compose.
- Set up frontend, backend, Postgres, Redis.
- Add auth and health routes.

### Day 2

- Build upload flow.
- Store files locally.
- Persist document metadata.
- Build dashboard shell.

### Day 3

- Add Tesseract OCR pipeline.
- Parse PDF and images.
- Store extracted blocks.

### Day 4

- Add clause segmentation.
- Add rule engine.
- Add first findings categories.

### Day 5

- Add risk scoring and true-cost logic.
- Build results UI.
- Generate HTML reports.

### Day 6

- Add Redis-backed worker.
- Add observability stack.
- Add dashboards and GitHub Actions.

### Day 7

- Seed sample files.
- Polish frontend.
- Improve README.
- Record demo.
- Run end-to-end checks.

---

## 12. Future Upgrade Path

After the free MVP is working, the next upgrades should be:

- Swap local storage for MinIO or S3.
- Add PaddleOCR for harder layouts.[cite:204][cite:192]
- Add side-by-side compare mode.
- Add browser extension capture.
- Add multi-language support.
- Split worker into separate services.
- Add message broker if throughput grows.

---

## 13. Senior Engineer Review Checklist

A senior reviewer should be able to see these qualities:

- Clear problem and user value.
- Sensible scope control.
- Production-style architecture without overengineering.
- Async document pipeline.
- Explainable rule engine.
- Secure file handling.
- Good schema design.
- Strong observability.
- Automated tests and CI.
- Thoughtful README and demos.

If all of those are visible, the project will read as serious engineering work rather than a shallow AI demo.

---

## 14. Final Build Recommendation

The best free version of ClearClause is:

- Next.js frontend.[cite:191][cite:199]
- FastAPI API.[cite:203][cite:202]
- FastAPI or Celery worker with Redis.[cite:205]
- PostgreSQL database.[cite:203][cite:202]
- Tesseract-first OCR with PaddleOCR adapter later.[cite:179][cite:204][cite:192][cite:200]
- Docker Compose local orchestration.[cite:205][cite:193][cite:206][cite:208]
- OpenTelemetry + Prometheus + Loki + Tempo + Grafana observability stack.[cite:193][cite:206][cite:208][cite:180][cite:63]
- GitHub Actions CI/CD.

This version stays free, ships fast, and still demonstrates strong full-stack and platform engineering judgment.
