from functools import lru_cache

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

DEFAULT_JWT_SECRET = "change-me-in-prod"


class Settings(BaseSettings):
    """App configuration, sourced from environment (see .env.example)."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str = "postgresql+asyncpg://clearclause:clearclause@db:5432/clearclause"
    REDIS_URL: str = "redis://redis:6379/0"
    JWT_SECRET: str = DEFAULT_JWT_SECRET
    UPLOAD_DIR: str = "/storage/uploads"
    REPORT_DIR: str = "/storage/reports"
    OCR_PROVIDER: str = "auto"  # auto = PDF text layer first, OCR only scanned pages
    OTEL_EXPORTER_OTLP_ENDPOINT: str = ""
    MAX_UPLOAD_MB: int = 10
    MAX_PDF_PAGES: int = 50   # a 10MB PDF can hold thousands of pages; OCR memory scales with them
    FILE_RETENTION_DAYS: int = 7
    CORS_ORIGINS: str = "http://localhost:3000"  # comma-separated

    ENV: str = "development"          # set to "production" in prod deployments
    COOKIE_SECURE: bool = False       # set True when serving over HTTPS
    TRUSTED_PROXY_DEPTH: int = 0      # 1 for nginx/Traefik, 0 for direct
    METRICS_TOKEN: str = ""           # non-empty enables /internal/metrics with token auth

    # routing thresholds: auto proceeds, confirm surfaces alternatives, manual needs a pick
    CLASSIFICATION_AUTO_THRESHOLD: float = 0.90
    CLASSIFICATION_CONFIRM_THRESHOLD: float = 0.70

    # AI / RAG (V3) — all optional. AI_MODE=off keeps V1/V2 fully working.
    AI_MODE: str = "off"  # off | summary_only | full
    AI_MODEL: str = "llama-3.3-70b-versatile"
    GROQ_API_KEY: str = ""
    JINA_API_KEY: str = ""
    QDRANT_URL: str = "http://qdrant:6333"

    @model_validator(mode="after")
    def _enforce_production_invariants(self) -> "Settings":
        """Refuse to start a misconfigured production deployment.

        Lives here, not in the API's lifespan, so it also covers the worker and
        alembic — neither of which runs the app's startup hooks.
        """
        if self.ENV != "production":
            return self
        problems = []
        if self.JWT_SECRET == DEFAULT_JWT_SECRET:
            problems.append("JWT_SECRET is still the default value")
        if not self.COOKIE_SECURE:
            problems.append("COOKIE_SECURE must be true (auth cookies need the Secure flag)")
        if any(o.startswith("http://") for o in self.cors_origins_list):
            problems.append("CORS_ORIGINS contains a plaintext http:// origin")
        if problems:
            raise ValueError("Refusing to start in production: " + "; ".join(problems))
        return self

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    @property
    def sync_database_url(self) -> str:
        """psycopg2 URL for Alembic (async driver can't run migrations)."""
        return self.DATABASE_URL.replace("+asyncpg", "+psycopg2")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
