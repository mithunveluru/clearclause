"""Hybrid retriever: vector search + BM25 reranking via Reciprocal Rank Fusion.

Three retrieval layers composed here; QAService calls them selectively by intent.
"""
import math
from collections import Counter

from app.contracts import Chunk
from app.rag.embeddings import Embedder
from app.rag.knowledge_store import KnowledgeStore
from app.rag.store import QdrantStore


def _bm25_scores(query: str, corpus: list[str], k1: float = 1.5, b: float = 0.75) -> list[float]:
    terms = query.lower().split()
    tokenized = [doc.lower().split() for doc in corpus]
    n = len(tokenized)
    avgdl = sum(len(d) for d in tokenized) / n if n else 1
    scores: list[float] = []
    for doc in tokenized:
        freq = Counter(doc)
        dl = len(doc)
        score = 0.0
        for term in terms:
            tf = freq.get(term, 0)
            df = sum(1 for d in tokenized if term in d)
            idf = math.log((n - df + 0.5) / (df + 0.5) + 1)
            score += idf * (tf * (k1 + 1)) / (tf + k1 * (1 - b + b * dl / avgdl))
        scores.append(score)
    return scores


def _rrf(rankings: list[list[int]], k: int = 60) -> list[int]:
    scores: dict[int, float] = {}
    for ranking in rankings:
        for rank, idx in enumerate(ranking):
            scores[idx] = scores.get(idx, 0.0) + 1.0 / (k + rank + 1)
    return sorted(scores, key=lambda i: scores[i], reverse=True)


class HybridRetriever:
    """Layer 1 retriever: semantic (vector) + BM25 reranking, fused via RRF."""

    def __init__(
        self,
        embedder: Embedder | None = None,
        store: QdrantStore | None = None,
        knowledge_store: KnowledgeStore | None = None,
    ):
        self.embedder = embedder or Embedder()
        self.store = store or QdrantStore()
        self.knowledge_store = knowledge_store or KnowledgeStore()

    def search(
        self,
        document_id: int,
        query: str,
        top_k: int = 5,
        candidate_k: int = 20,
    ) -> list[Chunk]:
        """Retrieve document chunks: vector top-candidate_k, BM25-reranked, RRF-fused → top_k."""
        vector = self.embedder.embed([query])[0]
        hits = self.store.search(vector, document_id, top_k=candidate_k)
        if not hits:
            return []

        texts = [h.payload.get("text", "") for h in hits]
        bm25 = _bm25_scores(query, texts)
        bm25_rank = sorted(range(len(bm25)), key=lambda i: bm25[i], reverse=True)
        vector_rank = list(range(len(hits)))  # already sorted by cosine score

        fused = _rrf([vector_rank, bm25_rank])

        return [
            Chunk(
                chunk_index=hits[i].payload.get("chunk_index", 0),
                page_number=hits[i].payload.get("page"),
                section_name=hits[i].payload.get("section"),
                text=hits[i].payload.get("text", ""),
            )
            for i in fused[:top_k]
        ]

    def search_knowledge(
        self,
        query: str,
        family: str | None = None,
        top_k: int = 3,
    ) -> list[dict]:
        """Layer 3: retrieve applicable regulations from the knowledge collection."""
        vector = self.embedder.embed([query])[0]
        return self.knowledge_store.search(vector, family=family, top_k=top_k)
