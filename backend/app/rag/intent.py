"""Rule-based intent detection — routes Q&A queries to the right retrieval layer.

structured  → question asks about a specific extracted entity value (SQL)
knowledge   → question asks about regulations, rights, what's legal
semantic    → everything else (clause search)
"""

_STRUCTURED_TERMS = frozenset({
    "interest rate", "emi", "processing fee", "foreclosure", "late fee",
    "penalty", "deposit", "security deposit", "rent", "monthly rent",
    "tenure", "term", "loan amount", "principal", "annual fee",
    "minimum due", "credit limit", "survey number", "extent", "owner",
    "landlord", "tenant", "lender", "borrower", "billing cycle",
    "renewal fee", "cash advance", "overlimit", "taluk", "district",
    "subdivision", "village", "classification",
})

_KNOWLEDGE_TERMS = frozenset({
    "legal", "law", "allowed", "illegal", "regulation", "rules", "right",
    "rights", "rbi", "rera", "irdai", "consumer protection", "act",
    "guideline", "mandatory", "maximum", "limit", "cap", "permitted",
    "refund", "dispute", "complaint", "ombudsman", "penalty limit",
    "fair", "unfair", "reasonable", "entitled", "obligation",
})


def detect_intent(question: str) -> str:
    """Returns 'structured', 'knowledge', or 'semantic'."""
    q = question.lower()
    if any(term in q for term in _STRUCTURED_TERMS):
        return "structured"
    if any(term in q for term in _KNOWLEDGE_TERMS):
        return "knowledge"
    return "semantic"
