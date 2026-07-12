import logging
import time

from fastapi import HTTPException, Request, status
from redis.exceptions import RedisError

from app.core.config import settings
from app.core.redis import redis_client

logger = logging.getLogger(__name__)

__all__ = ["rate_limit", "redis_client"]


def _real_ip(request: Request) -> str:
    """Return the real client IP, honoring X-Forwarded-For up to TRUSTED_PROXY_DEPTH hops."""
    depth = settings.TRUSTED_PROXY_DEPTH
    if depth > 0:
        xff = request.headers.get("X-Forwarded-For", "")
        ips = [ip.strip() for ip in xff.split(",") if ip.strip()]
        # The rightmost entry added by the last trusted proxy is at index -(depth)
        if len(ips) >= depth:
            return ips[-depth]
    return request.client.host if request.client else "unknown"


def rate_limit(limit: int, window: int, scope: str):
    """Fixed-window Redis rate limiter keyed by real client IP.

    ponytail: fixed window (cheap, INCR+EXPIRE). Bursts at window edges are
    acceptable for an MVP; swap for sliding-window/token bucket if abused.
    """

    async def dependency(request: Request) -> None:
        ip = _real_ip(request)
        key = f"rl:{scope}:{ip}:{int(time.time()) // window}"
        try:
            count = await redis_client.incr(key)
            if count == 1:
                await redis_client.expire(key, window)
        except RedisError:
            # Fail open: a Redis outage must not take down login/upload/Q&A with it.
            # The tradeoff is that brute-force protection is absent while Redis is
            # down, so this logs at error level — it should page, not pass quietly.
            logger.error("rate limiter unavailable (scope=%s); allowing request", scope)
            return
        if count > limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests, slow down.",
            )

    return dependency
