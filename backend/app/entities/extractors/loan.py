import re

from app.contracts import Entity

_AMOUNT = re.compile(
    r"(?:rs\.?|inr|₹)\s*([\d,]+(?:\.\d+)?)|([\d,]+(?:\.\d+)?)\s*(?:rupees|percent|%)",
    re.I,
)

# entity_type -> keyword that anchors the value
_SPECS = [
    ("processing_fee", "processing fee"),
    ("late_fee", "late payment"),
    ("foreclosure_charge", "foreclosure"),
    ("prepayment_penalty", "prepayment"),
    ("interest_rate", "interest rate"),
]


class LoanEntityExtractor:
    def extract(self, text: str) -> list[Entity]:
        low = text.lower()
        out: list[Entity] = []
        for entity_type, keyword in _SPECS:
            idx = low.find(keyword)
            if idx < 0:
                continue
            window = text[idx : idx + 70]
            m = _AMOUNT.search(window)
            if m:
                out.append(
                    Entity(
                        entity_type=entity_type,
                        entity_value=(m.group(1) or m.group(2)),
                        confidence=0.7,
                        source_text=window.strip(),
                    )
                )
        return out
