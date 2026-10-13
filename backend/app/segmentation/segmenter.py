"""Turn ordered OCR blocks into normalized, lightly-classified clauses.

Stdlib only. The clause_type here is a coarse hint for grouping/UX; the precise,
explainable issue detection happens in the Phase 6 rules engine.
"""
import re
import unicodedata
from collections import OrderedDict

# clause_type -> keywords; order is priority (penalty before fee)
CLAUSE_KEYWORDS: "OrderedDict[str, tuple[str, ...]]" = OrderedDict(
    [
        ("penalty", ("penalty", "penal", "late payment", "late fee", "default",
                     "overdue", "foreclosure", "prepayment", "pre-payment")),
        ("renewal", ("auto-renew", "auto renew", "autorenew", "renewal", "renews",
                     "recurring", "auto-debit", "auto debit", "autopay", "mandate")),
        ("cancellation", ("cancel", "termination", "terminate", "unsubscribe")),
        ("consent", ("consent", "authorize", "authorise", "deemed", "opt-out", "opt out")),
        ("add_on", ("insurance", "add-on", "add on", "bundle", "bundled")),
        ("fee", ("fee", "charge", "processing", "convenience", "service")),
    ]
)

_NON_PRINTABLE = re.compile(r"[^\x09\x0a\x0d\x20-\x7e]")
_REPEAT_PUNCT = re.compile(r"([.,;:!?])\1+")
_SENTENCE_SPLIT = re.compile(r"(?<=[.;])\s+")

# Periods that abbreviate rather than terminate. This text is full of them, and the
# costly one is "Rs.": splitting there severed "A late payment charge of Rs." from
# "500 per month", so the clause describing the fee no longer contained its figure and
# the fee was reported as having no amount at all.
_ABBREVIATIONS = frozenset(
    """
    rs inr no nos mr mrs ms m/s dr ltd pvt co inc etc viz vs v sec cl art sch ann
    sr jr st rd approx min max fig para cap ref addl asst govt dept
    """.split()
)
_BULLET = re.compile(r"^\s*(?:[-*•·]|\(?[a-z0-9]{1,2}[).])\s+", re.IGNORECASE)
_MIN_CLAUSE_LEN = 8


def normalize_text(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)
    text = (
        text.replace("‘", "'").replace("’", "'")
        .replace("“", '"').replace("”", '"')
    )
    text = re.sub(r"[–—]", "-", text)  # en/em dash -> hyphen
    text = _NON_PRINTABLE.sub(" ", text)
    text = _REPEAT_PUNCT.sub(r"\1", text)  # "fee.." -> "fee."
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def is_heading(text: str) -> bool:
    words = text.split()
    if not (1 <= len(words) <= 8) or text.endswith("."):
        return False
    letters = [c for c in text if c.isalpha()]
    if not letters:
        return False
    upper_ratio = sum(c.isupper() for c in letters) / len(letters)
    return upper_ratio > 0.7 or text.endswith(":")


def _ends_a_sentence(before: str) -> bool:
    """Whether the punctuation ending this half terminates a sentence.

    Only the word before it is consulted. Requiring a capital after it as well read
    "a processing fee of 2 percent; a late payment charge of Rs. 500" as one sentence,
    so the processing fee was reported as Rs 500 — the merge costs the same
    misattribution the split was supposed to prevent. A semicolon never abbreviates,
    and "Rs." is caught by the word before it without help.
    """
    word = before.rsplit(maxsplit=1)[-1].rstrip(".;").lower() if before.split() else ""
    return not (word in _ABBREVIATIONS or len(word) == 1)  # "Rs. 500", "A. Kumar"


def split_sentences(text: str) -> list[str]:
    parts, start = [], 0
    for match in _SENTENCE_SPLIT.finditer(text):
        if _ends_a_sentence(text[start : match.start()]):
            parts.append(text[start : match.start()])
            start = match.end()
    parts.append(text[start:])
    return parts


def split_clauses(text: str) -> list[str]:
    clauses = []
    for part in split_sentences(text):
        part = _BULLET.sub("", part).strip()
        if len(part) >= _MIN_CLAUSE_LEN:
            clauses.append(part)
    return clauses


def classify_clause(text: str) -> str:
    low = text.lower()
    for clause_type, keywords in CLAUSE_KEYWORDS.items():
        if any(kw in low for kw in keywords):
            return clause_type
    return "general"


def segment(blocks: list[tuple[int, str]]) -> list[dict]:
    """blocks: ordered (page_number, raw_block_text). Returns clause dicts."""
    section: str | None = None
    out: list[dict] = []
    for page_number, raw in blocks:
        norm = normalize_text(raw)
        if not norm:
            continue
        if is_heading(norm):
            section = norm.rstrip(":")
            continue
        for clause in split_clauses(norm):
            out.append(
                {
                    "page_number": page_number,
                    "section_name": section,
                    "raw_text": raw,
                    "normalized_text": clause,
                    "clause_type": classify_clause(clause),
                }
            )
    return out
