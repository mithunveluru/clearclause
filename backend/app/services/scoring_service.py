from app.repositories.clause_repo import ClauseRepository
from app.repositories.finding_repo import FindingRepository
from app.repositories.score_repo import ScoreRepository
from app.scoring import estimate_cost, score_findings


class ScoringService:
    def __init__(
        self,
        clauses: ClauseRepository,
        findings: FindingRepository,
        scores: ScoreRepository,
    ):
        self.clauses = clauses
        self.findings = findings
        self.scores = scores

    async def process(self, document_id: int) -> dict:
        clauses = await self.clauses.list_for_document(document_id)
        text_by_id = {c.id: c.normalized_text for c in clauses}
        texts = [c.normalized_text for c in clauses]

        finding_rows = await self.findings.list_for_document(document_id)
        fdicts = [
            {
                "issue_type": f.issue_type,
                "severity": f.severity,
                "clause_text": text_by_id.get(f.clause_id),
            }
            for f in finding_rows
        ]

        cats = score_findings(fdicts, texts)
        cost = estimate_cost(fdicts, texts)
        await self.scores.save_risk(document_id, cats)
        await self.scores.save_cost(document_id, cost)
        return cats
