from sqlalchemy import Float, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class RiskScore(Base):
    __tablename__ = "risk_scores"

    id: Mapped[int] = mapped_column(primary_key=True)
    document_id: Mapped[int] = mapped_column(
        ForeignKey("documents.id", ondelete="CASCADE"), unique=True, index=True, nullable=False
    )
    total_score: Mapped[int] = mapped_column(Integer, nullable=False)
    fee_opacity_score: Mapped[int] = mapped_column(Integer, nullable=False)
    penalty_score: Mapped[int] = mapped_column(Integer, nullable=False)
    consent_score: Mapped[int] = mapped_column(Integer, nullable=False)
    renewal_score: Mapped[int] = mapped_column(Integer, nullable=False)
    cancellation_score: Mapped[int] = mapped_column(Integer, nullable=False)


class CostBreakdown(Base):
    __tablename__ = "cost_breakdowns"

    id: Mapped[int] = mapped_column(primary_key=True)
    document_id: Mapped[int] = mapped_column(
        ForeignKey("documents.id", ondelete="CASCADE"), unique=True, index=True, nullable=False
    )
    headline_rate: Mapped[float | None] = mapped_column(Float, nullable=True)
    processing_fee: Mapped[float | None] = mapped_column(Float, nullable=True)
    late_fee: Mapped[float | None] = mapped_column(Float, nullable=True)
    renewal_fee: Mapped[float | None] = mapped_column(Float, nullable=True)
    foreclosure_charge: Mapped[float | None] = mapped_column(Float, nullable=True)
    estimated_true_cost: Mapped[float | None] = mapped_column(Float, nullable=True)
