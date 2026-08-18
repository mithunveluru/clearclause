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
    # Real documents belong on s3; local is unencrypted
    STORAGE_BACKEND: str = "local"   # local | s3
    STORAGE_DIR: str = "/storage"    # local backend root
    S3_BUCKET: str = ""
    S3_ENDPOINT_URL: str = ""        # set for R2 / Spaces / MinIO; blank for AWS
    S3_REGION: str = ""
    OCR_PROVIDER: str = "auto"  # auto = PDF text layer first, OCR only scanned pages
    OCR_LOW_CONFIDENCE: int = 60  # below this mean OCR confidence, warn the user (0-100)
    # Retried only on pages English could not read; patta and sale deeds are often Tamil.
    # Needs the matching tesseract-ocr-<lang> package; blank disables the retry.
    OCR_FALLBACK_LANGS: str = "eng+tam"
    OTEL_EXPORTER_OTLP_ENDPOINT: str = ""
    MAX_UPLOAD_MB: int = 10
    MAX_PDF_PAGES: int = 50   # a 10MB PDF can hold thousands of pages; OCR memory scales with them
    FILE_RETENTION_DAYS: int = 7
    CORS_ORIGINS: str = "http://localhost:3000"  # comma-separated
    CORS_ORIGIN_REGEX: str = ""       # Vercel previews get a new hostname per commit
    # Password reset links are built against this; it is what the user's browser sees
    PUBLIC_APP_URL: str = "http://localhost:3000"

    # Transactional email. Blank host logs the message instead of sending it, which
    # is what dev and CI want — and what production must not do, hence the invariant.
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = "ClearClause <noreply@localhost>"

    ENV: str = "development"          # set to "production" in prod deployments
    COOKIE_SECURE: bool = False       # set True when serving over HTTPS
    # none when frontend and API are different sites
    COOKIE_SAMESITE: str = "lax"      # lax | none
    TRUSTED_PROXY_DEPTH: int = 0      # 1 for nginx/Traefik, 0 for direct
    METRICS_TOKEN: str = ""           # non-empty enables /internal/metrics with token auth

    # auto proceeds, confirm surfaces alternatives, manual needs a pick
    CLASSIFICATION_AUTO_THRESHOLD: float = 0.90
    CLASSIFICATION_CONFIRM_THRESHOLD: float = 0.70

    AI_MODE: str = "off"  # off | summary_only | full
    AI_MODEL: str = "llama-3.3-70b-versatile"
    GROQ_API_KEY: str = ""
    JINA_API_KEY: str = ""
    QDRANT_URL: str = "http://qdrant:6333"

    @model_validator(mode="after")
    def _normalize_database_url(self) -> "Settings":
        """Managed Postgres (Render, Heroku, …) hands out a driverless URL."""
        url = self.DATABASE_URL
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
        if url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
        object.__setattr__(self, "DATABASE_URL", url)
        return self

    @model_validator(mode="after")
    def _enforce_production_invariants(self) -> "Settings":
        """Refuse to start a misconfigured production deployment.

        In settings, not the API lifespan, so it covers the worker and alembic too.
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
        if not self.PUBLIC_APP_URL.startswith("https://"):
            problems.append("PUBLIC_APP_URL must be an https:// URL (reset links use it)")
        if not self.SMTP_HOST:
            # Without it, password reset silently succeeds and mails nothing
            problems.append("SMTP_HOST is required (password reset cannot work without it)")
        if problems:
            raise ValueError("Refusing to start in production: " + "; ".join(problems))
        return self

    @model_validator(mode="after")
    def _enforce_cookie_invariants(self) -> "Settings":
        """Browsers silently drop a SameSite=None cookie that is not Secure."""
        problems = []
        if self.COOKIE_SAMESITE not in ("lax", "none"):
            problems.append(f"COOKIE_SAMESITE must be lax or none, got {self.COOKIE_SAMESITE!r}")
        if self.COOKIE_SAMESITE == "none" and not self.COOKIE_SECURE:
            problems.append("COOKIE_SAMESITE=none requires COOKIE_SECURE=true")
        if problems:
            raise ValueError("Refusing to start: " + "; ".join(problems))
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
