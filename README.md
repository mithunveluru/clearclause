# ClearClause

**Understand exactly what you're agreeing to.** ClearClause reviews loan agreements
and subscription terms for hidden fees, penalties, and auto-renew traps — and explains
every risk in plain English, with a downloadable PDF report.

Upload a PDF or image → it reads the text, segments every clause, applies an
**explainable rule engine**, scores the risk, estimates the true cost, and generates a
professional report. No black-box, model-only verdicts: every finding traces to specific
wording in your document.

---

## Why this matters

Consumers routinely agree to financial terms they don't fully understand — hidden
processing fees deducted upfront, late-payment penalties, prepayment/foreclosure charges,
free-trial auto-renewals, bundled insurance, and "deemed consent" clauses. Regulatory and
consumer-protection pressure increasingly emphasises transparent fees, clear borrower
disclosures, explicit consent, and fewer dark patterns. ClearClause puts that scrutiny in
the consumer's hands before they sign.

**MVP scope:** personal-loan agreements and subscription / free-trial / AutoPay terms.

## Features

- Secure upload (PDF / PNG / JPG) with content-sniffing validation
- **Automatic** pipeline — analysis starts on upload, no extra step
- Free, local-first OCR (Tesseract) behind a pluggable provider interface
- Clause segmentation + normalization
- Explainable detection of 12 risk categories (fees, penalties, auto-renew, consent, …)
- Weighted risk score (0–100) with severity bands and a plain-English summary
- True-cost estimation from amounts stated in the document
- Per-finding depth: what was found · why it matters · where it appears · what to do
- **Purpose-built PDF report** (cover, executive summary, clause analysis, cost impact, …)
- Per-user scan history, ownership-enforced access, document deletion
- Full observability: traces, metrics, and logs

## Architecture

A **modular monolith with a separate worker** — clean module boundaries without
microservice overhead.

```mermaid
flowchart TD
    U[User] --> FE[Next.js frontend]
    FE -->|JWT REST| API[FastAPI API]
    API --> PG[(PostgreSQL)]
    API --> RD[(Redis)]
    API --> FS[/Local file storage/]
    API -->|enqueue| RD
    RD -->|job| W[Celery worker]
    W --> OCR[OCR · Tesseract]
    OCR --> SEG[Clause segmentation]
    SEG --> DET[Rule engine]
    DET --> SCORE[Risk scoring + true cost]
    SCORE --> REP[PDF report]
    W --> PG
    API -.OTLP.-> COL[OTel Collector]
    W -.OTLP.-> COL
    COL --> TEMPO[Tempo · traces]
    COL --> LOKI[Loki · logs]
    API -. /metrics .-> PROM[Prometheus]
    COL --> PROM
    TEMPO & LOKI & PROM --> GRAF[Grafana]
```

**Pipeline:** Upload → OCR → Clause extraction → Risk detection → Scoring → Report.

## Stack

| Layer | Choice | Why |
|---|---|---|
| Frontend | Next.js + TypeScript + Tailwind + Framer Motion | Modern, fast, premium UI |
| API | FastAPI + SQLAlchemy 2.0 + Pydantic v2 | Async, clean, great for OCR/rules |
| Worker | Celery + Redis | Proven async document processing |
| Database | PostgreSQL (Alembic migrations) | Production-standard relational store |
| Cache / queue | Redis | Job queue + rate limiting |
| OCR | Tesseract (PaddleOCR adapter stub) | Free, CPU-only, pluggable |
| Reports | ReportLab | Purpose-built PDF, not HTML-to-PDF |
| Observability | OpenTelemetry + Prometheus + Loki + Tempo + Grafana | Fully open-source |
| CI/CD | GitHub Actions | Lint, test, build, GHCR |

Everything is free and runs locally via Docker Compose.

## Quick start

```bash
cp .env.example .env
docker compose up --build
docker compose exec backend alembic upgrade head   # once db is healthy
docker compose exec backend python scripts/seed.py # optional: 6 demo documents
```

With the observability stack:

```bash
docker compose -f docker-compose.yml -f infra/docker-compose.obs.yml up --build
```

| Service | URL |
|---|---|
| Frontend | http://localhost:3000 |
| API docs | http://localhost:8000/docs |
| API health | http://localhost:8000/health |
| API metrics | http://localhost:8000/metrics |
| Grafana | http://localhost:3001 (admin / admin) |
| Prometheus | http://localhost:9090 |

Demo login after seeding: **demo@example.com / supersecret1**.
See [docs/DEMO.md](docs/DEMO.md) for a guided walkthrough.

## Tests

```bash
docker compose exec backend python -m pytest -q     # 38 tests
docker compose exec frontend npx tsc --noEmit
```

Unit (OCR, rules, scoring, report, security), integration (full pipeline, DB, real OCR),
and end-to-end on the 6 seeded sample documents.

## Screenshots

Add captures to `docs/screenshots/` — referenced here:

| | |
|---|---|
| Landing | `docs/screenshots/landing.png` |
| Processing | `docs/screenshots/processing.png` |
| Findings | `docs/screenshots/findings.png` |
| PDF report | `docs/screenshots/report.png` |
| Grafana | `docs/screenshots/grafana.png` |

## Trade-offs

- **Modular monolith + one worker**, not microservices/Kafka — right-sized for the scope.
- **Rule engine over an LLM** — explainable and free; every finding cites the clause.
  Ceiling: nuanced wording an LLM might catch is out of scope (see roadmap).
- **Tesseract** for OCR — light and free; a PaddleOCR adapter stub exists for harder layouts.
- **True-cost** sums stated currency amounts; percentages are shown but not compounded
  (no reliable principal). 
- **Local filesystem** storage with a retention sweep — swap for S3/MinIO to scale.
- One overview Grafana dashboard wired across all three signals (others are quick to add).

## Roadmap

- PaddleOCR for harder layouts · S3/MinIO storage · side-by-side document compare
- Browser-extension capture at checkout · multi-language OCR
- LLM-assisted explanations layered *on top of* (not replacing) the rule engine
- Split the worker into dedicated services if throughput grows

> Informational analysis only — not legal or financial advice.
