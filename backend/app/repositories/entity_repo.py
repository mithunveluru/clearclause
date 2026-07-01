from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.contracts import Entity
from app.models.entity import DocumentEntity


class EntityRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def replace_for_document(self, document_id: int, entities: list[Entity]) -> int:
        await self.db.execute(
            delete(DocumentEntity).where(DocumentEntity.document_id == document_id)
        )
        self.db.add_all(
            DocumentEntity(
                document_id=document_id,
                entity_type=e.entity_type,
                entity_value=e.entity_value,
                confidence=e.confidence,
                page_number=e.page_number,
                source_text=e.source_text,
            )
            for e in entities
        )
        await self.db.commit()
        return len(entities)

    async def list_for_document(self, document_id: int) -> list[DocumentEntity]:
        r = await self.db.execute(
            select(DocumentEntity)
            .where(DocumentEntity.document_id == document_id)
            .order_by(DocumentEntity.id)
        )
        return list(r.scalars().all())
