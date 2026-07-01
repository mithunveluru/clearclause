"""Patta (land record) analyzer — checks the key fields a valid patta should
carry and reports a Patta Health risk score (higher = less complete/healthy)."""
from app.analysis.base import AnalyzerContext, BaseAnalyzer
from app.analysis.helpers import headline, mk_finding
from app.contracts import AnalyzerResult
from app.core.constants import ClassifiedType, DocumentFamily
from app.entities.extractors._util import present
from app.entities.extractors.patta import PattaEntityExtractor


class PattaAnalyzer(BaseAnalyzer):
    analyzer_type = ClassifiedType.PATTA
    document_family = DocumentFamily.PROPERTY

    def analyze(self, ctx: AnalyzerContext) -> AnalyzerResult:
        low = ctx.full_text.lower()
        findings = [f for f in [
            mk_finding(present(low, "survey"), "missing_survey_number", "high",
                "No survey number is recorded.",
                "Without a survey number the parcel cannot be reliably identified.",
                "Obtain the survey number and verify it against revenue records."),
            mk_finding(present(low, "owner"), "missing_owner_name", "high",
                "No owner name is recorded.",
                "Ownership cannot be confirmed without a named owner.",
                "Confirm the registered owner name on the patta."),
            mk_finding(present(low, "classification"), "missing_classification", "medium",
                "Land classification is not stated.",
                "Permitted use (e.g. dry/wet/agricultural) is unclear.",
                "Get the land classification from the revenue authority."),
            mk_finding(present(low, "bound", "boundar"), "incomplete_boundary", "medium",
                "Boundary description is missing or incomplete.",
                "Disputes over extent and neighbours become likely.",
                "Ensure the four boundaries are clearly described."),
            mk_finding(present(low, "extent", "hectare", "acre"), "missing_extent", "medium",
                "The land extent/area is not stated.",
                "You can't confirm the size you're paying for.",
                "Record the exact extent in hectares/acres."),
            mk_finding(present(low, "taluk") and present(low, "district"),
                "missing_taluk_district", "medium",
                "Taluk and/or district is not stated.",
                "Jurisdiction for verification is unclear.",
                "Add the taluk and district for record verification."),
        ] if f is not None]
        strengths = [
            f"{label} is recorded."
            for kw, label in [("survey", "Survey number"), ("owner", "Owner name"),
                              ("extent", "Extent"), ("classification", "Classification")]
            if kw in low
        ]
        metric = headline("Patta Health", findings)
        summary = (
            f"This patta scores {metric.value}/100 — {metric.band.lower()} risk. "
            + (f"{len(findings)} field(s) need attention before relying on it."
               if findings else "All key fields appear to be present.")
        )
        return AnalyzerResult(
            analyzer_type=self.analyzer_type, document_family=self.document_family,
            entities=PattaEntityExtractor().extract(ctx.full_text), findings=findings,
            headline_metric=metric, strengths=strengths,
            recommendations=[f.action_text for f in findings][:6], summary=summary,
        )
