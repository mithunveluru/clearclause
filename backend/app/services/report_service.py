from app.core import storage
from app.reporting import build_pdf, build_summary
from app.repositories.clause_repo import ClauseRepository
from app.repositories.document_repo import DocumentRepository
from app.repositories.entity_repo import EntityRepository
from app.repositories.finding_repo import FindingRepository
from app.repositories.report_repo import ReportRepository
from app.repositories.score_repo import ScoreRepository
from app.scoring.cost import cost_dict
from app.scoring.risk import band, summarize
from app.services.explorer_service import timeline_entries


class ReportService:
    def __init__(
        self,
        documents: DocumentRepository,
        clauses: ClauseRepository,
        findings: FindingRepository,
        scores: ScoreRepository,
        reports: ReportRepository,
        store: storage.Storage | None = None,
        entities: EntityRepository | None = None,
    ):
        self.store = store or storage.get_storage()
        self.documents = documents
        self.clauses = clauses
        self.findings = findings
        self.scores = scores
        self.reports = reports
        # Optional; without it the report omits key dates
        self.entities = entities

    async def process(self, document_id: int, user_id: int) -> dict:
        doc = await self.documents.get_for_user(document_id, user_id)
        if doc is None:
            raise ValueError("Document not found")
        risk = await self.scores.get_risk(document_id)
        if risk is None:
            raise ValueError("Document not scored yet")

        clauses = await self.clauses.list_for_document(document_id)
        text_by_id = {c.id: c.normalized_text for c in clauses}
        # Source location for each quoted clause
        page_by_id = {c.id: c.page_number for c in clauses}
        section_by_id = {c.id: c.section_name for c in clauses}
        findings = [
            {
                "issue_type": f.issue_type,
                "severity": f.severity,
                "confidence": f.confidence,
                "explanation": f.explanation,
                "impact": f.impact,
                "action_text": f.action_text,
                "clause_text": text_by_id.get(f.clause_id),
                "page_number": page_by_id.get(f.clause_id),
                "section_name": section_by_id.get(f.clause_id),
            }
            for f in await self.findings.list_for_document(document_id)
        ]
        cost = await self.scores.get_cost(document_id)
        key_dates = timeline_entries(
            await self.entities.list_for_document(document_id)
        ) if self.entities else []

        cats = {
            "total": risk.total_score,
            "fee_opacity": risk.fee_opacity_score,
            "penalty": risk.penalty_score,
            "renewal": risk.renewal_score,
            "consent": risk.consent_score,
            "cancellation": risk.cancellation_score,
        }
        summary = build_summary(
            doc={
                "id": doc.id,
                "filename": doc.original_filename,
                "source_type": doc.source_type,
                "doc_type": doc.doc_type,
            },
            findings=findings,
            risk={
                "total": risk.total_score,
                "band": band(risk.total_score),
                "summary": summarize(cats),
                "breakdown": {k: v for k, v in cats.items() if k != "total"},
            },
            key_dates=key_dates,
            cost=cost_dict(cost),
        )

        # reportlab writes to a path, not bytes
        key = storage.new_key("reports", ".pdf")
        with storage.temp_file(b"", ".pdf") as tmp:
            build_pdf(summary, tmp)
            with open(tmp, "rb") as f:
                self.store.put(key, f.read())

        await self.reports.save(document_id, summary, key)
        return summary
