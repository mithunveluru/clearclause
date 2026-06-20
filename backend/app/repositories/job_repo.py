from datetime import datetime

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import JobStatus
from app.models.document import Job


class JobRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, document_id: int, job_type: str) -> Job:
        job = Job(
            document_id=document_id,
            job_type=job_type,
            status=JobStatus.RUNNING,
            started_at=datetime.utcnow(),
        )
        self.db.add(job)
        await self.db.commit()
        await self.db.refresh(job)
        return job

    async def mark_done(self, job_id: int) -> None:
        await self._finish(job_id, JobStatus.DONE, None)

    async def mark_failed(self, job_id: int, error: str) -> None:
        await self._finish(job_id, JobStatus.FAILED, error[:1000])

    async def _finish(self, job_id: int, status: str, error: str | None) -> None:
        await self.db.execute(
            update(Job)
            .where(Job.id == job_id)
            .values(status=status, error_message=error, finished_at=datetime.utcnow())
        )
        await self.db.commit()
