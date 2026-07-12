"""Refresh-token deny-list.

JWTs are self-validating, so logout could not previously end a session: a stolen
refresh token stayed valid for its full 7 days. Revoked jtis are held in Redis
only until the token would have expired anyway, so the list stays small.

Unlike the rate limiter, this fails CLOSED: if we cannot verify a token was not
revoked, we refuse it. Losing Redis costs users a re-login, not their session
security. Access tokens are not covered — they are unrevocable by design and
kept short (30 min).
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
        # Pre-revocation token, issued before jtis existed. It cannot be revoked,
        # so treat it as spent rather than trusting it.
        return True
    try:
        return bool(await redis_client.exists(_PREFIX + jti))
    except RedisError as e:
        raise RevocationUnavailable from e
