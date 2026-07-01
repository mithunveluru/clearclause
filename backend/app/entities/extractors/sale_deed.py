from app.contracts import Entity
from app.entities.extractors._util import after_label, num_near


class SaleDeedEntityExtractor:
    def extract(self, text: str) -> list[Entity]:
        low = text.lower()
        out: list[Entity] = []

        def add(etype: str, value: str | None) -> None:
            if value:
                out.append(Entity(entity_type=etype, entity_value=value, confidence=0.7))

        add("buyer_name", after_label(text, low, ["buyer name", "purchaser", "buyer"]))
        add("seller_name", after_label(text, low, ["seller name", "vendor", "seller"]))
        add("survey_number", after_label(text, low, ["survey number", "survey no"]))
        add("sale_consideration", num_near(low, ["sale consideration", "consideration", "sale price"]))
        add("advance_amount", num_near(low, ["advance"]))
        add("registration_date", after_label(text, low, ["registration date", "date of registration"]))
        add("possession_date", after_label(text, low, ["possession date", "date of possession"]))
        return out
