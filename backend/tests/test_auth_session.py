"""Session lifecycle over HTTP: logout must actually end a session.

JWTs are self-validating, so before revocation existed, logout only deleted the
client's cookie — a stolen refresh token stayed usable for its full 7 days.
"""
import uuid
from contextlib import asynccontextmanager

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text

from app.core import lockout
from app.core.redis import redis_client
from app.db.session import SessionLocal
from app.main import app

_last_email = ""


async def _reachable() -> bool:
    try:
        async with SessionLocal() as db:
            await db.execute(text("SELECT 1"))
        await redis_client.ping()
        return True
    except Exception:
        return False


async def _clear_rate_limit_keys() -> None:
    keys = [k async for k in redis_client.scan_iter("rl:*")]
    if keys:
        await redis_client.delete(*keys)


@pytest_asyncio.fixture(autouse=True)
async def _clear_rate_limits():
    if await _reachable():
        await _clear_rate_limit_keys()


@asynccontextmanager
async def _login():
    """A client carrying a fresh user's auth cookies."""
    global _last_email
    client = AsyncClient(transport=ASGITransport(app=app), base_url="http://test")
    email = _last_email = f"session-{uuid.uuid4().hex}@example.com"
    password = "correct horse battery"
    r = await client.post("/api/v1/auth/register", json={"email": email, "password": password})
    assert r.status_code == 201, r.text
    r = await client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert r.status_code == 200, r.text
    try:
        yield client
    finally:
        await client.aclose()


async def test_logout_revokes_the_refresh_token():
    if not await _reachable():
        pytest.skip("database/redis not reachable")

    async with _login() as client:
        stolen = client.cookies["cc_refresh"]

        assert (await client.post("/api/v1/auth/refresh")).status_code == 200
        assert (await client.post("/api/v1/auth/logout")).status_code == 200

        # A token captured before logout must be refused
        client.cookies.set("cc_refresh", stolen, path="/api/v1/auth")
        r = await client.post("/api/v1/auth/refresh")
        assert r.status_code == 401, "logout did not actually end the session"


async def test_refresh_rotates_and_the_old_token_cannot_be_replayed():
    if not await _reachable():
        pytest.skip("database/redis not reachable")

    async with _login() as client:
        first = client.cookies["cc_refresh"]

        r = await client.post("/api/v1/auth/refresh")
        assert r.status_code == 200
        assert client.cookies["cc_refresh"] != first, "refresh did not rotate the token"

        client.cookies.set("cc_refresh", first, path="/api/v1/auth")
        r = await client.post("/api/v1/auth/refresh")
        assert r.status_code == 401, "a spent refresh token was accepted again"


async def test_logout_is_reachable_by_the_refresh_cookie():
    # Path-scoped: if it misses /logout, revocation is dead code
    if not await _reachable():
        pytest.skip("database/redis not reachable")

    async with _login() as client:
        r = await client.post("/api/v1/auth/logout")
        assert "cc_refresh" in r.request.headers.get("cookie", "")


async def test_duplicate_registration_is_rejected():
    if not await _reachable():
        pytest.skip("database/redis not reachable")

    async with _login() as client:
        # A duplicate registration must not silently succeed
        r = await client.post("/api/v1/auth/register", json={"email": _last_email, "password": "x" * 12})
        assert r.status_code == 409
        assert "already registered" in r.json()["detail"].lower()


async def test_account_locks_after_repeated_failures():
    if not await _reachable():
        pytest.skip("database/redis not reachable")

    async with _login() as client:
        email = _last_email
        for _ in range(lockout.MAX_FAILURES):
            # Clearing the IP window each round simulates many IPs
            await _clear_rate_limit_keys()
            r = await client.post("/api/v1/auth/login", json={"email": email, "password": "wrong"})
            assert r.status_code == 401

        # Per-account: the correct password is refused too
        await _clear_rate_limit_keys()
        r = await client.post(
            "/api/v1/auth/login", json={"email": email, "password": "correct horse battery"}
        )
        assert r.status_code == 429

        await lockout.clear(email)
        r = await client.post(
            "/api/v1/auth/login", json={"email": email, "password": "correct horse battery"}
        )
        assert r.status_code == 200, "clearing the lock should let the real user back in"
