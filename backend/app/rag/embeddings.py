"""Embeddings via Jina AI API (jina-embeddings-v3). HTTP only — no heavy ML deps."""
import httpx

from app.core.config import settings

_JINA_EMBED_URL = "https://api.jina.ai/v1/embeddings"
_EMBED_MODEL = "jina-embeddings-v3"
_EMBED_DIM = 768


class Embedder:
    provider = "jina"

    def embed(self, texts: list[str]) -> list[list[float]]:
        with httpx.Client(timeout=120) as client:
            r = client.post(
                _JINA_EMBED_URL,
                headers={"Authorization": f"Bearer {settings.JINA_API_KEY}"},
                json={"model": _EMBED_MODEL, "input": texts, "dimensions": _EMBED_DIM},
            )
            r.raise_for_status()
            return [item["embedding"] for item in r.json()["data"]]
