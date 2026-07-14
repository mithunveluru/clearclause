"""Per-account login lockout.

The IP-keyed rate limiter cannot see credential stuffing spread across many IPs.
Fails open: a Redis outage must not lock everyone out of their own accounts.
"""
import logging

from redis.exceptions import RedisError

from app.core.redis import redis_client

logger = logging.getLogger(__name__)

MAX_FAILURES = 10
WINDOW_SECONDS = 15 * 60

_PREFIX = "login_fail:"


def _key(email: str) -> str:
    return _PREFIX + email.strip().lower()


async def is_locked(email: str) -> bool:
    try:
        count = await redis_client.get(_key(email))
    except RedisError:
        logger.error("lockout store unavailable; allowing login attempt")
        return False
    return int(count or 0) >= MAX_FAILURES


async def record_failure(email: str) -> None:
    try:
        key = _key(email)
        count = await redis_client.incr(key)
        if count == 1:
            await redis_client.expire(key, WINDOW_SECONDS)
    except RedisError:
        logger.error("lockout store unavailable; failed login not counted")


async def clear(email: str) -> None:
    try:
        await redis_client.delete(_key(email))
    except RedisError:
        logger.error("lockout store unavailable; failure count not cleared")
