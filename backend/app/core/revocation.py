"""Refresh-token deny-list, so logout can actually end a session.

Fails CLOSED, unlike the rate limiter: an unverifiable token is refused.
Access tokens are unrevocable by design and kept short.
"""
from datetime import datetime, timezone

from redis.exceptions import RedisError

from app.core.redis import redis_client

_PREFIX = "revoked_jti:"


class RevocationUnavailable(Exception):
    """Redis is unreachable, so revocation cannot be checked or recorded."""


async def revoke(payload: dict) -> None:
    """Deny-list this token until its own expiry."""
    ttl = int(payload["exp"] - datetime.now(timezone.utc).timestamp())
    if ttl <= 0:
        return  # already expired; nothing to revoke
    try:
        await redis_client.setex(_PREFIX + payload["jti"], ttl, "1")
    except RedisError as e:
        raise RevocationUnavailable from e


async def is_revoked(payload: dict) -> bool:
    jti = payload.get("jti")
    if jti is None:
        # Pre-jti token: unrevocable, so treat as spent
        return True
    try:
        return bool(await redis_client.exists(_PREFIX + jti))
    except RedisError as e:
        raise RevocationUnavailable from e
