"""Assembles the Interactive Document Explorer from existing pipeline outputs.

No new AI calls — purely aggregates findings, entities, clauses, and scores
into a navigable, section-based structure the frontend consumes.
"""
import asyncio

from app.repositories.analyzer_run_repo import AnalyzerRunRepository
from app.repositories.clause_repo import ClauseRepository
from app.repositories.entity_repo import EntityRepository
from app.repositories.finding_repo import FindingRepository
from app.repositories.score_repo import ScoreRepository
from app.schemas.explorer import (
    ExplorerClauseItem,
    ExplorerOut,
    ExplorerSection,
    FinancialImpact,
    SuggestedQuestion,
    TimelineEvent,
    WalkthroughStep,
)
from app.scoring.risk import band as risk_band

# section_id → (label, lucide-icon-name, summary)
_SECTION_DEFS: dict[str, tuple[str, str, str]] = {
    "financial_terms": (
        "Financial Terms", "DollarSign",
        "All fees, rates, and costs in this agreement",
    ),
    "penalties": (
        "Penalties & Charges", "AlertTriangle",
        "What you pay for late payments or early exit",
    ),
    "hidden_charges": (
        "Hidden Charges", "Eye",
        "Undisclosed fees and bundled add-ons you didn't explicitly choose",
    ),
    "rights": (
        "Rights & Consent", "Shield",
        "What you are explicitly agreeing to — and what you can refuse",
    ),
    "cancellation": (
        "Cancellation & Renewal", "RotateCcw",
        "How and when you can exit or stop this agreement",
    ),
}

_ISSUE_TO_SECTION: dict[str, str] = {
    "processing_fee": "financial_terms",
    "service_fee": "financial_terms",
    "vague_pricing_revision": "financial_terms",
    "missing_cost_disclosure": "financial_terms",
    "late_fee": "penalties",
    "prepayment_penalty": "penalties",
    "foreclosure_charge": "penalties",
    "hidden_fee": "hidden_charges",
    "bundled_addon": "hidden_charges",
    "auto_renew_trap": "cancellation",
    "hard_cancellation": "cancellation",
    "implied_consent": "rights",
}

_SEVERITY_ORDER = {"low": 1, "medium": 2, "high": 3, "critical": 4}

_ENTITY_TIMELINE: dict[str, tuple[str, str, str]] = {
    "lock_in_period":           ("period",      "Lock-in Period",            "Cannot exit before this duration ends"),
    "notice_period":            ("deadline",    "Required Notice Period",    "Must notify the other party this far in advance"),
    "lease_duration":           ("period",      "Lease Duration",            "Total duration of this agreement"),
    "loan_tenure":              ("period",      "Loan Tenure",               "Duration over which you repay this loan"),
    "rent_amount":              ("payment",     "Monthly Rent",              "Due every month for the lease duration"),
    "deposit_amount":           ("payment",     "Security Deposit",          "Paid upfront; refundable on exit"),
    "processing_fee":           ("payment",     "Processing Fee",            "Deducted from loan before disbursal"),
    "interest_rate":            ("recurring",   "Interest Rate (Annual)",    "Applied to outstanding balance each year"),
    "prepayment_penalty":       ("payment",     "Prepayment Penalty",        "Charged if you repay before tenure ends"),
    "foreclosure_charge":       ("payment",     "Foreclosure Charge",        "Charged for closing the loan early"),
    "late_fee":                 ("payment",     "Late Payment Fee",          "Triggered if payment is overdue"),
    "maintenance_responsibility": ("obligation","Maintenance Responsibility","Responsibility specified in agreement"),
    "termination_clause":       ("rights",      "Termination Clause",        "Conditions under which the agreement can end"),
}

def timeline_entries(entities) -> list[dict[str, str]]:
    """The dated/periodic terms, as plain dicts. Shared with the PDF report so the two
    surfaces cannot drift apart on which entities count as timeline events."""
    return [
        {
            "label": _ENTITY_TIMELINE[e.entity_type][1],
            "value": e.entity_value,
            "description": _ENTITY_TIMELINE[e.entity_type][2],
        }
        for e in entities
        if e.entity_type in _ENTITY_TIMELINE and e.entity_value
    ]


_FINANCIAL_UPFRONT = {"processing_fee", "deposit_amount"}
_FINANCIAL_RECURRING = {"rent_amount", "interest_rate"}
_FINANCIAL_PENALTIES = {"late_fee", "prepayment_penalty", "foreclosure_charge"}

