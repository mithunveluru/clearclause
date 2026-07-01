from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.finding import Finding


class FindingRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def replace_for_document(self, document_id: int, findings: list[dict]) -> int:
        await self.db.execute(delete(Finding).where(Finding.document_id == document_id))
        self.db.add_all(
            Finding(
                document_id=document_id,
                clause_id=f["clause_id"],
                issue_type=f["issue_type"],
                severity=f["severity"],
                confidence=f["confidence"],
                explanation=f["explanation"],
                impact=f.get("impact"),
                action_text=f["action_text"],
                document_family=f.get("document_family"),
                analyzer_type=f.get("analyzer_type"),
            )
            for f in findings
        )
        await self.db.commit()
        return len(findings)

    async def list_for_document(self, document_id: int) -> list[Finding]:
        result = await self.db.execute(
            select(Finding).where(Finding.document_id == document_id).order_by(Finding.id)
        )
        return list(result.scalars().all())

    async def list_with_clause_text(
        self, document_id: int
    ) -> list[tuple[Finding, str | None]]:
        """Single JOIN query — findings + their clause text in one round-trip."""
        from app.models.clause import Clause

        result = await self.db.execute(
            select(Finding, Clause.normalized_text)
            .outerjoin(Clause, Finding.clause_id == Clause.id)
            .where(Finding.document_id == document_id)
            .order_by(Finding.id)
        )
        return list(result.all())
