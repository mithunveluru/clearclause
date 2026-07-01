"""Credit card terms analyzer — fee/interest transparency. Consumer family but,
like the property analyzers, reports its own headline (Card Terms Transparency)."""
from app.analysis.base import AnalyzerContext, BaseAnalyzer
from app.analysis.helpers import headline, mk_finding
from app.contracts import AnalyzerResult
from app.core.constants import ClassifiedType, DocumentFamily
from app.entities.extractors._util import present
from app.entities.extractors.credit_card import CreditCardEntityExtractor, interest_apr


class CreditCardAnalyzer(BaseAnalyzer):
    analyzer_type = ClassifiedType.CREDIT_CARD
    document_family = DocumentFamily.CONSUMER

    def analyze(self, ctx: AnalyzerContext) -> AnalyzerResult:
        low = ctx.full_text.lower()
        apr = interest_apr(low)
        high_interest = apr is not None and apr >= 36

        findings = [f for f in [
            mk_finding(present(low, "annual fee"), "undisclosed_annual_fee", "medium",
                "The annual fee is not clearly disclosed.",
                "You may be charged a yearly fee you didn't expect.",
                "Confirm the annual fee and any waiver conditions."),
            mk_finding(not (present(low, "reward") and not present(low, "expir", "validity", "valid till")),
                "reward_expiry_ambiguity", "medium",
                "Reward points are mentioned but expiry/validity is unclear.",
                "Points may lapse before you can redeem them.",
                "Ask for the exact reward validity and expiry rules."),
            mk_finding(not present(low, "overlimit", "over limit", "over-limit"),
                "overlimit_fee_exposure", "medium",
                "An over-limit fee applies if you exceed your credit limit.",
                "Spending over the limit triggers an extra charge.",
                "Set a usage alert and confirm the over-limit fee amount."),
            mk_finding(not high_interest, "high_revolving_interest", "high",
                "The revolving interest rate is very high.",
                "Carrying a balance becomes expensive quickly.",
                "Pay the full statement balance to avoid revolving interest."),
            mk_finding(present(low, "minimum due", "minimum amount due"), "unclear_minimum_due", "medium",
                "The minimum amount due is not clearly stated.",
                "Paying only the minimum can trap you in revolving debt.",
                "Confirm how the minimum due is calculated."),
        ] if f is not None]
        metric = headline("Card Terms Transparency", findings)
        summary = (
            f"This card's terms score {metric.value}/100 — {metric.band.lower()} risk. "
            + (f"{len(findings)} transparency concern(s) to review."
               if findings else "The fee and interest terms look clearly disclosed.")
        )
        return AnalyzerResult(
            analyzer_type=self.analyzer_type, document_family=self.document_family,
            entities=CreditCardEntityExtractor().extract(ctx.full_text), findings=findings,
            headline_metric=metric, strengths=[],
            recommendations=[f.action_text for f in findings][:6], summary=summary,
        )
