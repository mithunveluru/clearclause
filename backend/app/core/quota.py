"""Per-account monthly upload quota.

The IP rate limiter caps how fast a client can upload; this caps how much. They are
different problems: OCR is the expensive part of this product and it is CPU-bound, so
one account uploading steadily all month costs real money that a per-minute limit
never notices.

Counted in Redis rather than by counting rows. Documents are deleted after
FILE_RETENTION_DAYS and users can delete their own at any time, so the documents table
is not a record of what anyone used — count it and an account can upload, delete, and
upload again without limit.

Fails open, like the rate limiter and the login lockout: a Redis outage must not stop
people using what they were promised.
"""
import logging
from datetime import datetime, timezone

from fastapi import HTTPException, status
from redis.exceptions import RedisError

from app.core.config import settings
from app.core.redis import redis_client
from app.metrics import count_degraded

logger = logging.getLogger(__name__)

_PREFIX = "quota:"
# Comfortably past any month, so a key outlives the period it counts and then goes
_TTL_SECONDS = 62 * 24 * 3600


def _key(user_id: int) -> str:
    """Calendar month, which is what a person expects a monthly allowance to mean."""
    return f"{_PREFIX}{user_id}:{datetime.now(timezone.utc):%Y-%m}"


async def used(user_id: int) -> int:
    try:
        return int(await redis_client.get(_key(user_id)) or 0)
    except RedisError:
        count_degraded("quota_store_unavailable")
        logger.error("quota store unavailable; allowing upload")
        return 0


async def enforce(user_id: int) -> None:
    """Refuse the upload if this account has spent its month. Call before accepting one."""
    if settings.MONTHLY_UPLOAD_LIMIT <= 0:  # 0 disables the quota entirely
        return
    if await used(user_id) < settings.MONTHLY_UPLOAD_LIMIT:
        return
    raise HTTPException(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        detail=(
            f"You have used all {settings.MONTHLY_UPLOAD_LIMIT} document uploads for this "
            "month. The allowance resets on the first of next month."
        ),
    )


async def record(user_id: int) -> None:
    """Count one upload. Call only once the document is safely stored.

    Separate from enforce() so a rejected file — wrong type, too many pages — does not
    cost the user part of their month. Two calls means two accounts uploading at the
    same instant can both pass the check and land one over the limit; a quota that
    overshoots by one under a race is not worth a lock.
    """
    if settings.MONTHLY_UPLOAD_LIMIT <= 0:
        return
    try:
        key = _key(user_id)
        if await redis_client.incr(key) == 1:
            await redis_client.expire(key, _TTL_SECONDS)
    except RedisError:
        count_degraded("quota_store_unavailable")
        logger.error("quota store unavailable; upload not counted")
