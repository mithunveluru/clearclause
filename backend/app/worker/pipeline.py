"""Staged pipeline: each stage is its own retry-safe, idempotent Celery task,
wired into a chain across queues.

Idempotency: every stage's repository writes are replace-by-document, so a retry
or reprocess reproduces the same state. Status + an OTel span are written per stage;
on failure the document is marked failed and the chain stops.
"""
import asyncio
import logging
import time
from collections.abc import Awaitable, Callable

from celery import chain
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings
from app.core.constants import DocStatus
from app.metrics import record_stage
from app.repositories.block_repo import ExtractedBlockRepository
from app.repositories.classification_repo import ClassificationRepository
from app.repositories.clause_repo import ClauseRepository
from app.repositories.analyzer_run_repo import AnalyzerRunRepository
from app.repositories.document_repo import DocumentRepository
from app.repositories.entity_repo import EntityRepository
from app.repositories.finding_repo import FindingRepository
from app.repositories.report_repo import ReportRepository
from app.repositories.score_repo import ScoreRepository
from app.repositories.ai_output_repo import AIOutputRepository
from app.repositories.chunk_repo import ChunkRepository
from app.services.ai_summary_service import AISummaryService
from app.services.analyzer_service import AnalyzerService
from app.services.chunk_service import ChunkService
from app.services.classification_service import ClassificationService
from app.services.embed_service import EmbedService
from app.services.ocr_service import OCRService
from app.services.report_service import ReportService
from app.services.scoring_service import ScoringService
from app.services.segmentation_service import SegmentationService
from app.telemetry import get_tracer
from app.worker.celery_app import celery_app

_RETRY = dict(bind=True, autoretry_for=(Exception,), max_retries=2, retry_backoff=True)


def _session():
    engine = create_async_engine(settings.DATABASE_URL)
    return engine, async_sessionmaker(engine, expire_on_commit=False)


async def _mark_failed(document_id: int) -> None:
    engine, Session = _session()
    try:
        async with Session() as db:
            await DocumentRepository(db).update_status(document_id, DocStatus.FAILED)
    finally:
        await engine.dispose()


async def _run_stage(
    document_id: int,
    span: str,
    work: Callable[[AsyncSession], Awaitable[None]],
    status_before: str | None = None,
    status_after: str | None = None,
) -> None:
    engine, Session = _session()
    start = time.perf_counter()
    try:
        async with Session() as db:
            docs = DocumentRepository(db)
            if status_before:
                await docs.update_status(document_id, status_before)
            with get_tracer("clearclause.stage").start_as_current_span(span):
                await work(db)
            if status_after:
                await docs.update_status(document_id, status_after)
    except Exception:
        await _mark_failed(document_id)
        raise
    finally:
        record_stage(span, time.perf_counter() - start)
        await engine.dispose()


@celery_app.task(name="stage.ocr", **_RETRY)
def ocr_task(self, document_id: int, user_id: int) -> None:
    async def work(db: AsyncSession) -> None:
        doc = await DocumentRepository(db).get_for_user(document_id, user_id)
        if doc is None:
            raise ValueError(f"document {document_id} not found")
        await OCRService(ExtractedBlockRepository(db), DocumentRepository(db)).process(doc)

    asyncio.run(_run_stage(document_id, "ocr", work, DocStatus.OCR_PROCESSING, DocStatus.OCR_DONE))


@celery_app.task(name="stage.classify", **_RETRY)
def classify_task(self, document_id: int) -> None:
    async def work(db: AsyncSession) -> None:
        await ClassificationService(
            ExtractedBlockRepository(db), DocumentRepository(db), ClassificationRepository(db)
        ).process(document_id)

    asyncio.run(_run_stage(document_id, "classification", work))


@celery_app.task(name="stage.segment", **_RETRY)
def segment_task(self, document_id: int) -> None:
    async def work(db: AsyncSession) -> None:
        await SegmentationService(
            ExtractedBlockRepository(db), ClauseRepository(db)
        ).process(document_id)

    asyncio.run(_run_stage(document_id, "segmentation", work, DocStatus.ANALYSIS_PROCESSING))


