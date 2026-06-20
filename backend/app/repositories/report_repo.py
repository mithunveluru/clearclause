from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.report import Report


class ReportRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def save(self, document_id: int, summary_json: dict, html_path: str) -> Report:
        await self.db.execute(delete(Report).where(Report.document_id == document_id))
        report = Report(
            document_id=document_id, summary_json=summary_json, html_path=html_path
        )
        self.db.add(report)
        await self.db.commit()
        await self.db.refresh(report)
        return report

    async def get(self, document_id: int) -> Report | None:
        r = await self.db.execute(select(Report).where(Report.document_id == document_id))
        return r.scalar_one_or_none()
