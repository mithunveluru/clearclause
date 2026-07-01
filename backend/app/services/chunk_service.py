from app.rag import chunk_clauses
from app.repositories.chunk_repo import ChunkRepository
from app.repositories.clause_repo import ClauseRepository


class ChunkService:
    def __init__(self, clauses: ClauseRepository, chunks: ChunkRepository):
        self.clauses = clauses
        self.chunks = chunks

    async def process(self, document_id: int) -> int:
        rows = await self.clauses.list_for_document(document_id)
        triples = [(c.page_number, c.section_name, c.normalized_text) for c in rows]
        return await self.chunks.replace_for_document(document_id, chunk_clauses(triples))
