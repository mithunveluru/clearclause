"""Qdrant collection for static knowledge packs (regulations, guidelines).

Separate from document chunks. Filterable by family so retrieval stays
scoped to the document's domain (consumer_finance, rental, property, etc.)
"""
import hashlib

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchValue,
    PointStruct,
    VectorParams,
)

from app.core.config import settings

KNOWLEDGE_COLLECTION = "clearclause_knowledge"


class KnowledgeStore:
    def __init__(self, url: str | None = None):
        self.client = QdrantClient(url=url or settings.QDRANT_URL)

    def ensure_collection(self, dim: int) -> None:
        names = [c.name for c in self.client.get_collections().collections]
        if KNOWLEDGE_COLLECTION not in names:
            self.client.create_collection(
                KNOWLEDGE_COLLECTION,
                vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
            )

    def count(self, family: str | None = None) -> int:
        filt = (
            Filter(must=[FieldCondition(key="family", match=MatchValue(value=family))])
            if family
            else None
        )
        return self.client.count(KNOWLEDGE_COLLECTION, count_filter=filt).count

    def upsert(self, entries: list[dict], vectors: list[list[float]]) -> None:
        points = [
            PointStruct(
                id=int(hashlib.sha256(e["id"].encode()).hexdigest(), 16) % (2**63),
                vector=v,
                payload={
                    "pack_id": e["id"],
                    "family": e["family"],
                    "category": e["category"],
                    "title": e["title"],
                    "text": e["text"],
                    "tags": e.get("tags", []),
                },
            )
            for e, v in zip(entries, vectors)
        ]
        self.client.upsert(KNOWLEDGE_COLLECTION, points=points)

    def search(
        self,
        vector: list[float],
        family: str | None = None,
        top_k: int = 3,
    ) -> list[dict]:
        filt = (
            Filter(must=[FieldCondition(key="family", match=MatchValue(value=family))])
            if family
            else None
        )
        hits = self.client.search(
            KNOWLEDGE_COLLECTION,
            query_vector=vector,
            query_filter=filt,
            limit=top_k,
        )
        return [
            {
                "title": h.payload["title"],
                "text": h.payload["text"],
                "category": h.payload["category"],
                "score": h.score,
            }
            for h in hits
        ]
