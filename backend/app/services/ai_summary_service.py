import asyncio
import hashlib
import json
import time

from app.ai.summarizer import AISummarizer
from app.metrics import record_ai
from app.repositories.ai_output_repo import AIOutputRepository
from app.repositories.document_repo import DocumentRepository
from app.repositories.entity_repo import EntityRepository
from app.repositories.finding_repo import FindingRepository
from app.repositories.score_repo import ScoreRepository
from app.scoring.risk import band


class AISummaryService:
    """Generates a grounded AI summary from deterministic outputs only, cached in
    ai_outputs by a hash of its inputs (so re-runs don't re-call the model)."""

    def __init__(
        self,
        documents: DocumentRepository,
        findings: FindingRepository,
        scores: ScoreRepository,
        entities: EntityRepository,
        ai_outputs: AIOutputRepository,
        summarizer: AISummarizer | None = None,
    ):
        self.documents = documents
        self.findings = findings
        self.scores = scores
        self.entities = entities
        self.ai_outputs = ai_outputs
        self.summarizer = summarizer or AISummarizer()

    async def _context(self, document_id: int) -> dict:
        doc = await self.documents.get_by_id(document_id)
        risk = await self.scores.get_risk(document_id)
        cost = await self.scores.get_cost(document_id)
        finding_rows = await self.findings.list_for_document(document_id)
        entity_rows = await self.entities.list_for_document(document_id)
        return {
            "type": doc.classified_type if doc else None,
            "score": risk.total_score if risk else None,
            "band": band(risk.total_score) if risk else None,
            "findings": [
                {"issue": f.issue_type, "severity": f.severity, "explanation": f.explanation}
                for f in finding_rows[:8]
            ],
            "entities": [
                {"type": e.entity_type, "value": e.entity_value} for e in entity_rows[:10]
            ],
            "cost": {
                "headline_rate": cost.headline_rate if cost else None,
                "processing_fee": cost.processing_fee if cost else None,
                "late_fee": cost.late_fee if cost else None,
                "renewal_fee": cost.renewal_fee if cost else None,
                "foreclosure_charge": cost.foreclosure_charge if cost else None,
                "estimated_true_cost": cost.estimated_true_cost if cost else None,
            } if cost else None,
        }

    async def process(self, document_id: int) -> str:
        ctx = await self._context(document_id)
        input_hash = hashlib.sha256(json.dumps(ctx, sort_keys=True).encode()).hexdigest()

        cached = await self.ai_outputs.get_by_hash(document_id, "summary", input_hash)
        if cached:
            await self.documents.set_ai_summary_ready(document_id, True)
            return cached.content

        _t = time.perf_counter()
        text = await asyncio.to_thread(self.summarizer.summarize, ctx)
        record_ai("summary", time.perf_counter() - _t)
        await self.ai_outputs.save(
            document_id, "summary", text, self.summarizer.client.model, input_hash
        )
        await self.documents.set_ai_summary_ready(document_id, True)
        return text
