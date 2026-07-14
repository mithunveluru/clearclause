from app.ai.prompts import GROUNDING_SYSTEM, build_summary_prompt
from app.ai.summarizer import AISummarizer

CTX = {
    "type": "loan",
    "score": 45,
    "band": "Moderate",
    "findings": [{"issue": "late_fee", "explanation": "Late payments trigger a penalty."}],
    "entities": [{"type": "processing_fee", "value": "2"}],
}


def test_summary_prompt_contains_only_grounded_facts():
    p = build_summary_prompt(CTX)
    assert "45/100" in p
    assert "late_fee" in p and "Late payments trigger a penalty." in p
    assert "processing_fee: 2" in p
    assert "ONLY" in p  # instructs the model to use only the given facts


def test_system_prompt_forbids_invention():
    low = GROUNDING_SYSTEM.lower()
    assert "do not add" in low and "invent" in low and "not present" in low


def test_summarizer_passes_exactly_the_grounded_prompt():
    seen = {}

    class FakeClient:
        model = "fake"

        def generate(self, prompt, system=""):
            seen["prompt"] = prompt
            seen["system"] = system
            return "A grounded summary."

    out = AISummarizer(FakeClient()).summarize(CTX)
    assert out == "A grounded summary."
    # Only the grounded prompt reaches the model
    assert seen["system"] == GROUNDING_SYSTEM
    assert seen["prompt"] == build_summary_prompt(CTX)
