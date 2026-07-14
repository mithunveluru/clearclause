"""Best-effort true-cost extraction from clause text.

ponytail: percentages are stored but never summed — that needs a principal we
don't reliably have. Upgrade path: resolve principal, then compound.
"""
import re

_FIELD_FOR_ISSUE = {
    "processing_fee": "processing_fee",
    "late_fee": "late_fee",
    "auto_renew_trap": "renewal_fee",
    "foreclosure_charge": "foreclosure_charge",
}

_CUR = re.compile(r"(?:rs\.?|inr|₹)\s*([\d,]+(?:\.\d+)?)|([\d,]+(?:\.\d+)?)\s*(?:rupees|rs\b)", re.I)
_PCT = re.compile(r"(\d+(?:\.\d+)?)\s*(?:%|percent|per\s*cent)", re.I)
_RATE = re.compile(
    r"interest[^.]{0,40}?(\d+(?:\.\d+)?)\s*(?:%|percent)"
    r"|(\d+(?:\.\d+)?)\s*(?:%|percent)[^.]{0,20}?(?:per\s+annum|p\.?\s*a\.?)",
    re.I,
)


def _amount(text: str) -> tuple[float | None, str | None]:
    m = _CUR.search(text)
    if m:
        return float((m.group(1) or m.group(2)).replace(",", "")), "amount"
    m = _PCT.search(text)
    if m:
        return float(m.group(1)), "pct"
    return None, None


def _headline_rate(texts: list[str]) -> float | None:
    for t in texts:
        m = _RATE.search(t)
        if m:
            return float(m.group(1) or m.group(2))
    return None


def estimate_cost(findings: list[dict], clause_texts: list[str]) -> dict:
    out = {
        "headline_rate": None,
        "processing_fee": None,
        "late_fee": None,
        "renewal_fee": None,
        "foreclosure_charge": None,
        "estimated_true_cost": None,
    }
    true_cost, have_amount = 0.0, False
    for f in findings:
        field = _FIELD_FOR_ISSUE.get(f["issue_type"])
        if not field or out[field] is not None:
            continue
        val, kind = _amount(f.get("clause_text") or "")
        out[field] = val
        if kind == "amount" and val:
            true_cost += val
            have_amount = True
    out["headline_rate"] = _headline_rate(clause_texts)
    out["estimated_true_cost"] = round(true_cost, 2) if have_amount else None
    return out
