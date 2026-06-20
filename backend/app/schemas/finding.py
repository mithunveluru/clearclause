from datetime import datetime

from pydantic import BaseModel


class FindingOut(BaseModel):
    id: int
    clause_id: int | None
    issue_type: str
    severity: str
    confidence: float
    explanation: str
    action_text: str
    created_at: datetime
    clause_text: str | None = None

    model_config = {"from_attributes": True}
