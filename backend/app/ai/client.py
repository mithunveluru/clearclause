"""LLM via Groq API (OpenAI-compatible chat completions)."""
import httpx

from app.core.config import settings

_GROQ_CHAT_URL = "https://api.groq.com/openai/v1/chat/completions"


class LLMClient:
    def __init__(self, model: str | None = None):
        self.model = model or settings.AI_MODEL

    def generate(self, prompt: str, system: str = "") -> str:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        with httpx.Client(timeout=180) as client:
            r = client.post(
                _GROQ_CHAT_URL,
                headers={"Authorization": f"Bearer {settings.GROQ_API_KEY}"},
                json={"model": self.model, "messages": messages},
            )
            r.raise_for_status()
            return r.json()["choices"][0]["message"]["content"].strip()
