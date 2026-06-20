from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.extracted_block import ExtractedBlock


class ExtractedBlockRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def replace_for_document(self, document_id: int, blocks: list[dict]) -> int:
        """Idempotent: clear any prior blocks, then insert the new set."""
        await self.db.execute(
            delete(ExtractedBlock).where(ExtractedBlock.document_id == document_id)
        )
        self.db.add_all(
            ExtractedBlock(
                document_id=document_id,
                page_number=b["page_number"],
                block_order=b["block_order"],
                text=b["text"],
                bbox_json=b.get("bbox"),
            )
            for b in blocks
        )
        await self.db.commit()
        return len(blocks)

    async def list_for_document(self, document_id: int) -> list[ExtractedBlock]:
        result = await self.db.execute(
            select(ExtractedBlock)
            .where(ExtractedBlock.document_id == document_id)
            .order_by(ExtractedBlock.page_number, ExtractedBlock.block_order)
        )
        return list(result.scalars().all())
