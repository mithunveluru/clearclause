"""Index static knowledge packs into Qdrant on startup. Idempotent: skips if already indexed."""
import asyncio
import logging

from app.knowledge.packs import KNOWLEDGE_PACKS
from app.rag.embeddings import Embedder
from app.rag.knowledge_store import KnowledgeStore

log = logging.getLogger("clearclause.knowledge")


class KnowledgeIndexService:
    def __init__(self, embedder: Embedder | None = None, store: KnowledgeStore | None = None):
        self.embedder = embedder or Embedder()
        self.store = store or KnowledgeStore()

    def index(self, force: bool = False) -> int:
        """Embed and upsert all knowledge packs. Returns number of entries indexed.
        Skips if already indexed unless force=True."""
        try:
            first_entry = KNOWLEDGE_PACKS[0]
            sample_vector = self.embedder.embed([first_entry["text"]])[0]
            dim = len(sample_vector)
            self.store.ensure_collection(dim)

            if not force and self.store.count() >= len(KNOWLEDGE_PACKS):
                log.info("Knowledge packs already indexed (%d entries); skipping.", len(KNOWLEDGE_PACKS))
                return 0

            texts = [p["text"] for p in KNOWLEDGE_PACKS]
            # One batch; rebuild avoids partial state
            all_texts = [first_entry["text"]] + texts[1:]
            vectors = [sample_vector] + self.embedder.embed(all_texts[1:])
            self.store.upsert(KNOWLEDGE_PACKS, vectors)
            log.info("Indexed %d knowledge pack entries.", len(KNOWLEDGE_PACKS))
            return len(KNOWLEDGE_PACKS)
        except Exception as e:
            log.warning("Knowledge indexing failed (non-fatal): %s", e)
            return 0

    async def index_async(self, force: bool = False) -> int:
        return await asyncio.to_thread(self.index, force)
