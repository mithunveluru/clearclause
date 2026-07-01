import asyncio
import time

from app.metrics import record_ai
from app.rag import QdrantStore
from app.rag.embeddings import Embedder
from app.repositories.chunk_repo import ChunkRepository
from app.repositories.classification_repo import ClassificationRepository
from app.repositories.document_repo import DocumentRepository
from app.repositories.finding_repo import FindingRepository


class EmbedService:
    """Embeds chunks into Qdrant with severity/risk_tags metadata for filtered retrieval."""

    def __init__(
        self,
        chunks: ChunkRepository,
        documents: DocumentRepository,
        classifications: ClassificationRepository | None = None,
        findings: FindingRepository | None = None,
        embedder=None,
        store: QdrantStore | None = None,
    ):
        self.chunks = chunks
        self.documents = documents
        self.classifications = classifications
        self.findings = findings
        self.embedder = embedder or Embedder()
        self.store = store or QdrantStore()

    async def process(self, document_id: int) -> int:
        rows = await self.chunks.list_for_document(document_id)
        if not rows:
            return 0

        # Fetch enrichment metadata (best-effort; empty dicts if unavailable)
        doc_type: str | None = None
        severity_by_clause: dict[int, str] = {}
        tags_by_clause: dict[int, list[str]] = {}

        if self.classifications:
            cls = await self.classifications.get(document_id)
            if cls:
                doc_type = cls.classified_type

        if self.findings:
            finding_rows = await self.findings.list_for_document(document_id)
            _sev_rank = {"critical": 4, "high": 3, "medium": 2, "low": 1}
            for f in finding_rows:
                if f.clause_id is None:
                    continue
                cid = f.clause_id
                current = severity_by_clause.get(cid, "low")
                if _sev_rank.get(f.severity, 0) > _sev_rank.get(current, 0):
                    severity_by_clause[cid] = f.severity
                tags_by_clause.setdefault(cid, [])
                if f.issue_type not in tags_by_clause[cid]:
                    tags_by_clause[cid].append(f.issue_type)

        texts = [r.chunk_text for r in rows]
        _t = time.perf_counter()
        vectors = await asyncio.to_thread(self.embedder.embed, texts)
        record_ai("embed", time.perf_counter() - _t)

        points = []
        for r, v in zip(rows, vectors):
            # Chunks can span multiple clauses; use chunk's own clause_id if available
            clause_id = getattr(r, "clause_id", None)
            severity = severity_by_clause.get(clause_id) if clause_id else None
            risk_tags = tags_by_clause.get(clause_id, []) if clause_id else []
            points.append({
                "id": r.id,
                "vector": v,
                "payload": {
                    "document_id": document_id,
                    "doc_type": doc_type,
                    "page": r.page_number,
                    "section": r.section_name,
                    "chunk_index": r.chunk_index,
                    "text": r.chunk_text,
                    "severity": severity,
                    "risk_tags": risk_tags,
                },
            })

        await asyncio.to_thread(self.store.ensure_collection, len(vectors[0]))
        await asyncio.to_thread(self.store.delete_document, document_id)
        await asyncio.to_thread(self.store.upsert, points)

        for r in rows:
            await self.chunks.set_vector(r.id, str(r.id), self.embedder.provider)
        await self.documents.set_qa_ready(document_id, True)
        return len(rows)
