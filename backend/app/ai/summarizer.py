from app.ai.client import LLMClient
from app.ai.prompts import GROUNDING_SYSTEM, build_summary_prompt


class AISummarizer:
    """Rephrases the deterministic findings/score/entities into a plain-English
    summary. Adds no facts — grounding is enforced by the system prompt."""

    def __init__(self, client=None):
        self.client = client or LLMClient()

    def summarize(self, context: dict) -> str:
        return self.client.generate(build_summary_prompt(context), GROUNDING_SYSTEM)
