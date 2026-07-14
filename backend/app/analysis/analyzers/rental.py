"""Rental contract analyzer (property family). Deterministic fairness findings
from clause presence/thresholds, a Rental Fairness risk score (higher = less
fair), strengths, and a negotiation checklist."""
import re

from app.analysis.base import AnalyzerContext, BaseAnalyzer
from app.contracts import AnalyzerResult, FindingDraft, HeadlineMetric
from app.core.constants import ClassifiedType, DocumentFamily
from app.entities.extractors.rental import RentalEntityExtractor
from app.scoring.risk import SEVERITY_POINTS, band

# issue_type -> (severity, explanation, impact, action)
_ISSUES = {
    "excessive_deposit": ("high",
        "The security deposit is large relative to the monthly rent.",
        "It ties up a big sum and raises the cost of moving in.",
        "Ask to reduce the deposit to one or two months' rent."),
    "restrictive_lock_in": ("medium",
        "A lock-in period prevents you from leaving early without penalty.",
        "You may pay for months you don't use if you need to move.",
        "Negotiate a shorter lock-in or an early-exit clause."),
    "one_sided_termination": ("high",
        "The landlord can terminate, but the tenant has no equivalent right.",
        "You can be asked to vacate with little recourse.",
        "Insist on mutual termination rights with equal notice."),
    "uncapped_rent_increase": ("high",
        "Rent can be increased without a stated cap.",
        "Your rent could rise sharply after you move in.",
        "Negotiate a fixed annual cap (e.g. 5–7%) on increases."),
    "unclear_maintenance": ("medium",
        "Maintenance responsibility is not clearly assigned.",
        "Disputes over repairs and who pays can arise later.",
        "Get maintenance duties written down for both parties."),
    "missing_notice_period": ("medium",
        "No notice period for vacating is specified.",
        "Either side could end the tenancy abruptly.",
        "Add a clear notice period, e.g. one to two months."),
    "missing_exit_clause": ("high",
        "There is no clear termination or exit clause.",
        "Leaving the agreement cleanly may be difficult.",
        "Add a termination clause with conditions and notice."),
}

_NUM = re.compile(r"([\d,]{3,})")


def _money(low: str, anchors: list[str]) -> float | None:
    for a in anchors:
        i = low.find(a)
        if i >= 0:
            m = _NUM.search(low[i : i + 60])
            if m and float(m.group(1).replace(",", "")) >= 1000:
                return float(m.group(1).replace(",", ""))
    return None


class RentalAnalyzer(BaseAnalyzer):
    analyzer_type = ClassifiedType.RENTAL_CONTRACT
    document_family = DocumentFamily.PROPERTY

    def analyze(self, ctx: AnalyzerContext) -> AnalyzerResult:
        low = ctx.full_text.lower()
        keys: list[str] = []

        rent = _money(low, ["monthly rent", "rent is", "rent of"])
        deposit = _money(low, ["security deposit", "deposit is", "deposit of"])
        if rent and deposit and deposit >= 3 * rent:
            keys.append("excessive_deposit")
        if "lock-in" in low or "lock in" in low:
            keys.append("restrictive_lock_in")
        landlord_term = "landlord may terminate" in low or "landlord can terminate" in low
        tenant_term = "tenant may terminate" in low or "tenant can terminate" in low
        if landlord_term and not tenant_term:
            keys.append("one_sided_termination")
        if not ("terminat" in low or "vacate" in low or "exit" in low):
            keys.append("missing_exit_clause")
        # Only the increase sentence; ignore a stray '%'
        sentences = re.split(r"(?<=[.;])\s+|\n", low)
        inc_sentence = next(
            (s for s in sentences if any(k in s for k in ("increase", "revis", "escalat"))),
            None,
        )
        if inc_sentence and "rent" in low and not any(
            s in inc_sentence for s in ("cap", "%", "percent", "maximum")
        ):
            keys.append("uncapped_rent_increase")
        if "maintenance" not in low and "repair" not in low:
            keys.append("unclear_maintenance")
        if "notice" not in low:
            keys.append("missing_notice_period")

        findings = [
            FindingDraft(
                issue_type=k, severity=_ISSUES[k][0], confidence=0.7,
                explanation=_ISSUES[k][1], impact=_ISSUES[k][2], action_text=_ISSUES[k][3],
            )
            for k in keys
        ]
        risk = min(100, sum(SEVERITY_POINTS[f.severity] for f in findings))
        metric = HeadlineMetric(name="Rental Fairness", value=risk, band=band(risk))

        strengths = []
        if "notice" in low:
            strengths.append("A notice period is specified.")
        if "terminat" in low:
            strengths.append("The agreement includes a termination clause.")
        if rent:
            strengths.append("The monthly rent is clearly stated.")

        summary = (
            f"This rental agreement scores {risk}/100 — {band(risk).lower()} risk. "
            + (f"It flags {len(findings)} fairness concern"
               f"{'s' if len(findings) != 1 else ''} to review before signing."
               if findings else "No major fairness concerns were found.")
        )
        return AnalyzerResult(
            analyzer_type=self.analyzer_type,
            document_family=self.document_family,
            entities=RentalEntityExtractor().extract(ctx.full_text),
            findings=findings,
            headline_metric=metric,
            strengths=strengths,
            recommendations=[f.action_text for f in findings][:6],
            summary=summary,
        )
