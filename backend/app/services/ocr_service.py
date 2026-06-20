import asyncio

from app.models.document import Document
from app.ocr import OCRProvider, get_ocr_provider
from app.repositories.block_repo import ExtractedBlockRepository


class OCRService:
    def __init__(self, blocks: ExtractedBlockRepository, provider: OCRProvider | None = None):
        self.blocks = blocks
        self.provider = provider or get_ocr_provider()

    async def process(self, document: Document) -> int:
        """OCR the document's file and persist its blocks. Returns block count."""
        # extract() is CPU-bound and blocking; keep the event loop free.
        blocks = await asyncio.to_thread(self.provider.extract, document.file_path)
        return await self.blocks.replace_for_document(document.id, blocks)
