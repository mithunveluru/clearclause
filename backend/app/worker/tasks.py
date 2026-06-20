import asyncio

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.config import settings
from app.repositories.job_repo import JobRepository
from app.services.analysis_service import AnalysisService
from app.worker.celery_app import celery_app


async def _run(document_id: int, user_id: int) -> None:
    # Fresh engine per task: asyncpg pools are bound to the event loop, and each
    # Celery task runs its own asyncio.run loop.
    engine = create_async_engine(settings.DATABASE_URL)
    Session = async_sessionmaker(engine, expire_on_commit=False)
    try:
        async with Session() as db:
            jobs = JobRepository(db)
            job = await jobs.create(document_id, "analysis")
            try:
                await AnalysisService(db).run(document_id, user_id)
                await jobs.mark_done(job.id)
            except Exception as e:
                await jobs.mark_failed(job.id, str(e))
                raise
    finally:
        await engine.dispose()


@celery_app.task(
    name="run_analysis",
    bind=True,
    autoretry_for=(Exception,),
    max_retries=2,
    retry_backoff=True,
)
def run_analysis(self, document_id: int, user_id: int) -> None:
    asyncio.run(_run(document_id, user_id))
