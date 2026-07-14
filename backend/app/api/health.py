from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db

router = APIRouter(tags=["system"])


@router.get("/health")
async def health(db: AsyncSession = Depends(get_db)) -> dict:
    """Liveness + DB connectivity check."""
    try:
        await db.execute(text("SELECT 1"))
        db_ok = True
    except Exception:  # ponytail: any DB error means unhealthy
        db_ok = False
    return {"status": "ok" if db_ok else "degraded", "database": db_ok}
