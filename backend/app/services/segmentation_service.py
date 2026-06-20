from app.repositories.block_repo import ExtractedBlockRepository
from app.repositories.clause_repo import ClauseRepository
from app.segmentation import segment


class SegmentationService:
    def __init__(self, blocks: ExtractedBlockRepository, clauses: ClauseRepository):
        self.blocks = blocks
        self.clauses = clauses

    async def process(self, document_id: int) -> int:
        rows = await self.blocks.list_for_document(document_id)
        pairs = [(b.page_number, b.text) for b in rows]
        clauses = segment(pairs)
        return await self.clauses.replace_for_document(document_id, clauses)
