from app.repositories.analyzer_run_repo import AnalyzerRunRepository
from app.repositories.clause_repo import ClauseRepository
from app.repositories.finding_repo import FindingRepository
from app.repositories.score_repo import ScoreRepository
from app.scoring import empty_cost, estimate_cost, score_findings


class ScoringService:
    def __init__(
        self,
        clauses: ClauseRepository,
        findings: FindingRepository,
        scores: ScoreRepository,
        analyzer_runs: AnalyzerRunRepository | None = None,
    ):
        self.clauses = clauses
        self.findings = findings
        self.scores = scores
        self.analyzer_runs = analyzer_runs

    async def process(self, document_id: int) -> dict:
        # Property/specialized analyzers compute their own headline metric; use it.
        if self.analyzer_runs is not None:
            run = await self.analyzer_runs.latest(document_id)
            metric = (run.result_json or {}).get("headline_metric") if run else None
            if metric:
                cats = {
                    "total": metric["value"], "fee_opacity": 0, "penalty": 0,
                    "renewal": 0, "consent": 0, "cancellation": 0,
                }
                await self.scores.save_risk(document_id, cats)
                await self.scores.save_cost(document_id, empty_cost())
                return cats

        # Consumer (fee-weighted) path.
        clauses = await self.clauses.list_for_document(document_id)
        text_by_id = {c.id: c.normalized_text for c in clauses}
        texts = [c.normalized_text for c in clauses]
        finding_rows = await self.findings.list_for_document(document_id)
        fdicts = [
            {"issue_type": f.issue_type, "severity": f.severity,
             "clause_text": text_by_id.get(f.clause_id)}
            for f in finding_rows
        ]
        cats = score_findings(fdicts, texts)
        cost = estimate_cost(fdicts, texts)
        await self.scores.save_risk(document_id, cats)
        await self.scores.save_cost(document_id, cost)
        return cats
