# ClearClause V2/V3 — Document Risk Intelligence Platform: Plan

Status: **COMPLETE — P0–P10 shipped & verified.** All V2/V3 phases landed incrementally
on V1 with backward-compatible migrations; V1 regression suite stayed green throughout.

### Delivered (P0–P10)
- P0 safety net (v1_regression markers, PIPELINE flag) · P1 data + Pydantic contracts (migration 0009)
- P2 rule-based classification (8 types) · P3 staged Celery pipeline across queues (idempotent, retry-safe)
- P4 analyzer/entity framework (loan/subscription wrap V1 rules — parity) · P5 rental vertical slice
- P6 RAG (section chunker, Ollama embeddings, Qdrant + metadata filter, retriever)
- P7 grounded AI summaries (AI_MODE gating, ai_outputs cache, no-hallucination prompts)
- P8 grounded Q&A (retrieve→ground→cite, refuses on empty) · P9 patta / sale_deed / credit_card analyzers
- P10 metrics + dashboards (doc-type distribution, stage/analyzer/AI latency) + docs
- Endpoints: classification, entities, analysis, ai-summary, qa, reprocess. 58 backend tests green.
- AI fully optional (off|summary_only|full); core stack runs AI-off on low-resource machines.



## 0. Decisions — LOCKED
- AI layer = **`app/ai/` module in backend**, invoked by worker `ai_queue` tasks (not a separate FastAPI service). Ollama + Qdrant remain separate containers in the `ai` profile.
- Embeddings = **Ollama `nomic-embed-text`**.
- Sequencing = **rental_contract vertical slice first**, then fan out patta / sale_deed / credit_card.

### Original fork analysis (for the record)

1. **ai-service: separate FastAPI microservice vs module in backend.**
   Recommendation: **`app/ai/` module inside backend, invoked by worker `ai_queue` tasks**
   that call Ollama over HTTP. Rationale: Ollama and Qdrant are the real separate
   services; a third FastAPI just to wrap `httpx → ollama` adds ops/build surface for no
   isolation we actually need, and `AI_MODE` gating is trivial in-process. Fully reversible
   (the module has a clean interface and could be lifted into a service later). The spec's
   literal "ai-service" is honored as a logical layer, not a separate container.
2. **Embedding model:** Ollama `nomic-embed-text` (one AI runtime) vs `fastembed` (ONNX,
   no torch, in-process). Recommendation: **`nomic-embed-text` via Ollama** — keeps a single
   local AI runtime under one profile; fastembed is the fallback if Ollama embeddings are slow.
3. **Sequencing:** build all four new analyzers before V3, or take **one vertical slice**
   (rental_contract) through the *entire* new pipeline incl. classification → entities →
   analyzer → score → chunk → embed → AI summary → grounded Q&A first, then fan out the
   other analyzers? Recommendation: **vertical slice first** — proves every new seam once,
   de-risks the architecture, then the remaining analyzers are repetitive fill-in.

Default if no response: module-in-backend, nomic-embed-text, vertical-slice (rental).

---

## 1. Current repo map (verified)

**Backend** (`backend/app/`, FastAPI modular monolith):
- `api/` — `auth`, `documents`, `analysis` (findings/score/report/analyze), `health`, `deps`
- `services/` — per-stage services + **`AnalysisService`** (orchestrator)
- `repositories/`, `models/` (user, document, job, extracted_block, clause, finding, score=risk+cost, report)
- `detection/` (rules + engine — loan/subscription, 12 categories), `ocr/` (base, tesseract, paddle stub, factory),
  `segmentation/`, `scoring/` (risk + cost), `reporting/` (builder + pdf + render)
- `core/` (config, security, ratelimit, redis, logredact, files, constants), `worker/` (celery_app + tasks), `telemetry.py`

**Pipeline (V1):** `POST /documents/upload` → `run_analysis.delay` → `AnalysisService.run()` runs
**inline** stages with OTel spans: OCR → segmentation → detection → scoring → report; updates
`documents.status` (uploaded→ocr_*→analysis_*→report_ready/failed). **Single Celery task, one default queue.**

