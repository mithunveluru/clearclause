"""Land sale agreement analyzer — flags missing protections a buyer needs and
reports a Sale Agreement Risk score."""
from app.analysis.base import AnalyzerContext, BaseAnalyzer
from app.analysis.helpers import headline, mk_finding
from app.contracts import AnalyzerResult
from app.core.constants import ClassifiedType, DocumentFamily
from app.entities.extractors._util import present
from app.entities.extractors.sale_deed import SaleDeedEntityExtractor


class SaleDeedAnalyzer(BaseAnalyzer):
    analyzer_type = ClassifiedType.SALE_DEED
    document_family = DocumentFamily.PROPERTY

    def analyze(self, ctx: AnalyzerContext) -> AnalyzerResult:
        low = ctx.full_text.lower()
        findings = [f for f in [
            mk_finding(present(low, "refund"), "missing_refund_terms", "high",
                "No refund terms are stated for the advance.",
                "If the deal falls through you may not recover your advance.",
                "Add a clear refund clause for the advance amount."),
            mk_finding(present(low, "possession"), "ambiguous_possession_date", "medium",
                "The possession date is not specified.",
                "You can't hold the seller to a handover timeline.",
                "Fix a definite possession date in the agreement."),
            mk_finding(present(low, "warrant"), "unclear_ownership_warranty", "high",
                "No clear ownership warranty from the seller.",
                "Title defects could surface after purchase.",
                "Require the seller to warrant clear, marketable title."),
            mk_finding(present(low, "encumbrance"), "missing_encumbrance_declaration", "high",
                "No encumbrance declaration is present.",
                "Hidden loans or charges on the property may remain.",
                "Get a written encumbrance-free declaration and an EC."),
            mk_finding(present(low, "registration"), "missing_registration_timeline", "medium",
                "No registration timeline is stated.",
                "Registration could be delayed indefinitely.",
                "Set a deadline for completing registration."),
            mk_finding(not present(low, "buyer shall bear", "buyer is liable"),
                "heavy_buyer_liability", "medium",
                "Liabilities appear to fall heavily on the buyer.",
                "You may absorb costs that should be shared or on the seller.",
                "Re-balance liability and cost-sharing clauses."),
        ] if f is not None]
        strengths = [
            f"{label} present."
            for kw, label in [("refund", "Refund terms"), ("encumbrance", "Encumbrance declaration"),
                              ("warrant", "Ownership warranty"), ("possession", "Possession date")]
            if kw in low
        ]
        metric = headline("Sale Agreement Risk", findings)
        summary = (
            f"This sale agreement scores {metric.value}/100 — {metric.band.lower()} risk. "
            + (f"{len(findings)} protection(s) are missing or weak."
               if findings else "Key buyer protections appear to be present.")
        )
        return AnalyzerResult(
            analyzer_type=self.analyzer_type, document_family=self.document_family,
            entities=SaleDeedEntityExtractor().extract(ctx.full_text), findings=findings,
            headline_metric=metric, strengths=strengths,
            recommendations=[f.action_text for f in findings][:6], summary=summary,
        )
