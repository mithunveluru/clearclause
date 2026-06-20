from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.score import CostBreakdown, RiskScore


class ScoreRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def save_risk(self, document_id: int, cats: dict) -> None:
        await self.db.execute(
            delete(RiskScore).where(RiskScore.document_id == document_id)
        )
        self.db.add(
            RiskScore(
                document_id=document_id,
                total_score=cats["total"],
                fee_opacity_score=cats["fee_opacity"],
                penalty_score=cats["penalty"],
                consent_score=cats["consent"],
                renewal_score=cats["renewal"],
                cancellation_score=cats["cancellation"],
            )
        )
        await self.db.commit()

    async def save_cost(self, document_id: int, cost: dict) -> None:
        await self.db.execute(
            delete(CostBreakdown).where(CostBreakdown.document_id == document_id)
        )
        self.db.add(CostBreakdown(document_id=document_id, **cost))
        await self.db.commit()

    async def get_risk(self, document_id: int) -> RiskScore | None:
        r = await self.db.execute(
            select(RiskScore).where(RiskScore.document_id == document_id)
        )
        return r.scalar_one_or_none()

    async def get_cost(self, document_id: int) -> CostBreakdown | None:
        r = await self.db.execute(
            select(CostBreakdown).where(CostBreakdown.document_id == document_id)
        )
        return r.scalar_one_or_none()
