import uuid

import pytest
from fastapi import HTTPException
from redis.exceptions import ConnectionError as RedisConnectionError
from starlette.requests import Request

from app.core import ratelimit
from app.core.ratelimit import rate_limit, redis_client


def _request(ip: str = "203.0.113.7") -> Request:
    return Request(
        {"type": "http", "method": "POST", "path": "/", "headers": [], "client": (ip, 1234)}
    )


async def _redis_up() -> bool:
    try:
        await redis_client.ping()
        return True
    except Exception:
        return False


async def test_limit_is_enforced():
    if not await _redis_up():
        pytest.skip("redis not reachable")
    guard = rate_limit(limit=2, window=60, scope=f"test-{uuid.uuid4().hex}")
    req = _request()

    await guard(req)
    await guard(req)
    with pytest.raises(HTTPException) as e:
        await guard(req)
    assert e.value.status_code == 429


async def test_fails_open_when_redis_is_down(monkeypatch):
    # A Redis outage used to 500 every login, upload and Q&A. Availability wins;
    # the tradeoff (no brute-force protection meanwhile) is logged at error level.
    async def boom(*_a, **_kw):
        raise RedisConnectionError("redis is down")

    monkeypatch.setattr(ratelimit.redis_client, "incr", boom)
    guard = rate_limit(limit=1, window=60, scope="test-outage")

    assert await guard(_request()) is None
