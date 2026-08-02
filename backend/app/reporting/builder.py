"""Assemble the structured report summary (the stored summary_json)."""

_SEV_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}


def build_summary(
    doc: dict,
    findings: list[dict],
    risk: dict,
    cost: dict,
    key_dates: list[dict] | None = None,
) -> dict:
    ordered = sorted(findings, key=lambda f: _SEV_ORDER.get(f["severity"], 9))
    questions = list(dict.fromkeys(f["action_text"] for f in ordered))[:6]
    return {
        "document": doc,
        "key_dates": key_dates or [],
        "score": {
            "total": risk["total"],
            "band": risk["band"],
            "summary": risk["summary"],
            "breakdown": risk["breakdown"],
        },
        "cost": cost,
        "findings": ordered,
        "top_findings": ordered[:3],
        "questions": questions,
        "high_risk": risk["band"] in ("High", "Critical"),
    }
