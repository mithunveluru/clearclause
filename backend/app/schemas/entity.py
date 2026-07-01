from datetime import datetime

from pydantic import BaseModel


class EntityOut(BaseModel):
    entity_type: str
    entity_value: str
    confidence: float
    page_number: int | None
    source_text: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class AnalysisOut(BaseModel):
    analyzer_type: str
    status: str
    result: dict | None
    started_at: datetime | None
    finished_at: datetime | None
