from app.core import files
from app.reporting import build_summary, render_html
from app.repositories.clause_repo import ClauseRepository
from app.repositories.document_repo import DocumentRepository
from app.repositories.finding_repo import FindingRepository
from app.repositories.report_repo import ReportRepository
from app.repositories.score_repo import ScoreRepository
from app.scoring.risk import band, summarize


class ReportService:
    def __init__(
        self,
        documents: DocumentRepository,
        clauses: ClauseRepository,
        findings: FindingRepository,
        scores: ScoreRepository,
        reports: ReportRepository,
    ):
        self.documents = documents
        self.clauses = clauses
        self.findings = findings
        self.scores = scores
        self.reports = reports

    async def process(self, document_id: int, user_id: int) -> dict:
        doc = await self.documents.get_for_user(document_id, user_id)
        if doc is None:
            raise ValueError("Document not found")
        risk = await self.scores.get_risk(document_id)
        if risk is None:
            raise ValueError("Document not scored yet")

        clauses = await self.clauses.list_for_document(document_id)
        text_by_id = {c.id: c.normalized_text for c in clauses}
        findings = [
            {
                "issue_type": f.issue_type,
                "severity": f.severity,
                "confidence": f.confidence,
                "explanation": f.explanation,
                "action_text": f.action_text,
                "clause_text": text_by_id.get(f.clause_id),
            }
            for f in await self.findings.list_for_document(document_id)
        ]
        cost = await self.scores.get_cost(document_id)

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
            cost={
                "headline_rate": cost.headline_rate if cost else None,
                "processing_fee": cost.processing_fee if cost else None,
                "late_fee": cost.late_fee if cost else None,
                "renewal_fee": cost.renewal_fee if cost else None,
                "foreclosure_charge": cost.foreclosure_charge if cost else None,
                "estimated_true_cost": cost.estimated_true_cost if cost else None,
            },
        )

        html_path = files.save_report(render_html(summary))
        await self.reports.save(document_id, summary, html_path)
        return summary
