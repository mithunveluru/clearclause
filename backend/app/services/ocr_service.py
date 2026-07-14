import asyncio
import logging
import statistics

from app.core import storage
from app.core.config import settings
from app.metrics import count_degraded
from app.models.document import Document
from app.ocr import OCRProvider, get_ocr_provider
from app.repositories.block_repo import ExtractedBlockRepository
from app.repositories.document_repo import DocumentRepository

logger = logging.getLogger(__name__)


class OCRService:
    def __init__(
        self,
        blocks: ExtractedBlockRepository,
        documents: DocumentRepository | None = None,
        provider: OCRProvider | None = None,
        store: storage.Storage | None = None,
    ):
        self.blocks = blocks
        self.documents = documents
        self.provider = provider or get_ocr_provider()
        self.store = store or storage.get_storage()

    async def process(self, document: Document) -> int:
        """OCR the document's file and persist its blocks. Returns block count."""

        def read() -> list[dict]:
            # Temp copy; plaintext must not outlive the task
            with self.store.local_path(document.file_path) as path:
                return self.provider.extract(path)

        # CPU-bound; keep the event loop free
        blocks = await asyncio.to_thread(read)

        confidence = self._mean_confidence(blocks)
        if confidence is not None and confidence < settings.OCR_LOW_CONFIDENCE:
            # Garbled text yields no findings, so reads "clean"
            count_degraded("low_ocr_confidence")
            logger.warning(
                "document %s: low OCR confidence %.0f — analysis may be incomplete",
                document.id,
                confidence,
            )
        if self.documents is not None:
            await self.documents.set_ocr_confidence(document.id, confidence)

        return await self.blocks.replace_for_document(document.id, blocks)

    @staticmethod
    def _mean_confidence(blocks: list[dict]) -> float | None:
        scores = [b["confidence"] for b in blocks if b.get("confidence") is not None]
        return statistics.mean(scores) if scores else None
