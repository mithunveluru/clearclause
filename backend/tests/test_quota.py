"""The monthly upload quota — the ceiling on what one account can cost.

The interesting property is that it cannot be reset by deleting documents. Retention
deletes rows after seven days and users can delete their own at any time, so a quota
counted from the documents table would be a quota anyone could clear on demand.
"""
import uuid
from contextlib import asynccontextmanager

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text

from app.core.config import settings
from app.core.redis import redis_client
from app.db.session import SessionLocal
from app.main import app

# Smallest PDF that survives magic-byte sniffing and page counting
PDF = (
    b"%PDF-1.4\n"
    b"1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n"
    b"2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n"
    b"3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]>>endobj\n"
    b"trailer<</Root 1 0 R>>\n%%EOF\n"
)


async def _reachable() -> bool:
    try:
        async with SessionLocal() as db:
            await db.execute(text("SELECT 1"))
        await redis_client.ping()
        return True
    except Exception:
        return False


@pytest_asyncio.fixture(autouse=True)
async def _clear_limiter_keys():
    if await _reachable():
        keys = [k async for k in redis_client.scan_iter("rl:*")]
        if keys:
            await redis_client.delete(*keys)


@pytest.fixture
def limit_of_two(monkeypatch):
    monkeypatch.setattr(settings, "MONTHLY_UPLOAD_LIMIT", 2)


@asynccontextmanager
async def _account():
    client = AsyncClient(transport=ASGITransport(app=app), base_url="http://test")
    email = f"quota-{uuid.uuid4().hex}@example.com"
    r = await client.post(
        "/api/v1/auth/register", json={"email": email, "password": "correct horse battery"}
    )
    assert r.status_code == 201, r.text
    r = await client.post(
        "/api/v1/auth/login", json={"email": email, "password": "correct horse battery"}
    )
    assert r.status_code == 200, r.text
    client.headers["X-CSRF-Token"] = client.cookies["cc_csrf"]
    try:
        yield client
    finally:
        await client.aclose()


async def _upload(client: AsyncClient, name: str = "a.pdf"):
    return await client.post(
        "/api/v1/documents/upload", files={"file": (name, PDF, "application/pdf")}
    )


async def test_uploads_are_refused_once_the_month_is_spent(limit_of_two):
    if not await _reachable():
        pytest.skip("database/redis not reachable")

    async with _account() as client:
        assert (await _upload(client)).status_code == 201
        assert (await _upload(client)).status_code == 201

        r = await _upload(client)
        assert r.status_code == 429, "the quota let a third upload through"
        # The message has to say when it comes back, or it reads as a permanent ban
        assert "resets" in r.json()["detail"]


async def test_deleting_documents_does_not_refund_the_quota(limit_of_two):
    # Otherwise the cap is one DELETE away from being no cap at all
    if not await _reachable():
        pytest.skip("database/redis not reachable")

    async with _account() as client:
        first = await _upload(client)
        assert first.status_code == 201
        assert (await _upload(client)).status_code == 201

        deleted = await client.delete(f"/api/v1/documents/{first.json()['id']}")
        assert deleted.status_code in (200, 204), deleted.text

        r = await _upload(client)
        assert r.status_code == 429, "deleting a document handed the allowance back"


async def test_a_rejected_file_does_not_cost_the_user(limit_of_two):
    if not await _reachable():
        pytest.skip("database/redis not reachable")

    async with _account() as client:
        rejected = await client.post(
            "/api/v1/documents/upload",
            files={"file": ("notes.txt", b"this is not a pdf", "text/plain")},
        )
        assert rejected.status_code == 400, rejected.text

        # Both uploads must still be available
        assert (await _upload(client)).status_code == 201
        assert (await _upload(client)).status_code == 201


async def test_the_quota_is_per_account(limit_of_two):
    if not await _reachable():
        pytest.skip("database/redis not reachable")

    async with _account() as spender:
        assert (await _upload(spender)).status_code == 201
        assert (await _upload(spender)).status_code == 201
        assert (await _upload(spender)).status_code == 429

        async with _account() as newcomer:
            r = await _upload(newcomer)
            assert r.status_code == 201, "one account's spending blocked another's"


async def test_zero_disables_the_cap_without_counting(monkeypatch):
    # Turning the cap off must not quietly accrue a bill for when it comes back on
    if not await _reachable():
        pytest.skip("database/redis not reachable")

    monkeypatch.setattr(settings, "MONTHLY_UPLOAD_LIMIT", 0)

    async with _account() as client:
        for _ in range(3):
            assert (await _upload(client)).status_code == 201

        monkeypatch.setattr(settings, "MONTHLY_UPLOAD_LIMIT", 2)
        r = await _upload(client)
        assert r.status_code == 201, "uploads made while the cap was off were still counted"
