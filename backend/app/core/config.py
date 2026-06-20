from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """App configuration, sourced from environment (see .env.example)."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str = "postgresql+asyncpg://clearclause:clearclause@db:5432/clearclause"
    REDIS_URL: str = "redis://redis:6379/0"
    JWT_SECRET: str = "change-me-in-prod"
    UPLOAD_DIR: str = "/storage/uploads"
    REPORT_DIR: str = "/storage/reports"
    OCR_PROVIDER: str = "tesseract"
    OTEL_EXPORTER_OTLP_ENDPOINT: str = ""
    MAX_UPLOAD_MB: int = 10

    @property
    def sync_database_url(self) -> str:
        """psycopg2 URL for Alembic (async driver can't run migrations)."""
        return self.DATABASE_URL.replace("+asyncpg", "+psycopg2")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
