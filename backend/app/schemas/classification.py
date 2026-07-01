from datetime import datetime

from pydantic import BaseModel


class SecondaryCandidateOut(BaseModel):
    classified_type: str
    confidence: float


class ClassificationOut(BaseModel):
    classified_type: str
    document_family: str | None
    confidence: float
    signals: dict[str, int]
    secondary_candidates: list[SecondaryCandidateOut]
    routing_action: str  # auto | confirm | manual
    created_at: datetime


class ClassificationOverrideIn(BaseModel):
    classified_type: str
