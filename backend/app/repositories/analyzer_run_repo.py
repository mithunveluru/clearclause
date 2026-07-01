from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import JobStatus
from app.models.analyzer_run import AnalyzerRun


class AnalyzerRunRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, document_id: int, analyzer_type: str) -> AnalyzerRun:
        run = AnalyzerRun(
            document_id=document_id,
            analyzer_type=analyzer_type,
            status=JobStatus.RUNNING,
            started_at=datetime.utcnow(),
        )
        self.db.add(run)
        await self.db.commit()
        await self.db.refresh(run)
        return run

    async def finish(
        self, run_id: int, status: str, result_json: dict | None, error: str | None = None
    ) -> None:
        await self.db.execute(
            update(AnalyzerRun)
            .where(AnalyzerRun.id == run_id)
            .values(
                status=status,
                result_json=result_json,
                error_message=(error[:1000] if error else None),
                finished_at=datetime.utcnow(),
            )
        )
        await self.db.commit()

    async def latest(self, document_id: int) -> AnalyzerRun | None:
        r = await self.db.execute(
            select(AnalyzerRun)
            .where(AnalyzerRun.document_id == document_id)
            .order_by(AnalyzerRun.id.desc())
            .limit(1)
        )
        return r.scalar_one_or_none()
