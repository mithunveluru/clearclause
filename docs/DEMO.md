# ClearClause — Demo Script

A ~5-minute guided walkthrough. Assumes the stack is running and seeded.

## Setup (one time)

```bash
cp .env.example .env
docker compose -f docker-compose.yml -f infra/docker-compose.obs.yml up --build -d
docker compose exec backend alembic upgrade head
docker compose exec backend python scripts/seed.py
```

Open http://localhost:3000 and log in as **demo@example.com / supersecret1**.

## Walkthrough

1. **Landing** — lead with trust: the value proposition, "what we check," how it works,
   and the privacy/explainability promises. Click **See a real analysis** to show the
   findings experience without uploading anything.

2. **Upload (the centerpiece)** — from the workspace, drop a document (e.g. render any
   `sample-data/*.txt`, or use a real loan PDF). Note there is **no Analyze button** —
   analysis starts automatically and you're taken straight to the live processing view.

3. **Processing experience** — the stage list advances with the worker: Document received →
   Reading the pages → Understanding it → Reviewing the clauses → Compiling your report.
   Each step maps to a real pipeline status, so a slow document visibly sits on the stage
   it is actually on. A failed run offers **Try again**, which re-runs the full analysis.

4. **Results** — the risk score and band, the plain-English summary, and the section nav.
   Open a finding: *what it means · why it matters · recommended action*. Expand
   **Exact wording** for the quoted clause, or **Open page N** to jump into the original
   document at the cited page.

5. **True cost & categories** — the side rail shows extracted fees and the estimated true
   cost, plus the weighted category breakdown. Search the document from the sidebar —
   "deposit" or "late fee" — to pull matches from clauses, figures, dates and questions
   at once.

6. **PDF report** — click **Download PDF report** for the purpose-built auditor-style PDF
   (cover, executive summary, clause analysis, cost impact, recommended actions, appendix).

7. **Observability** (the engineering story) — open Grafana at http://localhost:3001:
   - Request rate / latency / errors from the API `/metrics`
   - Worker logs streaming into Loki
   - A full distributed trace (API → Celery task → OCR/segmentation/detection/report spans)
     in Tempo. Pick a failed document and debug it from logs + traces alone.

## Talking points

- **Explainable, not a black box** — every finding cites the exact clause; no LLM verdicts.
- **Async by design** — upload returns instantly; the worker does the heavy lifting with
  retries and status tracking.
- **Production-shaped** — migrations, service/repository separation, JWT + rate limiting +
  log redaction, 38 tests, CI/CD, and full traces/metrics/logs.

## Reset

```bash
# remove demo documents from the workspace via the UI, or wipe everything:
docker compose down -v && docker compose up -d && docker compose exec backend alembic upgrade head
```
