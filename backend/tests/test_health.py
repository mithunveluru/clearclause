"""The health route is what every watching layer reads.

Container healthchecks, platform health probes and uptime monitors all look at the
status code and nothing else. A 200 carrying the word "degraded" tells them the
service is fine, which is how an outage goes unnoticed for hours.
"""
import pytest
from httpx import ASGITransport, AsyncClient
from redis.exceptions import RedisError
from sqlalchemy import text

from app.core.redis import redis_client
from app.db.session import SessionLocal
from app.main import app


async def _reachable() -> bool:
    try:
        async with SessionLocal() as db:
            await db.execute(text("SELECT 1"))
        await redis_client.ping()
        return True
    except Exception:
        return False


async def test_health_is_ok_when_both_dependencies_answer():
    if not await _reachable():
        pytest.skip("database/redis not reachable")

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        r = await client.get("/health")

    assert r.status_code == 200
    assert r.json() == {"status": "ok", "database": True, "redis": True}


async def test_health_reports_503_when_redis_is_down(monkeypatch):
    if not await _reachable():
        pytest.skip("database/redis not reachable")

    async def refuse():
        raise RedisError("connection refused")

    monkeypatch.setattr(redis_client, "ping", refuse)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        r = await client.get("/health")

    assert r.status_code == 503, "a degraded service answered 200; nothing watching it would notice"
    # Which dependency failed is the difference between a quick fix and an hour of guessing
    assert r.json() == {"status": "degraded", "database": True, "redis": False}
