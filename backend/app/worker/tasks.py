import asyncio
import os
from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core import storage
from app.core.config import settings
from app.models.document import Document
from app.models.report import Report
from app.services.document_service import purge_vectors
from app.worker.celery_app import celery_app


def _sweep_local_orphans(keep: set[str], store: storage.Storage) -> int:
    """Delete unreferenced files the local backend left behind.

    Local backend only; on S3 a lifecycle rule does this.
    """
    if not isinstance(store, storage.LocalStorage):
        return 0

    removed = 0
    for prefix in ("uploads", "reports"):
        directory = os.path.join(store.root, prefix)
        if not os.path.isdir(directory):
            continue
        for name in os.listdir(directory):
            if name == ".gitkeep":
                continue
            key = f"{prefix}/{name}"
            if key not in keep:
                store.delete(key)
                removed += 1
    return removed


async def _cleanup() -> dict:
    cutoff = datetime.utcnow() - timedelta(days=settings.FILE_RETENTION_DAYS)
    store = storage.get_storage()
    engine = create_async_engine(settings.DATABASE_URL)
    Session = async_sessionmaker(engine, expire_on_commit=False)
    try:
        async with Session() as db:
            # Filter in SQL; the whole table grew memory
            stale = (
                await db.execute(select(Document).where(Document.created_at < cutoff))
            ).scalars().all()
            for d in stale:
                store.delete(d.file_path)
                purge_vectors(d.id)
                await db.delete(d)  # cascades to clauses/findings/scores/reports rows
            await db.commit()

            # Keys only, not rows
            keep = set((await db.execute(select(Document.file_path))).scalars().all())
            keep |= {
                p for p in (await db.execute(select(Report.pdf_path))).scalars().all() if p
            }
            orphans = _sweep_local_orphans(keep, store)
            return {"stale_docs": len(stale), "orphan_files": orphans}
    finally:
        await engine.dispose()


@celery_app.task(name="cleanup_stale_files")
def cleanup_stale_files() -> dict:
    """Delete documents past retention and sweep unreferenced local files."""
    return asyncio.run(_cleanup())
