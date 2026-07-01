import re

from app.contracts import Entity

_NUM = re.compile(r"([\d,]{3,}(?:\.\d+)?)")
_DUR = re.compile(r"(\d+)\s*(month|year|day)s?", re.I)


def _money_near(low: str, anchors: list[str], window: int = 60) -> str | None:
    for a in anchors:
        i = low.find(a)
        if i >= 0:
            m = _NUM.search(low[i : i + window])
            if m and float(m.group(1).replace(",", "")) >= 1000:
                return m.group(1).replace(",", "")
    return None


def _dur_near(low: str, anchors: list[str], window: int = 50) -> str | None:
    for a in anchors:
        i = low.find(a)
        if i >= 0:
            m = _DUR.search(low[i : i + window])
            if m:
                return f"{m.group(1)} {m.group(2)}s"
    return None


class RentalEntityExtractor:
    def extract(self, text: str) -> list[Entity]:
        low = text.lower()
        out: list[Entity] = []

        def add(etype: str, value: str | None, conf: float = 0.7) -> None:
            if value:
                out.append(Entity(entity_type=etype, entity_value=value, confidence=conf))

        add("rent_amount", _money_near(low, ["monthly rent", "rent is", "rent of"]))
        add("deposit_amount", _money_near(low, ["security deposit", "deposit is", "deposit of"]))
        add("lease_duration", _dur_near(low, ["lease duration", "lease period", "lease", "duration"]))
        add("lock_in_period", _dur_near(low, ["lock-in", "lock in"]))
        add("notice_period", _dur_near(low, ["notice"]))
        if "maintenance" in low or "repair" in low:
            add("maintenance_responsibility", "specified", 0.5)
        if "terminat" in low:
            add("termination_clause", "present", 0.5)
        return out
