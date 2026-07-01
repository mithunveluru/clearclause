from sqlalchemy import Float, ForeignKey, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class DocumentClassification(Base, TimestampMixin):
    __tablename__ = "document_classifications"

    id: Mapped[int] = mapped_column(primary_key=True)
    document_id: Mapped[int] = mapped_column(
        ForeignKey("documents.id", ondelete="CASCADE"), unique=True, index=True, nullable=False
    )
    classified_type: Mapped[str] = mapped_column(String(40), nullable=False)
    document_family: Mapped[str | None] = mapped_column(String(20), nullable=True)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    signals_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    candidates_json: Mapped[list | None] = mapped_column(JSON, nullable=True)
    routing_action: Mapped[str] = mapped_column(String(10), nullable=False, server_default="auto")
