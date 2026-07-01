from app.contracts import Entity
from app.entities.extractors._util import after_label


class PattaEntityExtractor:
    def extract(self, text: str) -> list[Entity]:
        low = text.lower()
        out: list[Entity] = []

        def add(etype: str, value: str | None) -> None:
            if value:
                out.append(Entity(entity_type=etype, entity_value=value, confidence=0.7))

        add("patta_number", after_label(text, low, ["patta number", "patta no"]))
        add("owner_name", after_label(text, low, ["owner name", "name of the owner", "owner"]))
        add("survey_number", after_label(text, low, ["survey number", "survey no"]))
        add("village", after_label(text, low, ["village"]))
        add("taluk", after_label(text, low, ["taluk"]))
        add("district", after_label(text, low, ["district"]))
        add("land_classification", after_label(text, low, ["land classification", "classification"]))
        add("extent", after_label(text, low, ["extent"]))
        add("subdivision_number", after_label(text, low, ["subdivision", "sub division", "sub-division"]))
        return out
