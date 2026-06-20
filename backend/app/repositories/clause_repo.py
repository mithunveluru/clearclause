from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.clause import Clause


class ClauseRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def replace_for_document(self, document_id: int, clauses: list[dict]) -> int:
        await self.db.execute(delete(Clause).where(Clause.document_id == document_id))
        self.db.add_all(
            Clause(
                document_id=document_id,
                clause_type=c["clause_type"],
                raw_text=c["raw_text"],
                normalized_text=c["normalized_text"],
                page_number=c["page_number"],
                section_name=c["section_name"],
            )
            for c in clauses
        )
        await self.db.commit()
        return len(clauses)

    async def list_for_document(self, document_id: int) -> list[Clause]:
        result = await self.db.execute(
            select(Clause)
            .where(Clause.document_id == document_id)
            .order_by(Clause.page_number, Clause.id)
        )
        return list(result.scalars().all())
