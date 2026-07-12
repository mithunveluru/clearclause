import asyncio
import os
from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core import files
from app.core.config import settings
from app.models.document import Document
from app.models.report import Report
from app.worker.celery_app import celery_app


def _sweep_orphans(keep: set[str]) -> int:
    removed = 0
    for directory in (settings.UPLOAD_DIR, settings.REPORT_DIR):
        if not os.path.isdir(directory):
            continue
        for name in os.listdir(directory):
            if name == ".gitkeep":
                continue
            path = os.path.join(directory, name)
            if path not in keep:
                files.delete_file(path)
                removed += 1
    return removed


async def _cleanup() -> dict:
    cutoff = datetime.utcnow() - timedelta(days=settings.FILE_RETENTION_DAYS)
    engine = create_async_engine(settings.DATABASE_URL)
    Session = async_sessionmaker(engine, expire_on_commit=False)
    try:
        async with Session() as db:
            # Filter in SQL. Loading every document to find the stale ones grew the
            # job's memory with the whole table.
            stale = (
                await db.execute(select(Document).where(Document.created_at < cutoff))
            ).scalars().all()
            for d in stale:
                files.delete_file(d.file_path)
                await db.delete(d)  # cascades to clauses/findings/scores/reports rows
            await db.commit()

            # The orphan sweep does need every referenced path, but only the paths —
            # not the hydrated rows.
            keep = set((await db.execute(select(Document.file_path))).scalars().all())
            keep |= {
                p for p in (await db.execute(select(Report.pdf_path))).scalars().all() if p
            }
            orphans = _sweep_orphans(keep)
            return {"stale_docs": len(stale), "orphan_files": orphans}
    finally:
        await engine.dispose()


@celery_app.task(name="cleanup_stale_files")
def cleanup_stale_files() -> dict:
    """Delete documents past retention and sweep unreferenced files on disk."""
    return asyncio.run(_cleanup())
