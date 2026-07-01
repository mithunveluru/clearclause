from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.contracts import Chunk
from app.models.chunk import DocumentChunk


class ChunkRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def replace_for_document(self, document_id: int, chunks: list[Chunk]) -> int:
        await self.db.execute(
            delete(DocumentChunk).where(DocumentChunk.document_id == document_id)
        )
        self.db.add_all(
            DocumentChunk(
                document_id=document_id,
                chunk_index=c.chunk_index,
                page_number=c.page_number,
                section_name=c.section_name,
                chunk_text=c.text,
            )
            for c in chunks
        )
        await self.db.commit()
        return len(chunks)

    async def list_for_document(self, document_id: int) -> list[DocumentChunk]:
        r = await self.db.execute(
            select(DocumentChunk)
            .where(DocumentChunk.document_id == document_id)
            .order_by(DocumentChunk.chunk_index)
        )
        return list(r.scalars().all())

    async def set_vector(self, chunk_id: int, vector_id: str, provider: str) -> None:
        await self.db.execute(
            update(DocumentChunk)
            .where(DocumentChunk.id == chunk_id)
            .values(vector_id=vector_id, embedding_provider=provider)
        )
        await self.db.commit()
