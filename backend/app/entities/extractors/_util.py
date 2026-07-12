import re

_NUM = re.compile(r"([\d,]+(?:\.\d+)?)")

# Keeps the unit with the number. Dropping it rendered "Processing Fee: 2.5" in the
# UI — 2.5 percent or 2.5 rupees? On a document about money, an unlabelled number is
# not a fact, it's a guess the reader has to make.
AMOUNT = re.compile(
    r"(?:rs\.?|inr|₹)\s*(?P<money>[\d,]+(?:\.\d+)?)"
    r"|(?P<pct>[\d,]+(?:\.\d+)?)\s*(?:percent|%)"
    r"|(?P<rupees>[\d,]+(?:\.\d+)?)\s*rupees",
    re.I,
)


def amount_with_unit(match: re.Match) -> str:
    """Render an AMOUNT match as the reader should see it: '2.5%' or '₹50,000'."""
    if match.group("pct"):
        return f"{match.group('pct')}%"
    return f"₹{match.group('money') or match.group('rupees')}"


_BOUNDARY = re.compile(r"\.\s|\.$|\n")


def after_label(text: str, low: str, anchors: list[str], window: int = 70) -> str | None:
    """Value following a 'Label: value' style anchor, up to end of line/sentence.

    Cuts only on a sentence boundary ('. ' or trailing '.') or newline, so internal
    decimals/dotted ids (e.g. '0.45 hectares', '123/4.5') are preserved.
    """
    for a in anchors:
        i = low.find(a)
        if i >= 0:
            seg = text[i + len(a) : i + len(a) + window].lstrip(" :-\t")
            val = _BOUNDARY.split(seg, maxsplit=1)[0].strip()
            if val:
                return val[:80]
    return None


def num_near(low: str, anchors: list[str], window: int = 60) -> str | None:
    for a in anchors:
        i = low.find(a)
        if i >= 0:
            m = _NUM.search(low[i : i + window])
            if m:
                return m.group(1).replace(",", "")
    return None


def present(low: str, *keywords: str) -> bool:
    return any(k in low for k in keywords)