**Frontend** (`frontend/`, Next App Router): landing, login, register, dashboard, `documents/[id]`,
sample; `components/` (+ `ui/`), `lib/api.ts`, `lib/ui.ts`.

**Infra:** Postgres + Redis (core compose); OTel Collector → Tempo/Loki/Prometheus → Grafana (obs compose).
8 Alembic migrations. 38 tests. Reports = ReportLab PDF.

**Where things live:** loan/subscription rules → `detection/rules.py`; upload → `api/v1/documents.py`;
scoring → `scoring/`; results UI → `app/documents/[id]/page.tsx` + `FindingsTimeline`/`RiskMeter`/`CostBreakdown`.

---

## 2. Risk assessment & safety net

**Critical flows that must keep working:** register/login (JWT, rate limit); upload → auto-analyze
→ report_ready; `/findings` `/score` `/report` (PDF); dashboard list; ownership 404s; log redaction.

**Existing safety net:** 38 tests including pipeline integration + 6-sample e2e + DB/OCR integration.
These already act as V1 characterization tests. **Action:** mark them with a `v1_regression` pytest
marker and keep them green at every checkpoint (CI already runs them).

**Risky refactor points (highest first):**
- Worker pipeline: single task → staged chain across queues. *Mitigation:* keep `AnalysisService`
  stage methods as the task bodies; add a feature flag `PIPELINE=legacy|staged` so we can flip back.
- `documents` column additions + status-flow expansion. *Mitigation:* additive nullable columns,
  superset of statuses.
- Auto-enqueue point in `documents.py`. *Mitigation:* swap `run_analysis.delay` → chain head, one line.

**Safe-first modules (no V1 impact until wired):** `classification/`, `entities/`, `analysis/analyzers/`,
`rag/`, `ai/`, new tables. Build and unit-test in isolation, wire into the pipeline last.

**Migrations:** all **additive & backward-compatible**. New tables; new **nullable** columns
(`documents.classified_type`, `analysis_version` default 1, `qa_ready`/`ai_summary_ready` default false;
`findings.document_family`/`analyzer_type` nullable). **No backfill required** — existing rows stay valid
(treated as `analysis_version=1`, classified_type inferred lazily or left null).

---

## 3. Target repo structure (additions only)

```
backend/app/
  classification/      classifier.py (rule-based) + base.py (DocumentClassifier protocol)
  entities/            base.py (EntityExtractor) + extractors/{loan,subscription,credit_card,
                       patta,rental,sale_deed}.py + registry.py
  analysis/
    base.py            BaseAnalyzer (typed contract)
    registry.py        classified_type -> analyzer
    analyzers/         loan.py, subscription.py, credit_card.py, patta.py, rental.py, sale_deed.py
  risk/                generic weighted scorer reused across analyzers (wraps current scoring/)
  rag/                 chunker.py, embeddings.py (Ollama), store.py (Qdrant), retriever.py
  ai/                  client.py (Ollama), explainer.py, summarizer.py, qa.py, report_writer.py,
                       prompts.py, modes.py (AI_MODE gating)
  contracts/           pydantic models shared across stages (ClassificationResult, Entity,
                       AnalyzerResult, Chunk, Citation, QAAnswer, AIOutput)
  models/              + classification.py, entity.py, analyzer_run.py, chunk.py, ai_output.py
  worker/tasks/        ocr.py, classify.py, extract.py, analyze.py, score.py, report.py,
                       chunk_embed.py, ai.py  (chain wired in pipeline.py)
```
Frontend gains type-specific result sections + AI panels + Q&A (see §10). New `ai-service`/`ollama`/
`qdrant` live in an **`ai` compose profile**; core profile unchanged.

---

## 4. Database migration plan (additive)

New tables (all FK `document_id` ON DELETE CASCADE, indexed):
- `document_classifications` (id, document_id, classified_type, confidence, signals_json, created_at)
- `document_entities` (id, document_id, entity_type, entity_value, confidence, page_number, source_text, created_at)
- `analyzer_runs` (id, document_id, analyzer_type, status, error_message, result_json, started_at, finished_at)
- `document_chunks` (id, document_id, chunk_index, page_number, section_name, chunk_text, vector_id, embedding_provider, created_at)
- `ai_outputs` (id, document_id, kind[explanation|summary|qa|report], finding_id?, input_hash, content, model, created_at)

