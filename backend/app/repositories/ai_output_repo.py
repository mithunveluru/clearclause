from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ai_output import AIOutput


class AIOutputRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_hash(self, document_id: int, kind: str, input_hash: str) -> AIOutput | None:
        r = await self.db.execute(
            select(AIOutput).where(
                AIOutput.document_id == document_id,
                AIOutput.kind == kind,
                AIOutput.input_hash == input_hash,
            )
        )
        return r.scalar_one_or_none()

    async def latest(self, document_id: int, kind: str) -> AIOutput | None:
        r = await self.db.execute(
            select(AIOutput)
            .where(AIOutput.document_id == document_id, AIOutput.kind == kind)
            .order_by(AIOutput.id.desc())
            .limit(1)
        )
        return r.scalar_one_or_none()

    async def save(
        self, document_id: int, kind: str, content: str, model: str | None,
        input_hash: str, finding_id: int | None = None,
    ) -> AIOutput:
        out = AIOutput(
            document_id=document_id, kind=kind, content=content, model=model,
            input_hash=input_hash, finding_id=finding_id,
        )
        self.db.add(out)
        await self.db.commit()
        await self.db.refresh(out)
        return out
