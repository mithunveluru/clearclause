from app.analysis import AnalyzerContext, ClauseRef, get_analyzer
from app.core.constants import JobStatus
from app.detection import detect
from app.metrics import count_analyzer
from app.repositories.analyzer_run_repo import AnalyzerRunRepository
from app.repositories.clause_repo import ClauseRepository
from app.repositories.document_repo import DocumentRepository
from app.repositories.entity_repo import EntityRepository
from app.repositories.finding_repo import FindingRepository


class AnalyzerService:
    """Analyze stage: pick the analyzer for the classified type, run it, and
    persist entities + findings + an analyzer_run. Unregistered types fall back
    to the V1 rule engine (findings only) so behavior is never lost."""

    def __init__(
        self,
        documents: DocumentRepository,
        clauses: ClauseRepository,
        findings: FindingRepository,
        entities: EntityRepository,
        runs: AnalyzerRunRepository,
    ):
        self.documents = documents
        self.clauses = clauses
        self.findings = findings
        self.entities = entities
        self.runs = runs

    async def process(self, document_id: int) -> dict:
        doc = await self.documents.get_by_id(document_id)
        rows = await self.clauses.list_for_document(document_id)
        ctx = AnalyzerContext(
            document_id=document_id,
            classified_type=doc.classified_type if doc else None,
            document_family=doc.document_family if doc else None,
            clauses=[ClauseRef(c.id, c.normalized_text, c.page_number, c.section_name) for c in rows],
        )
        analyzer = get_analyzer(ctx.classified_type)
        run = await self.runs.create(
            document_id, analyzer.analyzer_type if analyzer else "detection"
        )
        try:
            if analyzer:
                result = analyzer.analyze(ctx)
                await self.entities.replace_for_document(document_id, result.entities)
                await self.findings.replace_for_document(
                    document_id,
                    [
                        {**f.model_dump(), "document_family": result.document_family,
                         "analyzer_type": result.analyzer_type}
                        for f in result.findings
                    ],
                )
                summary = {
                    "analyzer": result.analyzer_type,
                    "family": result.document_family,
                    "entities": len(result.entities),
                    "findings": len(result.findings),
                    "headline_metric": result.headline_metric.model_dump()
                    if result.headline_metric else None,
                    "summary": result.summary,
                    "strengths": result.strengths,
                    "recommendations": result.recommendations,
                }
            else:
                raw = detect([(c.id, c.text) for c in ctx.clauses])
                await self.findings.replace_for_document(document_id, raw)
                summary = {
                    "analyzer": "detection", "family": ctx.document_family,
                    "entities": 0, "findings": len(raw), "headline_metric": None,
                    "summary": None, "strengths": [], "recommendations": [],
                }
            await self.runs.finish(run.id, JobStatus.DONE, summary)
            count_analyzer(summary["analyzer"], JobStatus.DONE)
            return summary
        except Exception as e:
            await self.runs.finish(run.id, JobStatus.FAILED, None, str(e))
            count_analyzer(analyzer.analyzer_type if analyzer else "detection", JobStatus.FAILED)
            raise
