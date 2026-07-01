"""Consumer analyzer (loan / subscription / credit_card): reuses the existing
explainable rule engine unchanged, so V1 findings are preserved exactly, and
adds type-specific entity extraction. Scoring stays in the fee-weighted scorer."""
from app.analysis.base import AnalyzerContext, BaseAnalyzer
from app.contracts import AnalyzerResult, Entity, FindingDraft
from app.core.constants import DocumentFamily
from app.detection import detect

_FINDING_KEYS = (
    "issue_type", "severity", "confidence", "explanation",
    "impact", "action_text", "clause_id", "clause_text",
)


class ConsumerAnalyzer(BaseAnalyzer):
    document_family = DocumentFamily.CONSUMER

    def __init__(self, analyzer_type: str, extractor):
        self.analyzer_type = analyzer_type
        self.extractor = extractor

    def analyze(self, ctx: AnalyzerContext) -> AnalyzerResult:
        raw = detect([(c.id, c.text) for c in ctx.clauses])  # identical to V1
        findings = [FindingDraft(**{k: f.get(k) for k in _FINDING_KEYS}) for f in raw]
        entities: list[Entity] = self.extractor.extract(ctx.full_text)
        return AnalyzerResult(
            analyzer_type=self.analyzer_type,
            document_family=self.document_family,
            entities=entities,
            findings=findings,
        )