_ISSUE_QUESTIONS: dict[str, tuple[str, str]] = {
    "processing_fee":        ("Can the processing fee be reduced or waived?", "cost"),
    "service_fee":           ("Is the service fee mandatory, or can it be removed?", "cost"),
    "late_fee":              ("What is the exact grace period before late fees apply?", "cost"),
    "prepayment_penalty":    ("Can I repay the loan early without any penalty?", "penalty"),
    "foreclosure_charge":    ("What is the exact charge if I close this loan before the tenure ends?", "penalty"),
    "auto_renew_trap":       ("How do I cancel before the auto-renewal date, and what is the exact deadline?", "cancellation"),
    "hard_cancellation":     ("What are the exact steps and costs to cancel this agreement?", "cancellation"),
    "bundled_addon":         ("Can I opt out of the bundled insurance or add-on and pay a lower price?", "cost"),
    "implied_consent":       ("Where exactly do I actively agree to each term, rather than having consent assumed?", "rights"),
    "vague_pricing_revision":("How much notice will I receive before any fees or rates are changed?", "rights"),
    "hidden_fee":            ("Can you provide a complete written list of every charge I will be asked to pay?", "cost"),
    "missing_cost_disclosure": ("What is the total amount I will pay over the full term, including all fees?", "cost"),
}

# Included only when the matching section has findings
_WALKTHROUGH_TEMPLATES = [
    (1, "What you'll pay",      "financial_terms", "Review all costs, fees, and rates in this agreement.",
     "These are the actual charges — compare with what was advertised to you."),
    (2, "Penalties to watch",   "penalties",       "Understand what happens if you pay late or want to exit early.",
     "Late or early-exit penalties can often exceed the original benefit. Know the exact amounts."),
    (3, "Hidden charges",       "hidden_charges",  "Look out for undisclosed fees and bundled add-ons.",
     "Bundled products or vague 'other charges' wording can cost thousands over time."),
    (4, "Your rights",          "rights",          "Know exactly what you are and aren't agreeing to.",
     "Any clause that assumes your consent without an explicit choice is a red flag."),
    (5, "Cancellation terms",   "cancellation",    "Understand how and when you can cancel or exit.",
     "If cancellation is restricted or unclear, you could be locked in indefinitely."),
    (6, "Questions to ask",     "questions",       "Use these questions to negotiate better terms before signing.",
     "Asking the right questions before signing can reveal deal-breaking terms."),
]

# Entity highlight priority order
_HIGHLIGHT_PRIORITY = [
    "interest_rate", "processing_fee", "rent_amount", "deposit_amount",
    "late_fee", "foreclosure_charge", "lock_in_period", "notice_period",
    "prepayment_penalty", "lease_duration", "loan_tenure",
]