@celery_app.task(name="stage.analyze", **_RETRY)
def analyze_task(self, document_id: int) -> None:
    async def work(db: AsyncSession) -> None:
        await AnalyzerService(
            DocumentRepository(db), ClauseRepository(db), FindingRepository(db),
            EntityRepository(db), AnalyzerRunRepository(db),
        ).process(document_id)

    asyncio.run(_run_stage(document_id, "analyze", work))


@celery_app.task(name="stage.score", **_RETRY)
def score_task(self, document_id: int) -> None:
    async def work(db: AsyncSession) -> None:
        await ScoringService(
            ClauseRepository(db), FindingRepository(db), ScoreRepository(db),
            AnalyzerRunRepository(db),
        ).process(document_id)

    asyncio.run(_run_stage(document_id, "scoring", work, status_after=DocStatus.ANALYSIS_DONE))


async def _run_soft_stage(
    document_id: int, span: str, work: Callable[[AsyncSession], Awaitable[None]]
) -> None:
    """For optional AI stages: never fail the document — log and move on so a
    down Ollama/Qdrant leaves the (already report_ready) document intact."""
    engine, Session = _session()
    start = time.perf_counter()
    try:
        async with Session() as db:
            with get_tracer("clearclause.stage").start_as_current_span(span):
                await work(db)
    except Exception as e:  # noqa: BLE001 — graceful degradation is the point
        logging.getLogger("clearclause").warning(
            "AI stage %s skipped for document %s: %s", span, document_id, e
        )
    finally:
        record_stage(span, time.perf_counter() - start)
        await engine.dispose()


@celery_app.task(name="stage.chunk", **_RETRY)
def chunk_task(self, document_id: int) -> None:
    async def work(db: AsyncSession) -> None:
        await ChunkService(ClauseRepository(db), ChunkRepository(db)).process(document_id)

    asyncio.run(_run_soft_stage(document_id, "chunk", work))


@celery_app.task(name="stage.embed", **_RETRY)
def embed_task(self, document_id: int) -> None:
    async def work(db: AsyncSession) -> None:
        await EmbedService(
            ChunkRepository(db),
            DocumentRepository(db),
            classifications=ClassificationRepository(db),
            findings=FindingRepository(db),
        ).process(document_id)

    asyncio.run(_run_soft_stage(document_id, "embed", work))


@celery_app.task(name="stage.ai_summary", **_RETRY)
def ai_summary_task(self, document_id: int) -> None:
    async def work(db: AsyncSession) -> None:
        await AISummaryService(
            DocumentRepository(db), FindingRepository(db), ScoreRepository(db),
            EntityRepository(db), AIOutputRepository(db),
        ).process(document_id)

    asyncio.run(_run_soft_stage(document_id, "ai_summary", work))


@celery_app.task(name="stage.report", **_RETRY)
def report_task(self, document_id: int, user_id: int) -> None:
    async def work(db: AsyncSession) -> None:
        await ReportService(
            DocumentRepository(db), ClauseRepository(db), FindingRepository(db),
            ScoreRepository(db), ReportRepository(db),
        ).process(document_id, user_id)

    asyncio.run(_run_stage(document_id, "report", work, status_after=DocStatus.REPORT_READY))


def build_chain(document_id: int, user_id: int):
    steps = [
        ocr_task.si(document_id, user_id),
        classify_task.si(document_id),
        segment_task.si(document_id),
        analyze_task.si(document_id),
        score_task.si(document_id),
        report_task.si(document_id, user_id),
    ]
    # RAG indexing only in full AI mode (needed for Q&A).
    if settings.AI_MODE == "full":
        steps += [chunk_task.si(document_id), embed_task.si(document_id)]
    # AI summary in summary_only + full.
    if settings.AI_MODE in ("summary_only", "full"):
        steps += [ai_summary_task.si(document_id)]
    return chain(*steps)


def dispatch(document_id: int, user_id: int) -> str:
    """Entry point for upload / analyze / reprocess."""
    build_chain(document_id, user_id).apply_async()
    return "staged"
