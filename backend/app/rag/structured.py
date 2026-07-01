"""Layer 2 — Structured retrieval: answer entity questions directly from SQL.

Queries the entities and findings tables instead of going through embeddings.
Called when intent == 'structured' to avoid sending simple factual questions
through the LLM at all.
"""
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.entity_repo import EntityRepository
from app.repositories.finding_repo import FindingRepository

# entity_type keywords that map to question terms
_TERM_TO_TYPES: dict[str, list[str]] = {
    "interest": ["interest_rate", "rate", "apr"],
    "emi": ["emi", "installment", "monthly_payment"],
    "processing fee": ["processing_fee"],
    "foreclosure": ["foreclosure_charge", "prepayment_penalty"],
    "late fee": ["late_fee", "penalty_fee"],
    "deposit": ["security_deposit", "deposit"],
    "rent": ["rent", "monthly_rent"],
    "annual fee": ["annual_fee"],
    "credit limit": ["credit_limit"],
    "tenure": ["tenure", "loan_term", "term"],
    "loan amount": ["loan_amount", "principal"],
    "landlord": ["landlord", "lessor"],
    "tenant": ["tenant", "lessee"],
    "lender": ["lender", "bank"],
    "borrower": ["borrower"],
    "survey number": ["survey_number"],
    "extent": ["extent", "area"],
    "owner": ["owner"],
    "village": ["village"],
    "taluk": ["taluk"],
    "district": ["district"],
    "billing cycle": ["billing_cycle"],
    "overlimit": ["overlimit_fee"],
    "minimum due": ["minimum_due"],
    "cash advance": ["cash_advance_fee"],
    "renewal fee": ["renewal_fee"],
}


class StructuredRetriever:
    """Retrieve extracted entities by matching question terms to entity types."""

    def __init__(self, db: AsyncSession):
        self.entities = EntityRepository(db)
        self.findings = FindingRepository(db)

    async def retrieve(self, document_id: int, question: str) -> str | None:
        """Return a formatted string of relevant entity facts, or None if nothing matches."""
        q = question.lower()
        wanted: set[str] = set()
        for term, types in _TERM_TO_TYPES.items():
            if term in q:
                wanted.update(types)

        if not wanted:
            return None

        rows = await self.entities.list_for_document(document_id)
        matched = [
            r for r in rows
            if any(t in (r.entity_type or "").lower() for t in wanted)
        ]
        if not matched:
            return None

        lines = [f"- {r.entity_type}: {r.entity_value}" for r in matched]
        return "Extracted document facts:\n" + "\n".join(lines)
