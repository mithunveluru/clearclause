import asyncio
import re
import time

from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.client import LLMClient
from app.ai.prompts import build_follow_up_prompt, build_qa_prompt, get_qa_system
from app.contracts import Citation, KnowledgeRef, QAAnswer
from app.knowledge.packs import FAMILY_MAP
from app.metrics import record_ai
from app.rag import HybridRetriever, StructuredRetriever, detect_intent


class QAService:
    """Hybrid Q&A: three retrieval layers fused per intent, answers grounded in evidence.

    Layer 1 (always): BM25 + vector hybrid search over document chunks
    Layer 2 (structured intent): SQL entity lookup for factual questions
    Layer 3 (knowledge intent): semantic search over knowledge packs (regulations)
    """

    def __init__(
        self,
        db: AsyncSession | None = None,
        retriever: HybridRetriever | None = None,
        client: LLMClient | None = None,
    ):
        self.db = db
        self.retriever = retriever or HybridRetriever()
        self.client = client or LLMClient()

    async def answer(
        self,
        document_id: int,
        question: str,
        doc_type: str | None = None,
    ) -> QAAnswer:
        intent = detect_intent(question)
        family = FAMILY_MAP.get(doc_type or "", None) if doc_type else None
        extra_context: list[str] = []
        regulation_refs: list[KnowledgeRef] = []

        _t = time.perf_counter()
        chunks = await asyncio.to_thread(self.retriever.search, document_id, question)
        record_ai("retrieval_hybrid", time.perf_counter() - _t)

        if intent == "structured" and self.db:
            structured = await StructuredRetriever(self.db).retrieve(document_id, question)
            if structured:
                extra_context.append(f"=== {structured}")

        if intent in ("knowledge", "structured"):
            _t = time.perf_counter()
            knowledge = await asyncio.to_thread(
                self.retriever.search_knowledge, question, family, 3
            )
            record_ai("retrieval_knowledge", time.perf_counter() - _t)
            if knowledge:
                reg_lines = [f"- {k['title']}: {k['text']}" for k in knowledge]
                extra_context.append("=== Applicable Regulations ===\n" + "\n".join(reg_lines))
                regulation_refs = [
                    KnowledgeRef(title=k["title"], category=k["category"]) for k in knowledge
                ]

        if not chunks and not extra_context:
            return QAAnswer(
                answer="I couldn't find anything in this document to answer that question.",
                citations=[],
                regulation_refs=[],
                follow_up_questions=[],
                confidence_note="No relevant excerpts retrieved from this document.",
            )

        excerpts = [
            {"page": c.page_number, "section": c.section_name, "text": c.text}
            for c in chunks
        ]

        _t = time.perf_counter()
        answer_text = await asyncio.to_thread(
            self.client.generate,
            build_qa_prompt(question, excerpts, extra_context or None),
            get_qa_system(doc_type),
        )
        record_ai("qa_llm", time.perf_counter() - _t)

        follow_ups = await self._follow_ups(question, answer_text, doc_type)

        citations = [
            Citation(page=c.page_number, section=c.section_name, snippet=c.text[:160])
            for c in chunks[:3]
        ]

        confidence = "Grounded in retrieved document clauses" + (
            " and applicable regulations" if regulation_refs else ""
        ) + " only."

        return QAAnswer(
            answer=answer_text,
            citations=citations,
            regulation_refs=regulation_refs,
            follow_up_questions=follow_ups,
            confidence_note=confidence,
        )

    async def _follow_ups(self, question: str, answer: str, doc_type: str | None) -> list[str]:
        try:
            raw = await asyncio.to_thread(
                self.client.generate,
                build_follow_up_prompt(question, answer, doc_type),
                "Generate follow-up questions only. No preamble.",
            )
            # Parse numbered list: "1. ...\n2. ...\n3. ..."
            lines = [
                re.sub(r"^\d+[\.\)]\s*", "", line).strip()
                for line in raw.splitlines()
                if line.strip()
            ]
            return [line for line in lines if len(line) > 10][:3]
        except Exception:  # noqa: BLE001 — follow-ups are optional
            return []
