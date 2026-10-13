"""HTTP-level authorization: a document is reachable only by its owner.

Every document-scoped endpoint repeats an ownership check by hand
(`DocumentService.get(doc_id, user.id)`). One forgotten call is a silent IDOR,
so this walks the real ASGI app and asserts the invariant on every route.

Denial and "no data yet" both return 404, so asserting on the status alone would
pass even if the check were removed. We assert the *detail* is "Document not
found" — the ownership denial — which no missing-data path produces.
"""
import uuid

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text

from app.core.ratelimit import redis_client
from app.db.session import SessionLocal
from app.main import app
from app.repositories.document_repo import DocumentRepository

DENIED = "Document not found"

async def _reachable() -> bool:
    try:
        async with SessionLocal() as db:
            await db.execute(text("SELECT 1"))
        await redis_client.ping()
        return True
    except Exception:
        return False


def _client() -> AsyncClient:
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://test")


async def _signup(client: AsyncClient) -> dict[str, str]:
    """Register + log in a fresh user; returns their auth cookies."""
    email = f"authz-{uuid.uuid4().hex}@example.com"
    password = "correct horse battery"
    r = await client.post("/api/v1/auth/register", json={"email": email, "password": password})
    assert r.status_code == 201, r.text
    r = await client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert r.status_code == 200, r.text
    return {"cc_token": r.cookies["cc_token"]}


# (method, path suffix, json body) for every document-scoped route.
ROUTES = [
    ("GET", "", None),
    ("GET", "/file", None),
    ("DELETE", "", None),
    ("POST", "/analyze", None),
    ("POST", "/reprocess", None),
    ("GET", "/explorer", None),
    ("GET", "/classification", None),
    ("PATCH", "/classification", {"classified_type": "rental_contract"}),
    ("GET", "/entities", None),
    ("GET", "/analysis", None),
    ("GET", "/findings", None),
    ("GET", "/score", None),
    ("GET", "/ai-summary", None),
    ("GET", "/report", None),
    ("POST", "/qa", {"question": "what is the rent?"}),
]


@pytest_asyncio.fixture(autouse=True)
async def _clear_rate_limits():
    # Tests share one IP; without this, flaky
    if await _reachable():
        keys = [k async for k in redis_client.scan_iter("rl:*")]
        if keys:
            await redis_client.delete(*keys)


async def test_non_owner_is_denied_on_every_document_route():
    if not await _reachable():
        pytest.skip("database/redis not reachable")

    async with _client() as client:
        owner = await _signup(client)
        attacker = await _signup(client)

        async with SessionLocal() as db:
            docs = DocumentRepository(db)
            doc = await docs.create(
                (await _user_id(client, owner)), "private.pdf", "/tmp/private.pdf", "pdf"
            )
            doc_id = doc.id

        try:
            for method, suffix, body in ROUTES:
                r = await client.request(
                    method,
                    f"/api/v1/documents/{doc_id}{suffix}",
                    json=body,
                    cookies=attacker,
                )
                assert r.status_code == 404, f"{method} {suffix} leaked: {r.status_code}"
                assert r.json()["detail"] == DENIED, f"{method} {suffix} denied for the wrong reason"

            # The attacker's DELETE must not have actually deleted anything.
            async with SessionLocal() as db:
                assert await DocumentRepository(db).get_by_id(doc_id) is not None
        finally:
            async with SessionLocal() as db:
                d = await DocumentRepository(db).get_by_id(doc_id)
                if d:
                    await DocumentRepository(db).delete(d)


async def test_unauthenticated_is_rejected_on_every_document_route():
    if not await _reachable():
        pytest.skip("database/redis not reachable")

    async with _client() as client:
        for method, suffix, body in ROUTES:
            r = await client.request(method, f"/api/v1/documents/1{suffix}", json=body)
            assert r.status_code == 401, f"{method} {suffix} served an anonymous caller"


async def test_document_list_is_scoped_to_the_owner():
    if not await _reachable():
        pytest.skip("database/redis not reachable")

    async with _client() as client:
        owner = await _signup(client)
        attacker = await _signup(client)
        owner_id = await _user_id(client, owner)

        async with SessionLocal() as db:
            doc = await DocumentRepository(db).create(
                owner_id, "private.pdf", "/tmp/private.pdf", "pdf"
            )
            doc_id = doc.id

        try:
            r = await client.get("/api/v1/documents", cookies=attacker)
            assert r.status_code == 200
            assert doc_id not in [d["id"] for d in r.json()]

            r = await client.get("/api/v1/documents", cookies=owner)
            assert doc_id in [d["id"] for d in r.json()]
        finally:
            async with SessionLocal() as db:
                d = await DocumentRepository(db).get_by_id(doc_id)
                if d:
                    await DocumentRepository(db).delete(d)


async def _user_id(client: AsyncClient, cookies: dict[str, str]) -> int:
    r = await client.get("/api/v1/me", cookies=cookies)
    assert r.status_code == 200, r.text
    return r.json()["id"]
