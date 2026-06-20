import time

from fastapi import HTTPException, Request, status

from app.core.redis import redis_client


def rate_limit(limit: int, window: int, scope: str):
    """Fixed-window Redis limiter keyed by client IP. Use as a route dependency.

    ponytail: fixed window (cheap, INCR+EXPIRE). Bursts at window edges are
    acceptable for an MVP; swap for a sliding-window/token bucket if abused.
    """

    async def dependency(request: Request) -> None:
        ip = request.client.host if request.client else "unknown"
        key = f"rl:{scope}:{ip}:{int(time.time()) // window}"
        count = await redis_client.incr(key)
        if count == 1:
            await redis_client.expire(key, window)
        if count > limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests, slow down.",
            )

    return dependency
