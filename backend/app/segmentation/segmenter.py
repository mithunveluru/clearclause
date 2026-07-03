"""Turn ordered OCR blocks into normalized, lightly-classified clauses.

Stdlib only. The clause_type here is a coarse hint for grouping/UX; the precise,
explainable issue detection happens in the Phase 6 rules engine.
"""
import re
import unicodedata
from collections import OrderedDict

# clause_type -> keywords; order is priority (penalty before fee, so "late payment charge" wins)
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


def split_clauses(text: str) -> list[str]:
    clauses = []
    for part in _SENTENCE_SPLIT.split(text):
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
