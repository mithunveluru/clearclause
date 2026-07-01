import re

_NUM = re.compile(r"([\d,]+(?:\.\d+)?)")


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