class ExplorerService:
    def __init__(
        self,
        findings: FindingRepository,
        entities: EntityRepository,
        clauses: ClauseRepository,
        scores: ScoreRepository,
        analyzer_runs: AnalyzerRunRepository,
    ):
        self.findings = findings
        self.entities = entities
        self.clauses = clauses
        self.scores = scores
        self.analyzer_runs = analyzer_runs

    async def build(
        self,
        document_id: int,
        doc_type: str | None = None,
        document_family: str | None = None,
    ) -> ExplorerOut:
        findings_list, entities_list, score, run, clauses_list = await asyncio.gather(
            self.findings.list_for_document(document_id),
            self.entities.list_for_document(document_id),
            self.scores.get_risk(document_id),
            self.analyzer_runs.latest(document_id),
            self.clauses.list_for_document(document_id),
        )

        clause_texts: dict[int, str] = {c.id: c.normalized_text for c in clauses_list}
        clause_pages: dict[int, int | None] = {c.id: c.page_number for c in clauses_list}

        sections = self._sections(findings_list, clause_texts, clause_pages)
        financial = self._financial(entities_list, findings_list)
        timeline = self._timeline(entities_list)
        questions = self._questions(findings_list)
        section_ids = {s.id for s in sections}
        walkthrough = self._walkthrough(section_ids)
        highlights = self._highlights(entities_list)

        total = score.total_score if score else None
        r_band = risk_band(total) if total is not None else None

        result_json = (run.result_json or {}) if run else {}
        summary = result_json.get("summary")
        strengths = result_json.get("strengths") or []
        recommendations = result_json.get("recommendations") or []

        return ExplorerOut(
            doc_id=document_id,
            doc_type=doc_type,
            document_family=document_family,
            risk_score=total,
            risk_band=r_band,
            sections=sections,
            financial_impact=financial,
            timeline=timeline,
            suggested_questions=questions,
            walkthrough=walkthrough,
            entity_highlights=highlights,
            analysis_summary=summary,
            strengths=strengths,
            recommendations=recommendations,
        )

    def _sections(self, findings, clause_texts, clause_pages) -> list[ExplorerSection]:
        grouped: dict[str, list] = {}
        for f in findings:
            sid = _ISSUE_TO_SECTION.get(f.issue_type, "other")
            grouped.setdefault(sid, []).append(f)

        out = []
        for sid, (label, icon, summary) in _SECTION_DEFS.items():
            items = grouped.get(sid, [])
            if not items:
                continue
            max_sev = "low"
            clauses: list[ExplorerClauseItem] = []
            for f in items:
                clauses.append(ExplorerClauseItem(
                    clause_id=f.clause_id,
                    finding_id=f.id,
                    original_text=clause_texts.get(f.clause_id) if f.clause_id else None,
                    plain_english=f.explanation,
                    why_it_matters=f.impact,
                    action_text=f.action_text,
                    issue_type=f.issue_type,
                    risk_level=f.severity,
                    confidence=f.confidence,
                    page_number=clause_pages.get(f.clause_id) if f.clause_id else None,
                ))
                if _SEVERITY_ORDER.get(f.severity, 0) > _SEVERITY_ORDER.get(max_sev, 0):
                    max_sev = f.severity
            out.append(ExplorerSection(
                id=sid, label=label, icon=icon, risk_level=max_sev,
                item_count=len(clauses), clauses=clauses, summary=summary,
            ))
        return out

    def _financial(self, entities, findings) -> FinancialImpact:
        upfront, recurring, penalties, hidden = [], [], [], []
        for e in entities:
            if not e.entity_value:
                continue
            item = {"label": e.entity_type.replace("_", " ").title(), "value": e.entity_value}
            if e.entity_type in _FINANCIAL_UPFRONT:
                upfront.append(item)
            elif e.entity_type in _FINANCIAL_RECURRING:
                recurring.append(item)
            elif e.entity_type in _FINANCIAL_PENALTIES:
                penalties.append(item)
        for f in findings:
            if f.issue_type in ("hidden_fee", "bundled_addon"):
                hidden.append(f.explanation)
        return FinancialImpact(
            upfront_costs=upfront,
            recurring_costs=recurring,
            penalties=penalties,
            hidden_risks=hidden,
            total_note=None,
        )

    def _timeline(self, entities) -> list[TimelineEvent]:
        events = []
        for e in entities:
            if e.entity_type not in _ENTITY_TIMELINE or not e.entity_value:
                continue
            event_type, label, desc = _ENTITY_TIMELINE[e.entity_type]
            events.append(TimelineEvent(
                label=label, value=e.entity_value, entity_type=e.entity_type,
                event_type=event_type, description=desc,
            ))
        return events

    def _questions(self, findings) -> list[SuggestedQuestion]:
        seen: set[str] = set()
        questions = []
        for f in sorted(findings, key=lambda x: _SEVERITY_ORDER.get(x.severity, 0), reverse=True):
            if f.issue_type in seen or f.issue_type not in _ISSUE_QUESTIONS:
                continue
            seen.add(f.issue_type)
            q, cat = _ISSUE_QUESTIONS[f.issue_type]
            questions.append(SuggestedQuestion(question=q, category=cat, finding_id=f.id))
        return questions

    def _walkthrough(self, section_ids: set[str]) -> list[WalkthroughStep]:
        steps = []
        num = 1
        for _, title, sid, desc, insight in _WALKTHROUGH_TEMPLATES:
            if sid == "questions" or sid in section_ids:
                steps.append(WalkthroughStep(
                    step=num, title=title, section_id=sid,
                    description=desc, insight=insight,
                ))
                num += 1
        return steps

    def _highlights(self, entities) -> list[dict[str, str]]:
        entity_map = {e.entity_type: e for e in entities}
        return [
            {"label": k.replace("_", " ").title(), "value": entity_map[k].entity_value, "type": k}
            for k in _HIGHLIGHT_PRIORITY
            if k in entity_map and entity_map[k].entity_value
        ]
