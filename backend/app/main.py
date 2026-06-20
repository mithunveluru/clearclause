from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from app.api.deps import get_current_user
from app.core.config import settings
from app.db.session import engine
from app.telemetry import (
    instrument_celery,
    instrument_engine,
    instrument_fastapi,
    instrument_redis,
    setup_telemetry,
)

setup_telemetry("clearclause-api")
from app.api.health import router as health_router
from app.api.v1.auth import router as auth_router
from app.api.v1.analysis import router as analysis_router
from app.api.v1.documents import router as documents_router
from app.models.user import User
from app.schemas.auth import UserOut

app = FastAPI(title="ClearClause API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(auth_router)
app.include_router(documents_router)
app.include_router(analysis_router)


@app.get("/api/v1/me", response_model=UserOut, tags=["auth"])
async def me(user: User = Depends(get_current_user)):
    return user


# Prometheus /metrics (works with or without the OTel stack).
Instrumentator().instrument(app).expose(app, endpoint="/metrics", include_in_schema=False)

# OTel auto-instrumentation (no-op unless OTEL endpoint is configured).
instrument_fastapi(app)
instrument_engine(engine)
instrument_celery()  # producer side: propagates trace context into enqueued tasks
instrument_redis()
