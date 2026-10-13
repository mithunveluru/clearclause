from pydantic import BaseModel


class ScoreBreakdown(BaseModel):
    fee_opacity: int
    penalty: int
    renewal: int
    consent: int
    cancellation: int


class CostOut(BaseModel):
    headline_rate: float | None
    processing_fee: float | None
    late_fee: float | None
    renewal_fee: float | None
    foreclosure_charge: float | None
    estimated_true_cost: float | None
    # "inr" | "percent" | null. Null means the document stated neither, so the
    # number must not be rendered with a unit anyone could mistake for the truth.
    processing_fee_unit: str | None = None
    late_fee_unit: str | None = None
    renewal_fee_unit: str | None = None
    foreclosure_charge_unit: str | None = None


class ScoreOut(BaseModel):
    total_score: int
    band: str
    summary: str
    breakdown: ScoreBreakdown
    cost: CostOut