Column adds:
- `documents`: `classified_type` (nullable), `analysis_version` (int, default 1), `qa_ready` (bool default false), `ai_summary_ready` (bool default false), `document_family` (nullable: consumer|property)
- `findings`: `document_family` (nullable), `analyzer_type` (nullable)  ← lets findings span analyzers

One migration `0009_v2_v3_core` (tables + columns). Reversible. No data backfill.

---

## 5. Backend contracts (Pydantic, in `contracts/`)

```
ClassificationResult(classified_type, document_family, confidence, signals: dict)
Entity(entity_type, entity_value, confidence, page_number?, source_text?)
Finding(issue_type, severity, confidence, explanation, impact, action_text, clause_ref?)  # reuse shape
AnalyzerResult(analyzer_type, entities: list[Entity], findings: list[Finding],
               sub_scores: dict, headline_metric: {name,value,band}, strengths, recommendations)
Chunk(chunk_index, page_number?, section_name?, text)
Citation(page?, section?, snippet)
QAAnswer(answer, citations: list[Citation], confidence_note)
AIOutput(kind, content, model, grounded_on: list[str])
```
Stage interfaces (Protocols): `DocumentClassifier.classify(text)->ClassificationResult`;
`EntityExtractor.extract(text, pages)->list[Entity]`; `BaseAnalyzer.analyze(ctx)->AnalyzerResult`;
`RiskScorer.score(findings, ctx)->ScoreResult`; `Chunker.chunk(blocks)->list[Chunk]`;
`Retriever.search(document_id, query, filters)->list[Chunk]`; `AIExplainer/AISummarizer/AIReportWriter`.
The existing loan/subscription detection becomes `analyzers/loan.py` + `subscription.py` wrapping
**today's `detection/rules.py` unchanged** (no rewrite of working rules).

---

## 6. Analyzer-by-analyzer design

Each analyzer = entity extractor (regex/keyword, deterministic) + findings rules (presence/threshold)
+ headline metric (the "health/fairness/transparency score"). All reuse the generic weighted
`RiskScorer`. Detection = "missing/!threshold → severity", per the spec lists:
- **loan / subscription** — wrap existing rules; add entity extraction for fee amounts.
- **credit_card** — entities: annual_fee, late_fee, interest_rate, billing_cycle, min_due, reward_expiry,
  overlimit_fee, cash_advance_fee → Card Terms Transparency Score.
- **patta** — entities: owner_name, survey_number, village, taluk, district, patta_number,
  land_classification, extent, subdivision_number, boundary_description → Patta Health Score;
  findings on missing fields (severities per spec; ownership-mismatch placeholder = critical).
- **rental_contract** — landlord/tenant, rent, deposit, duration, notice, termination, maintenance,
  rent-increase, lock-in → Rental Fairness Score + negotiation checklist.
- **sale_deed** — buyer/seller, property desc, survey_number, advance, consideration, registration/
  possession dates, refund/penalty/warranty/encumbrance → Sale Agreement Risk Score + checklists.

Output shape is uniform (`AnalyzerResult`) so frontend + report render generically with
type-specific labels. Headline metric stored in `risk_scores` (reuse) or `analyzer_runs.result_json`.

## 7. AI / RAG design

- **Ollama** container (`ai` profile), `qwen3:8b` primary, `gemma3:4b` fallback; `OLLAMA_BASE_URL`.
- **`ai/modes.py`**: `AI_MODE=off` → AI stages skipped, `qa_ready=false`, reports = deterministic only;
  `summary_only` → explanations+summary, no Q&A index; `full` → + chunking/embedding/Q&A.
- **Explainer/Summarizer/ReportWriter**: prompts built **only** from extracted entities + findings +
  score + top clauses; system prompt forbids new facts; outputs stored in `ai_outputs` (cached by input_hash).
- **RAG**: `Chunker` chunks by section else bounded windows (preserve page/section); `embeddings.py`
  → Ollama `nomic-embed-text`; `store.py` → **Qdrant** (one collection, payload `{document_id, page,
  section, analyzer_type}`); `retriever.py` filters by `document_id` (+ optional page/section).
