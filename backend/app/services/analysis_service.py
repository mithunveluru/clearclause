from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import DocStatus
from app.telemetry import get_tracer
from app.repositories.block_repo import ExtractedBlockRepository
from app.repositories.classification_repo import ClassificationRepository
from app.repositories.clause_repo import ClauseRepository
from app.repositories.document_repo import DocumentRepository
from app.repositories.finding_repo import FindingRepository
from app.repositories.report_repo import ReportRepository
from app.repositories.score_repo import ScoreRepository
from app.services.classification_service import ClassificationService
from app.services.detection_service import DetectionService
from app.services.ocr_service import OCRService
from app.services.report_service import ReportService
from app.services.scoring_service import ScoringService
from app.services.segmentation_service import SegmentationService


class AnalysisService:
    """Runs the full pipeline for one document, updating status as it goes."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.docs = DocumentRepository(db)
        self.tracer = get_tracer("clearclause.analysis")

    async def run(self, document_id: int, user_id: int) -> str:
        doc = await self.docs.get_for_user(document_id, user_id)
        if doc is None:
            raise ValueError("Document not found")
        try:
            await self.docs.update_status(document_id, DocStatus.OCR_PROCESSING)
            with self.tracer.start_as_current_span("ocr"):
                await OCRService(ExtractedBlockRepository(self.db)).process(doc)
            await self.docs.update_status(document_id, DocStatus.OCR_DONE)

            # Selects the analyzer that runs next
            with self.tracer.start_as_current_span("classification"):
                await ClassificationService(
                    ExtractedBlockRepository(self.db),
                    self.docs,
                    ClassificationRepository(self.db),
                ).process(document_id)

            await self.docs.update_status(document_id, DocStatus.ANALYSIS_PROCESSING)
            with self.tracer.start_as_current_span("segmentation"):
                await SegmentationService(
                    ExtractedBlockRepository(self.db), ClauseRepository(self.db)
                ).process(document_id)
            with self.tracer.start_as_current_span("detection"):
                await DetectionService(
                    ClauseRepository(self.db), FindingRepository(self.db)
                ).process(document_id)
            with self.tracer.start_as_current_span("scoring"):
                await ScoringService(
                    ClauseRepository(self.db),
                    FindingRepository(self.db),
                    ScoreRepository(self.db),
                ).process(document_id)
            await self.docs.update_status(document_id, DocStatus.ANALYSIS_DONE)

            with self.tracer.start_as_current_span("report"):
                await ReportService(
                    self.docs,
                    ClauseRepository(self.db),
                    FindingRepository(self.db),
                    ScoreRepository(self.db),
                    ReportRepository(self.db),
                ).process(document_id, user_id)
            await self.docs.update_status(document_id, DocStatus.REPORT_READY)
            return DocStatus.REPORT_READY
        except Exception:
            await self.docs.update_status(document_id, DocStatus.FAILED)
            raise
