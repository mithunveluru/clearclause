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
                action_text=f["action_text"],
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
