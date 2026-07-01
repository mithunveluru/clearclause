from pydantic import BaseModel


class ExplorerClauseItem(BaseModel):
    clause_id: int | None
    finding_id: int | None
    original_text: str | None
    plain_english: str
    why_it_matters: str | None
    action_text: str
    issue_type: str
    risk_level: str
    confidence: float
    page_number: int | None


class ExplorerSection(BaseModel):
    id: str
    label: str
    icon: str
    risk_level: str
    item_count: int
    clauses: list[ExplorerClauseItem]
    summary: str


class TimelineEvent(BaseModel):
    label: str
    value: str
    entity_type: str
    event_type: str  # payment | period | deadline | obligation | rights
    description: str


class SuggestedQuestion(BaseModel):
    question: str
    category: str  # cost | penalty | cancellation | rights
    finding_id: int | None


class WalkthroughStep(BaseModel):
    step: int
    title: str
    description: str
    section_id: str
    insight: str


class FinancialImpact(BaseModel):
    upfront_costs: list[dict[str, str]]
    recurring_costs: list[dict[str, str]]
    penalties: list[dict[str, str]]
    hidden_risks: list[str]
    total_note: str | None


class ExplorerOut(BaseModel):
    doc_id: int
    doc_type: str | None
    document_family: str | None
    risk_score: int | None
    risk_band: str | None
    sections: list[ExplorerSection]
    financial_impact: FinancialImpact
    timeline: list[TimelineEvent]
    suggested_questions: list[SuggestedQuestion]
    walkthrough: list[WalkthroughStep]
    entity_highlights: list[dict[str, str]]
    analysis_summary: str | None
    strengths: list[str]
    recommendations: list[str]
