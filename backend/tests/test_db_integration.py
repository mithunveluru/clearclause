"""Integration: document persistence against the real database (skips if unreachable)."""
import uuid

import pytest
from sqlalchemy import text

from app.core.constants import DocStatus
from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.user import User
from app.repositories.document_repo import DocumentRepository


async def _db_reachable() -> bool:
    try:
        async with SessionLocal() as db:
            await db.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


async def test_document_repository_crud_flow():
    if not await _db_reachable():
        pytest.skip("database not reachable")

    async with SessionLocal() as db:
        user = User(email=f"itest-{uuid.uuid4().hex}@example.com", password_hash=hash_password("x" * 10))
        db.add(user)
        await db.commit()
        await db.refresh(user)

        repo = DocumentRepository(db)
        try:
            doc = await repo.create(user.id, "agreement.pdf", "/tmp/abc.pdf", "pdf")
            assert doc.id and doc.status == DocStatus.UPLOADED

            listed = await repo.list_for_user(user.id)
            assert [d.id for d in listed] == [doc.id]

            # ownership isolation: another user sees nothing
            assert await repo.get_for_user(doc.id, user.id + 10_000) is None

            await repo.update_status(doc.id, DocStatus.REPORT_READY)
            refreshed = await repo.get_for_user(doc.id, user.id)
            assert refreshed.status == DocStatus.REPORT_READY

            await repo.delete(refreshed)
            assert await repo.list_for_user(user.id) == []
        finally:
            await db.delete(user)
            await db.commit()
