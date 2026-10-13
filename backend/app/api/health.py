from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.redis import redis_client
from app.db.session import get_db

router = APIRouter(tags=["system"])


@router.get("/health")
async def health(response: Response, db: AsyncSession = Depends(get_db)) -> dict:
    """Liveness plus the two dependencies nothing works without.

    Degraded answers 503, not 200. A 200 that says "degraded" in its body is invisible
    to every layer that watches this route — the container healthcheck, the platform's
    health probe, an uptime monitor — all of which read the status code and nothing
    else. The body stays, because knowing *which* dependency is down is the difference
    between a two-minute fix and an hour of guessing.
    """
    try:
        await db.execute(text("SELECT 1"))
        db_ok = True
    except Exception:  # any DB error means unhealthy
        db_ok = False

    # Redis backs the queue, rate limiter and token revocation
    try:
        redis_ok = bool(await redis_client.ping())
    except Exception:
        redis_ok = False

    healthy = db_ok and redis_ok
    if not healthy:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return {
        "status": "ok" if healthy else "degraded",
        "database": db_ok,
        "redis": redis_ok,
    }
