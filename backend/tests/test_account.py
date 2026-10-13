"""Password reset, data export, and account erasure over HTTP.

These are the three things a user cannot do for themselves any other way: recover a
forgotten password, get a copy of their data, and leave. The interesting cases are
the ones where the flow must refuse — a spent reset link, a wrong password on
erasure — because a bug there is a bug that hands over an account.
"""
import uuid
from contextlib import asynccontextmanager

import jwt
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text

from app.core.redis import redis_client
from app.db.session import SessionLocal
from app.main import app

PASSWORD = "correct horse battery"


async def _reachable() -> bool:
    try:
        async with SessionLocal() as db:
            await db.execute(text("SELECT 1"))
        await redis_client.ping()
        return True
    except Exception:
        return False


@pytest_asyncio.fixture(autouse=True)
async def _clear_rate_limits():
    if await _reachable():
        keys = [k async for k in redis_client.scan_iter("rl:*")]
        if keys:
            await redis_client.delete(*keys)


@pytest.fixture
def sent(monkeypatch):
    """Capture what would have been mailed, instead of queueing it to Celery."""
    outbox = []
    monkeypatch.setattr(
        "app.worker.tasks.send_email.delay",
        lambda to, subject, body: outbox.append((to, subject, body)),
    )
    return outbox


@asynccontextmanager
async def _account():
    """A client carrying a fresh user's auth cookies, plus that user's email."""
    client = AsyncClient(transport=ASGITransport(app=app), base_url="http://test")
    email = f"account-{uuid.uuid4().hex}@example.com"
    r = await client.post("/api/v1/auth/register", json={"email": email, "password": PASSWORD})
    assert r.status_code == 201, r.text
    r = await client.post("/api/v1/auth/login", json={"email": email, "password": PASSWORD})
    assert r.status_code == 200, r.text
    # The frontend echoes the readable CSRF cookie back as a header
    client.headers["X-CSRF-Token"] = client.cookies["cc_csrf"]
    try:
        yield client, email
    finally:
        await client.aclose()


def _token_from(body: str) -> str:
    return body.split("reset-password?token=")[1].split()[0]


def _payload_of(token: str) -> dict:
    return jwt.decode(token, options={"verify_signature": False})


def _subject_of(token: str) -> str:
    return _payload_of(token)["sub"]


async def _token_for(client: AsyncClient, email: str, sent: list) -> str:
    """Issue a reset token for an account and return it."""
    before = len(sent)
    await client.post("/api/v1/auth/forgot-password", json={"email": email})
    assert len(sent) == before + 1
    return _token_from(sent[-1][2])


def _repoint(token: str, subject: str) -> str:
    """Rewrite a token's subject, keeping the original (now wrong) signature."""
    payload = _payload_of(token) | {"sub": subject}
    header, _, signature = token.split(".")
    forged = jwt.encode(payload, "irrelevant", algorithm="HS256").split(".")[1]
    return f"{header}.{forged}.{signature}"


async def test_reset_link_lets_a_locked_out_user_back_in(sent):
    if not await _reachable():
        pytest.skip("database/redis not reachable")

    async with _account() as (client, email):
        r = await client.post("/api/v1/auth/forgot-password", json={"email": email})
        assert r.status_code == 200
        assert len(sent) == 1, "no reset email was queued"
        recipient, _, body = sent[0]
        assert recipient == email

        new_password = "a whole new passphrase"
        r = await client.post(
            "/api/v1/auth/reset-password",
            json={"token": _token_from(body), "password": new_password},
        )
        assert r.status_code == 200, r.text

        r = await client.post("/api/v1/auth/login", json={"email": email, "password": PASSWORD})
        assert r.status_code == 401, "the old password still works after a reset"
        r = await client.post(
            "/api/v1/auth/login", json={"email": email, "password": new_password}
        )
        assert r.status_code == 200, r.text


async def test_a_reset_link_cannot_be_used_twice(sent):
    # The whole point of binding the token to the password hash it replaces
    if not await _reachable():
        pytest.skip("database/redis not reachable")

    async with _account() as (client, email):
        await client.post("/api/v1/auth/forgot-password", json={"email": email})
        token = _token_from(sent[0][2])

        first = await client.post(
            "/api/v1/auth/reset-password", json={"token": token, "password": "first new one"}
        )
        assert first.status_code == 200, first.text

        second = await client.post(
            "/api/v1/auth/reset-password", json={"token": token, "password": "attacker choice"}
        )
        assert second.status_code == 400, "a spent reset link was accepted a second time"

        r = await client.post(
            "/api/v1/auth/login", json={"email": email, "password": "attacker choice"}
        )
        assert r.status_code == 401


async def test_a_reset_token_cannot_be_repointed_at_another_account(sent):
    # The user id is read from the token unverified, to find the hash to verify
    # against. If that read were trusted for anything else, editing it would hand
    # over someone else's account.
    if not await _reachable():
        pytest.skip("database/redis not reachable")

    async with _account() as (victim_client, victim_email):
        async with _account() as (client, email):
            await client.post("/api/v1/auth/forgot-password", json={"email": email})
            token = _token_from(sent[0][2])

        victim_id = _subject_of(await _token_for(victim_client, victim_email, sent))
        forged = _repoint(token, victim_id)

        r = await victim_client.post(
            "/api/v1/auth/reset-password", json={"token": forged, "password": "attacker choice"}
        )
        assert r.status_code == 400, "a reset token was accepted for a different account"

        r = await victim_client.post(
            "/api/v1/auth/login", json={"email": victim_email, "password": "attacker choice"}
        )
        assert r.status_code == 401


async def test_forgot_password_does_not_reveal_whether_an_address_is_registered(sent):
    if not await _reachable():
        pytest.skip("database/redis not reachable")

    async with _account() as (client, email):
        known = await client.post("/api/v1/auth/forgot-password", json={"email": email})
        stranger = await client.post(
            "/api/v1/auth/forgot-password",
            json={"email": f"nobody-{uuid.uuid4().hex}@example.com"},
        )

    assert known.status_code == stranger.status_code == 200
    assert known.json() == stranger.json(), "the response distinguishes registered addresses"
    assert len(sent) == 1, "an email was sent to an address with no account"


async def test_export_returns_the_account_and_never_the_password_hash():
    if not await _reachable():
        pytest.skip("database/redis not reachable")

    async with _account() as (client, email):
        r = await client.get("/api/v1/auth/me/export")
        assert r.status_code == 200, r.text
        data = r.json()

        assert data["account"]["email"] == email
        assert "password_hash" not in data["account"], "the export leaks the password hash"
        assert data["documents"] == []


async def test_export_requires_a_session():
    if not await _reachable():
        pytest.skip("database/redis not reachable")

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        assert (await client.get("/api/v1/auth/me/export")).status_code == 401


async def test_erasure_needs_the_password_and_then_removes_the_account():
    if not await _reachable():
        pytest.skip("database/redis not reachable")

    async with _account() as (client, email):
        wrong = await client.post("/api/v1/auth/me/delete", json={"password": "not it"})
        assert wrong.status_code == 403, "a session alone was enough to erase an account"

        r = await client.post("/api/v1/auth/me/delete", json={"password": PASSWORD})
        assert r.status_code == 200, r.text

        # The account is gone, not merely signed out
        r = await client.post("/api/v1/auth/login", json={"email": email, "password": PASSWORD})
        assert r.status_code == 401, "the erased account can still sign in"
