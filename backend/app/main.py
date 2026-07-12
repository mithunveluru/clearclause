import logging
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from app.api.deps import get_current_user
from app.api.health import router as health_router
from app.api.v1.analysis import router as analysis_router
from app.api.v1.auth import router as auth_router
from app.api.v1.documents import router as documents_router
from app.core.config import settings
from app.core.logredact import install_redaction
from app.db.session import engine
from app.models.user import User
from app.schemas.auth import UserOut
from app.telemetry import (
    instrument_celery,
    instrument_engine,
    instrument_fastapi,
    instrument_redis,
    setup_telemetry,
)

logger = logging.getLogger(__name__)

setup_telemetry("clearclause-api")
install_redaction()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Refuse to start in production with the default JWT secret.
    if settings.JWT_SECRET == "change-me-in-prod":
        if settings.ENV == "production":
            raise RuntimeError(
                "JWT_SECRET must be changed from the default value before running in production"
            )
        logger.warning(
            "⚠  JWT_SECRET is using the insecure default — set a strong random value before deploying"
        )

    if settings.AI_MODE != "off":
        from app.services.knowledge_index_service import KnowledgeIndexService
        await KnowledgeIndexService().index_async()
    yield


app = FastAPI(title="ClearClause API", version="0.1.0", lifespan=lifespan)


@app.middleware("http")
async def add_security_headers(request: Request, call_next) -> Response:
    response = await call_next(request)
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("X-XSS-Protection", "0")  # OWASP: disable legacy auditor
    response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    response.headers.setdefault(
        "Content-Security-Policy",
        "default-src 'none'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; "
        "font-src 'self'; frame-ancestors 'none'; base-uri 'none'",
    )
    if settings.COOKIE_SECURE:  # HTTPS only
        response.headers.setdefault(
            "Strict-Transport-Security", "max-age=31536000; includeSubDomains"
        )
    return response


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Cookie", "X-Request-ID"],
)

app.include_router(health_router)
app.include_router(auth_router)
app.include_router(documents_router)
app.include_router(analysis_router)


@app.get("/api/v1/me", response_model=UserOut, tags=["auth"])
async def me(user: User = Depends(get_current_user)):
    return user


# Metrics not exposed publicly; guarded by METRICS_TOKEN on /internal/metrics.
_instrumentator = Instrumentator().instrument(app)

if settings.METRICS_TOKEN:
    import secrets as _secrets

    from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

    @app.get("/internal/metrics", include_in_schema=False)
    async def internal_metrics(request: Request):
        token = request.headers.get("X-Metrics-Token", "")
        if not _secrets.compare_digest(token, settings.METRICS_TOKEN):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


# OTel auto-instrumentation (no-op unless OTEL endpoint is configured).
instrument_fastapi(app)
instrument_engine(engine)
instrument_celery()
instrument_redis()
