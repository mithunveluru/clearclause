from app.detection import detect
from app.repositories.clause_repo import ClauseRepository
from app.repositories.finding_repo import FindingRepository


class DetectionService:
    def __init__(self, clauses: ClauseRepository, findings: FindingRepository):
        self.clauses = clauses
        self.findings = findings

    async def process(self, document_id: int) -> int:
        rows = await self.clauses.list_for_document(document_id)
        results = detect([(c.id, c.normalized_text) for c in rows])
        return await self.findings.replace_for_document(document_id, results)
