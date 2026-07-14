from app.contracts import Entity

# entity_type -> anchor keywords; value is the clause snippet
_SPECS = [
    ("renewal_term", ("auto-renew", "automatically renew", "renews", "recurring")),
    ("trial_period", ("free trial", "trial")),
    ("cancellation_term", ("cannot be cancelled", "cancel")),
]


class SubscriptionEntityExtractor:
    def extract(self, text: str) -> list[Entity]:
        low = text.lower()
        out: list[Entity] = []
        for entity_type, keywords in _SPECS:
            for kw in keywords:
                idx = low.find(kw)
                if idx >= 0:
                    snippet = text[idx : idx + 90].strip()
                    out.append(
                        Entity(entity_type=entity_type, entity_value=snippet,
                               confidence=0.5, source_text=snippet)
                    )
                    break
        return out
