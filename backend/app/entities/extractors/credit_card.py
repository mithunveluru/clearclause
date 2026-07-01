import re

from app.contracts import Entity
from app.entities.extractors._util import num_near

# A percentage near "interest", with an optional period qualifier.
_RATE = re.compile(
    r"(\d+(?:\.\d+)?)\s*(?:%|percent)\s*"
    r"(per\s*month|p\.?\s*m\.?|monthly|per\s*annum|p\.?\s*a\.?|per\s*year|annually)?",
    re.I,
)


def interest_apr(low: str) -> float | None:
    """Annualized interest rate (%) found near 'interest'. Requires an explicit
    percentage (so a stray amount like 'Rs 45,000' is never read as a rate), and
    multiplies monthly-quoted rates by 12."""
    i = low.find("interest")
    if i < 0:
        return None
    m = _RATE.search(low[i : i + 80])
    if not m:
        return None
    val = float(m.group(1))
    period = (m.group(2) or "").lower()
    if "month" in period or period.replace(".", "").replace(" ", "") == "pm":
        val *= 12
    return round(val, 2)


class CreditCardEntityExtractor:
    def extract(self, text: str) -> list[Entity]:
        low = text.lower()
        out: list[Entity] = []

        def add(etype: str, value: str | None) -> None:
            if value:
                out.append(Entity(entity_type=etype, entity_value=value, confidence=0.7))

        add("annual_fee", num_near(low, ["annual fee"]))
        add("late_payment_fee", num_near(low, ["late payment fee", "late fee"]))
        apr = interest_apr(low)
        add("interest_rate", f"{apr:g}% p.a." if apr is not None else None)
        add("minimum_due", num_near(low, ["minimum due", "minimum amount due"]))
        add("overlimit_fee", num_near(low, ["overlimit fee", "over limit fee", "over-limit"]))
        add("cash_advance_fee", num_near(low, ["cash advance"]))
        return out
