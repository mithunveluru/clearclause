"""Qdrant vector store. One collection; every point is payload-tagged with
document_id/page/section so retrieval can filter by document (and more)."""
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

COLLECTION = "clearclause_chunks"


class QdrantStore:
    def __init__(self, url: str | None = None):
        self.client = QdrantClient(url=url or settings.QDRANT_URL)

    def ensure_collection(self, dim: int) -> None:
        names = [c.name for c in self.client.get_collections().collections]
        if COLLECTION not in names:
            self.client.create_collection(
                COLLECTION, vectors_config=VectorParams(size=dim, distance=Distance.COSINE)
            )

    def upsert(self, points: list[dict]) -> None:
        self.client.upsert(
            COLLECTION,
            points=[
                PointStruct(id=p["id"], vector=p["vector"], payload=p["payload"])
                for p in points
            ],
        )

    def search(self, vector: list[float], document_id: int, top_k: int = 5):
        return self.client.search(
            COLLECTION,
            query_vector=vector,
            query_filter=Filter(
                must=[FieldCondition(key="document_id", match=MatchValue(value=document_id))]
            ),
            limit=top_k,
        )

    def delete_document(self, document_id: int) -> None:
        self.client.delete(
            COLLECTION,
            points_selector=Filter(
                must=[FieldCondition(key="document_id", match=MatchValue(value=document_id))]
            ),
        )
