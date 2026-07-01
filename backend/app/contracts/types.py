"""Typed contracts passed between pipeline stages (Pydantic v2).

These are the stable seams: classifier -> entities -> analyzer -> score -> chunk
-> retrieve -> AI. Persistence models map to/from these; stages depend only on these.
"""
from pydantic import BaseModel, Field


class SecondaryCandidate(BaseModel):
    classified_type: str
    confidence: float


class ClassificationResult(BaseModel):
    classified_type: str
    document_family: str | None = None
    confidence: float = Field(ge=0.0, le=1.0)
    signals: dict[str, int] = Field(default_factory=dict)
    secondary_candidates: list[SecondaryCandidate] = Field(default_factory=list)
    # routing_action: auto (≥AUTO_THRESHOLD), confirm (≥CONFIRM_THRESHOLD), manual (<CONFIRM)
    routing_action: str = "auto"


class Entity(BaseModel):
    entity_type: str
    entity_value: str
    confidence: float = 1.0
    page_number: int | None = None
    source_text: str | None = None


class FindingDraft(BaseModel):
    """A finding before persistence — same shape the rule engine already emits."""

    issue_type: str
    severity: str
    confidence: float
    explanation: str
    impact: str | None = None
    action_text: str
    clause_id: int | None = None
    clause_text: str | None = None


class HeadlineMetric(BaseModel):
    """The analyzer's signature score, e.g. 'Rental Fairness Score' 0-100 + band."""

    name: str
    value: int
    band: str


class AnalyzerResult(BaseModel):
    analyzer_type: str
    document_family: str
    entities: list[Entity] = Field(default_factory=list)
    findings: list[FindingDraft] = Field(default_factory=list)
    headline_metric: HeadlineMetric | None = None
    strengths: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    summary: str | None = None


class Chunk(BaseModel):
    chunk_index: int
    page_number: int | None = None
    section_name: str | None = None
    text: str


class Citation(BaseModel):
    page: int | None = None
    section: str | None = None
    snippet: str


class KnowledgeRef(BaseModel):
    title: str
    category: str


class QAAnswer(BaseModel):
    answer: str
    citations: list[Citation] = Field(default_factory=list)
    regulation_refs: list[KnowledgeRef] = Field(default_factory=list)
    follow_up_questions: list[str] = Field(default_factory=list)
    confidence_note: str
