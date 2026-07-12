
from app.contracts import Entity
from app.entities.extractors._util import AMOUNT, amount_with_unit

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
            m = AMOUNT.search(window)
            if m:
                out.append(
                    Entity(
                        entity_type=entity_type,
                        entity_value=amount_with_unit(m),
                        confidence=0.7,
                        source_text=window.strip(),
                    )
                )
        return out
