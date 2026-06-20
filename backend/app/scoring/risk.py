"""Weighted, explainable risk scoring. Weights are the spec's §7 table.

Tunable knobs (CATEGORY_MAX, SEVERITY_POINTS) live here as constants.
"""

# Spec §7 weighting: category -> max contribution to the 0-100 score.
CATEGORY_MAX = {
    "fee_opacity": 20,
    "penalty": 15,
    "renewal": 15,
    "consent": 15,
    "cancellation": 10,
    "bundling": 10,
    "missing": 10,
    "readability": 5,
}

ISSUE_CATEGORY = {
    "processing_fee": "fee_opacity",
    "service_fee": "fee_opacity",
    "hidden_fee": "fee_opacity",
    "vague_pricing_revision": "fee_opacity",
    "late_fee": "penalty",
    "prepayment_penalty": "penalty",
    "foreclosure_charge": "penalty",
    "auto_renew_trap": "renewal",
    "implied_consent": "consent",
    "hard_cancellation": "cancellation",
    "bundled_addon": "bundling",
    "missing_cost_disclosure": "missing",
}

SEVERITY_POINTS = {"low": 3, "medium": 7, "high": 12, "critical": 16}

_SUMMARY_REASON = {
    "fee_opacity": "fees are not clearly disclosed",
    "penalty": "penalty charges are significant",
    "renewal": "it auto-renews and is easy to forget to cancel",
    "consent": "consent is assumed rather than explicitly given",
    "cancellation": "it appears difficult to cancel",
    "bundling": "add-ons are bundled into the cost",
    "missing": "the total cost is not clearly disclosed",
    "readability": "the terms are hard to read",
}


def _readability(texts: list[str]) -> int:
    words = [len(t.split()) for t in texts if t]
    if not words:
        return 0
    avg = sum(words) / len(words)
    return max(0, min(5, int((avg - 10) // 4)))  # ponytail: avg-words proxy; swap for Flesch if needed


def band(total: int) -> str:
    if total < 25:
        return "Low"
    if total < 50:
        return "Moderate"
    if total < 75:
        return "High"
    return "Critical"


def score_findings(findings: list[dict], clause_texts: list[str]) -> dict:
    """findings: dicts with issue_type + severity. Returns category scores + total."""
    cats = {k: 0 for k in CATEGORY_MAX}
    for f in findings:
        cat = ISSUE_CATEGORY.get(f["issue_type"])
        if cat:
            cats[cat] += SEVERITY_POINTS.get(f["severity"], 7)
    cats["readability"] = _readability(clause_texts)
    cats = {k: min(CATEGORY_MAX[k], v) for k, v in cats.items()}
    cats["total"] = min(100, sum(cats.values()))
    return cats


def summarize(cats: dict) -> str:
    total = cats["total"]
    scored = {k: v for k, v in cats.items() if k != "total" and v > 0}
    if not scored:
        return "No significant risks were detected in this document."
    top = max(scored, key=scored.get)
    return f"This document looks {band(total).lower()} risk because {_SUMMARY_REASON[top]}."