- **Q&A flow**: question → retrieve top-k chunks (+ relevant findings) → grounded prompt → LLM →
  `QAAnswer{answer, citations[], confidence_note}`; refuses when retrieval is empty/low-signal.
- **Qdrant chosen** over Chroma: first-class metadata filtering (needed for `document_id`/page/section),
  runs as a lightweight container, stable API. No existing Chroma usage to favor.

## 8. API plan (additive, all ownership-checked)

`GET /documents/{id}/classification`, `/entities`, `/analysis`, `/ai-summary`;
`POST /documents/{id}/qa` (body `{question}` → `{answer, citations[], confidence_note}`);
`POST /documents/{id}/reprocess` (re-runs pipeline, bumps `analysis_version`).
Existing `/findings` `/score` `/report` stay (findings now carry analyzer_type). 404 if AI disabled
on AI endpoints (or 200 with `ai_disabled` note for graceful degrade).

## 9. Frontend plan (extend, not rebuild)

Reuse design system. Add: **document-type badge** + **classification panel**, **entities section**,
**analyzer-specific result sections** (Patta ownership/land; Rental fairness+risks; Sale-deed legal
checklist; Credit-card fee transparency), **AI summary panel**, **Q&A chat panel** with source-linked
citations, **dashboard filters** by family/type. All gated on capability flags from the API so AI-off
hides AI panels cleanly. Reuse `FindingsTimeline` (now generic), `RiskMeter` (headline metric).

## 10. Observability plan

New spans/metrics: classification latency, entity-extraction latency, analyzer selection +
failures-by-type, AI request latency, embedding latency, retrieval latency, Q&A latency, queue depth
by stage, document-type distribution (counter by classified_type). Dashboards: pipeline throughput,
doc-type distribution, analyzer performance by type, AI latency/failures, retrieval/Q&A signals.
Reuse existing OTel setup; queue depth via Celery/Redis metrics.

## 11. Test plan

- **Unit:** classifier rules, each entity extractor, each analyzer's findings, scoring, chunker,
  prompt builders. **Grounding:** Q&A refuses unsupported Qs; explanations/summaries only use
  findings/entities/score (assert no external facts via mocked model echoing its prompt).
- **Integration:** OCR→classify, classify→extract, extract→analyze, analyze→score, chunk→embed→
  retrieve (Qdrant), AI summary with **mocked** Ollama.
- **E2E:** patta, rental, sale_deed, credit_card full flows on new sample docs; **V1 regression**
  (loans/subscriptions) stays green.
- AI tests mock the model by default (no Ollama needed in CI); a marked `ai_live` suite can run
  against a real Ollama locally.

## 12. Execution order with checkpoints

- **P0 Safety:** mark v1_regression tests; add `PIPELINE` flag scaffolding. ✅ when V1 tests green.
- **P1 Data+contracts:** migration 0009, models, `contracts/`. ✅ migrate up/down clean, tests green.
- **P2 Classification:** classifier + table + stage + API + badge. ✅ classify 6 sample types.
- **P3 Staged worker:** refactor pipeline into Celery chain across queues (OCR/analysis/ai/report),
  idempotent + status; wrap existing services. ✅ V1 e2e green on staged path.
- **P4 Entities + analyzer framework:** BaseAnalyzer, registry, wrap loan/subscription. ✅ V1 parity.
- **P5 Vertical slice (rental):** rental extractor+analyzer+score+entities API+UI section. ✅ rental e2e.
- **P6 RAG:** chunker, Qdrant, embeddings, retriever + chunk/embed stages (full mode). ✅ retrieval test.
- **P7 AI:** explainer/summarizer/report-writer + ai stages + AI panels; AI_MODE gating. ✅ grounding tests.
- **P8 Q&A:** retrieve→LLM→cited answer + chat UI. ✅ Q&A grounding + refusal tests.
- **P9 Fan-out analyzers:** patta, sale_deed, credit_card (repeat P5 pattern). ✅ each e2e.
- **P10 Obs + dashboards + compose profiles + docs.** ✅ dashboards show new signals; core profile AI-off runs.

Each phase: summary, files changed, verify commands, follow-ups, behavior changes, suggested commit.
