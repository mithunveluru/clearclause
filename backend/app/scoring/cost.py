"""Best-effort true-cost extraction from clause text.

Percentages are stored but never summed; that needs a principal the document
does not reliably state. Resolve the principal first, then compound.

Each fee is stored with the unit it was written in. Without that, "4" is a number
nobody can read: Rs 4 and 4% of a loan are different by five orders of magnitude,
and the report used to print the bare figure and hope the reader guessed right.
"""
import re

# One splitter for the whole codebase: this module had its own, which split "Rs. 500"
# and discarded the very amount it was looking for.
from app.segmentation.segmenter import split_sentences

INR = "inr"
PERCENT = "percent"

# Fees whose written form genuinely varies between documents
AMBIGUOUS_FIELDS = ("processing_fee", "late_fee", "renewal_fee", "foreclosure_charge")
# headline_rate is a percentage by construction, estimated_true_cost rupees by
# construction, so neither needs a stored unit
COST_FIELDS = (
    "headline_rate",
    *AMBIGUOUS_FIELDS,
    "estimated_true_cost",
    *(f"{field}_unit" for field in AMBIGUOUS_FIELDS),
)

_FIELD_FOR_ISSUE = {
    "processing_fee": "processing_fee",
    "late_fee": "late_fee",
    "auto_renew_trap": "renewal_fee",
    "foreclosure_charge": "foreclosure_charge",
}

# Wording that locates the sentence a given fee is stated in
_PHRASES_FOR_FIELD = {
    "processing_fee": ("processing fee", "processing charge", "service fee"),
    "late_fee": ("late payment", "late fee", "overdue", "default charge"),
    "renewal_fee": ("renew", "renewal"),
    "foreclosure_charge": ("foreclos", "prepay", "pre-pay", "pre-clos", "early clos"),
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
        return float((m.group(1) or m.group(2)).replace(",", "")), INR
    m = _PCT.search(text)
    if m:
        return float(m.group(1)), PERCENT
    return None, None


# Which fee each phrase names. Fee tables arrive as one unpunctuated run of text
# ("Processing fee 2 percent Late payment charge Rs. 750 Foreclosure charge 4 percent"),
# and there is no sentence boundary in them to find — the only boundary the document
# offers is the point where it starts naming the next fee.
_FIELD_FOR_PHRASE = {
    phrase: field for field, phrases in _PHRASES_FOR_FIELD.items() for phrase in phrases
}


def _clip_at_the_next_fee(sentence: str, field: str) -> str:
    """The span of this sentence that belongs to `field` and to no fee after it.

    Clipping only at *another* fee's wording, never at this fee's own: "Late payment:
    overdue amounts attract Rs. 500" names late_fee twice, and cutting at the second
    would throw away the amount.

    ponytail: first-occurrence scan, no overlap handling. A sentence that names fee A,
    then fee B, then returns to A's amount reads as having no amount rather than the
    wrong one — the safe direction for a figure that gets printed as money. Upgrade to
    per-phrase spans if real documents turn out to interleave.
    """
    low = sentence.lower()
    start = min((low.find(p) for p in _PHRASES_FOR_FIELD[field] if p in low), default=0)
    later = [
        i
        for phrase, owner in _FIELD_FOR_PHRASE.items()
        if owner != field and (i := low.find(phrase, start + 1)) != -1
    ]
    return sentence[start : min(later)] if later else sentence[start:]


def _sentence_for(text: str, field: str) -> str:
    """The sentence stating this fee, falling back to the whole block if none names it.

    Segmentation hands back a block that can hold an entire agreement, and the first
    currency figure in such a block belongs to whichever fee happened to appear first.
    That is how a processing fee of "2 percent" was reported as Rs 500 — the rupee
    amount three sentences later belonged to the late payment charge.
    """
    phrases = _PHRASES_FOR_FIELD.get(field, ())
    for sentence in split_sentences(text):
        lowered = sentence.lower()
        if any(phrase in lowered for phrase in phrases):
            return _clip_at_the_next_fee(sentence, field)
    return text


def _headline_rate(texts: list[str]) -> float | None:
    for t in texts:
        m = _RATE.search(t)
        if m:
            return float(m.group(1) or m.group(2))
    return None


def empty_cost() -> dict:
    """A breakdown with nothing extracted — every field, so it maps onto the row."""
    return dict.fromkeys(COST_FIELDS)


def estimate_cost(findings: list[dict], clause_texts: list[str]) -> dict:
    out = empty_cost()
    true_cost, have_amount = 0.0, False
    for f in findings:
        field = _FIELD_FOR_ISSUE.get(f["issue_type"])
        if not field or out[field] is not None:
            continue
        val, unit = _amount(_sentence_for(f.get("clause_text") or "", field))
        out[field], out[f"{field}_unit"] = val, unit
        if unit == INR and val:
            true_cost += val
            have_amount = True
    out["headline_rate"] = _headline_rate(clause_texts)
    out["estimated_true_cost"] = round(true_cost, 2) if have_amount else None
    return out


def cost_dict(cost) -> dict:
    """A stored CostBreakdown row as a plain dict, units included.

    Shared so the PDF and the AI summary read the same fields; a unit added to one
    and forgotten in the other is how a report and a summary end up disagreeing.
    """
    return {field: getattr(cost, field, None) for field in COST_FIELDS} if cost else empty_cost()
