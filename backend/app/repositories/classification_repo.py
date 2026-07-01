from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.contracts import ClassificationResult
from app.models.classification import DocumentClassification


class ClassificationRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def save(self, document_id: int, result: ClassificationResult) -> None:
        await self.db.execute(
            delete(DocumentClassification).where(
                DocumentClassification.document_id == document_id
            )
        )
        self.db.add(
            DocumentClassification(
                document_id=document_id,
                classified_type=result.classified_type,
                document_family=result.document_family,
                confidence=result.confidence,
                signals_json=result.signals,
                candidates_json=[c.model_dump() for c in result.secondary_candidates],
                routing_action=result.routing_action,
            )
        )
        await self.db.commit()

    async def override(
        self,
        document_id: int,
        classified_type: str,
        document_family: str | None,
    ) -> None:
        """User-initiated type override. Sets routing_action='auto' (user is the authority)."""
        await self.db.execute(
            update(DocumentClassification)
            .where(DocumentClassification.document_id == document_id)
            .values(
                classified_type=classified_type,
                document_family=document_family,
                routing_action="auto",
            )
        )
        await self.db.commit()

    async def get(self, document_id: int) -> DocumentClassification | None:
        r = await self.db.execute(
            select(DocumentClassification).where(
                DocumentClassification.document_id == document_id
            )
        )
        return r.scalar_one_or_none()
