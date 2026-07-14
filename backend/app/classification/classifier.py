"""Rule-based document classifier: weighted keyword signals + filename hints.

A score of 1-2 routes to "confirm" rather than UNKNOWN, so a weak signal asks
rather than guesses. UNKNOWN needs empty text and no filename hint.
"""
import re

from app.contracts import ClassificationResult, SecondaryCandidate
from app.core.config import settings
from app.core.constants import FAMILY_OF, ClassifiedType

_MIN_SCORE = 3

# High-weight (≥3) keywords must be unique to one type
SIGNALS: dict[str, list[tuple[str, int]]] = {
    # Property
    ClassifiedType.PATTA: [
        ("survey number", 3), ("patta", 3), ("chitta", 3), ("taluk", 2),
        ("land classification", 2), ("subdivision", 2), ("extent", 1),
        ("village", 1), ("district", 1),
    ],
    ClassifiedType.RENTAL_CONTRACT: [
        ("landlord", 3), ("tenant", 3), ("monthly rent", 3), ("security deposit", 2),
        ("lock-in period", 2), ("notice period", 2), ("rental agreement", 2), ("rent", 1),
    ],
    ClassifiedType.RENTAL_INVOICE: [
        ("rent receipt", 4), ("rent invoice", 4), ("payment for rent", 3),
        ("rental invoice", 4), ("monthly rent receipt", 3), ("rent paid", 2),
    ],
    ClassifiedType.LEASE_AGREEMENT: [
        ("lease agreement", 4), ("lessor", 3), ("lessee", 3), ("lease term", 2),
        ("demised premises", 2), ("lease deed", 3),
    ],
    ClassifiedType.SALE_DEED: [
        ("sale deed", 4), ("sale consideration", 3), ("encumbrance", 3),
        ("conveyance", 2), ("possession", 2), ("vendor", 2), ("vendee", 2),
        ("seller", 1), ("buyer", 1), ("registration", 1),
    ],
    # Consumer finance agreements
    ClassifiedType.LOAN: [
        ("loan agreement", 4), ("processing fee", 3), ("foreclosure", 3),
        ("disbursal", 2), ("emi", 2), ("prepayment", 2), ("sanctioned amount", 3),
        ("sanctioned", 2), ("apr", 2), ("interest rate", 1), ("loan tenure", 2),
    ],
    ClassifiedType.CREDIT_CARD: [
        ("credit card", 4), ("annual fee", 3), ("minimum due", 3), ("billing cycle", 2),
        ("cash advance", 2), ("credit limit", 2), ("overlimit", 2),
        ("statement date", 2), ("reward", 1),
    ],
    ClassifiedType.SUBSCRIPTION: [
        ("subscription agreement", 4), ("auto-renew", 3), ("auto renew", 3),
        ("free trial", 3), ("subscription", 2), ("recurring", 2),
        ("renews automatically", 3), ("renews", 1), ("trial period", 2), ("trial", 1),
    ],
    # Financial statements & records
    ClassifiedType.BANK_STATEMENT: [
        ("bank statement", 4), ("account statement", 3), ("opening balance", 3),
        ("closing balance", 2), ("transaction history", 2), ("ifsc", 2),
        ("account number", 1), ("debit", 1), ("credit", 1),
    ],
    ClassifiedType.CREDIT_CARD_STATEMENT: [
        ("credit card statement", 4), ("statement of account", 3), ("minimum payment due", 3),
        ("payment due date", 2), ("outstanding balance", 2), ("new charges", 2),
        ("previous balance", 2), ("total amount due", 1),
    ],
    ClassifiedType.PAYSLIP: [
        ("payslip", 4), ("pay slip", 4), ("salary slip", 4),
        ("basic salary", 3), ("hra", 3), ("net pay", 3),
        ("gross salary", 2), ("provident fund", 2), ("allowance", 1),
    ],
    ClassifiedType.TAX_DOCUMENT: [
        ("form 16", 4), ("form 26as", 4), ("tax deducted at source", 4),
        ("tds", 3), ("income tax", 3), ("assessment year", 3),
        ("itr", 2), ("net taxable income", 2), ("gross salary", 2),
    ],
    ClassifiedType.PERSONAL_FINANCE: [
        ("mutual fund statement", 4), ("folio number", 4), ("net worth", 4),
        ("nav", 3), ("sip", 3), ("units held", 3),
        ("investment portfolio", 3), ("portfolio valuation", 2),
    ],
    # Commercial
    ClassifiedType.INVOICE: [
        ("tax invoice", 4), ("invoice number", 3), ("invoice date", 2),
        ("bill to", 2), ("unit price", 2), ("subtotal", 2),
        ("gst", 1), ("invoice", 1),
    ],
    ClassifiedType.RECEIPT: [
        ("payment received", 3), ("receipt number", 3), ("cash receipt", 3),
        ("amount paid", 2), ("payment confirmation", 2), ("receipt", 2),
        ("total paid", 2),
    ],
    ClassifiedType.UTILITY_BILL: [
        ("electricity bill", 4), ("water bill", 4), ("gas bill", 4),
        ("meter reading", 3), ("units consumed", 3), ("consumer number", 3),
        ("connection number", 2), ("bill date", 1),
    ],
    # Insurance
    ClassifiedType.INSURANCE_POLICY: [
        ("insurance policy", 4), ("policy number", 3), ("sum insured", 3),
        ("policy holder", 3), ("premium", 2), ("nominee", 2),
        ("coverage", 2), ("insured", 1),
    ],
    ClassifiedType.INSURANCE_CLAIM: [
        ("claim form", 4), ("insurance claim", 4), ("claim settlement", 3),
        ("claim number", 3), ("claim amount", 3), ("claimant", 2),
        ("reimbursement", 2),
    ],
    # Medical
    ClassifiedType.MEDICAL_REPORT: [
        ("medical report", 4), ("lab report", 4), ("pathology", 3),
        ("clinical report", 3), ("blood report", 3), ("test results", 2),
        ("diagnosis", 2), ("patient name", 1),
    ],
    ClassifiedType.PRESCRIPTION: [
        ("prescription", 4), ("dosage", 3), ("pharmacy", 2),
        ("tablets", 2), ("capsules", 2), ("mg", 1), ("rx", 1),
    ],
    # Legal & employment
    ClassifiedType.LEGAL_CONTRACT: [
        ("jurisdiction", 3), ("arbitration", 3), ("dispute resolution", 3),
        ("governing law", 3), ("legal contract", 4), ("indemnity", 2),
        ("obligations", 1), ("agreement", 1),
    ],
    ClassifiedType.EMPLOYMENT_LETTER: [
        ("offer letter", 4), ("appointment letter", 4), ("joining date", 3),
        ("ctc", 3), ("probation", 2), ("designation", 2),
        ("employee", 1), ("employer", 1),
    ],
    ClassifiedType.GOVERNMENT_FORM: [
        ("government of india", 4), ("official use only", 4), ("ministry", 3),
        ("affidavit", 3), ("notary", 3), ("application form", 2),
        ("declaration", 1), ("department", 1),
    ],
    # Personal & research
    ClassifiedType.RESUME: [
        ("curriculum vitae", 4), ("work experience", 3), ("skills", 2),
        ("objective", 2), ("education", 1), ("projects", 1), ("references", 1),
    ],
    ClassifiedType.RESEARCH_PAPER: [
        ("doi", 4), ("peer review", 4), ("bibliography", 3), ("methodology", 3),
        ("abstract", 2), ("journal", 2), ("literature review", 3),
    ],
    ClassifiedType.VEHICLE_INSPECTION: [
        ("vehicle inspection", 4), ("odometer", 3), ("chassis number", 3),
        ("engine number", 2), ("vin", 2), ("vehicle condition", 2),
        ("inspection checklist", 2),
    ],
}

# Filename hints: (regex, type, score boost)
_FILENAME_HINTS: list[tuple[re.Pattern, str, int]] = [
    (re.compile(r"pay.?slip|salary.?slip", re.I), ClassifiedType.PAYSLIP, 4),
    (re.compile(r"bank.?stat|account.?stat", re.I), ClassifiedType.BANK_STATEMENT, 4),
    (re.compile(r"cc.?stat|credit.?card.?stat|card.?stat", re.I), ClassifiedType.CREDIT_CARD_STATEMENT, 4),
    (re.compile(r"invoice", re.I), ClassifiedType.INVOICE, 4),
    (re.compile(r"\breceipt\b", re.I), ClassifiedType.RECEIPT, 4),
    (re.compile(r"form.?16|form.?26|tds|itr[\d_]", re.I), ClassifiedType.TAX_DOCUMENT, 4),
    (re.compile(r"rent.?receipt|rent.?invoice", re.I), ClassifiedType.RENTAL_INVOICE, 4),
    (re.compile(r"insurance.?polic|policy.*\.(pdf|jpg|png)$", re.I), ClassifiedType.INSURANCE_POLICY, 4),
    (re.compile(r"insurance.?claim|claim.?form", re.I), ClassifiedType.INSURANCE_CLAIM, 4),
    (re.compile(r"medical.?report|lab.?report|patholog", re.I), ClassifiedType.MEDICAL_REPORT, 4),
    (re.compile(r"prescript", re.I), ClassifiedType.PRESCRIPTION, 4),
    (re.compile(r"offer.?letter|appointment.?letter", re.I), ClassifiedType.EMPLOYMENT_LETTER, 4),
    (re.compile(r"utility.?bill|electric.*bill|water.*bill|gas.*bill", re.I), ClassifiedType.UTILITY_BILL, 4),
    (re.compile(r"mutual.?fund|portfolio|folio|nav.?stat", re.I), ClassifiedType.PERSONAL_FINANCE, 4),
    (re.compile(r"\bresume\b|curriculum.?vitae|\bcv\b", re.I), ClassifiedType.RESUME, 4),
    (re.compile(r"research|journal.*paper|paper.*journal", re.I), ClassifiedType.RESEARCH_PAPER, 4),
    (re.compile(r"loan.?agree|home.?loan|personal.?loan", re.I), ClassifiedType.LOAN, 4),
    (re.compile(r"rental.?agree|rent.?agree", re.I), ClassifiedType.RENTAL_CONTRACT, 4),
    (re.compile(r"sale.?deed", re.I), ClassifiedType.SALE_DEED, 4),
    (re.compile(r"patta|chitta", re.I), ClassifiedType.PATTA, 4),
    (re.compile(r"vehicle.?inspect|car.?inspect", re.I), ClassifiedType.VEHICLE_INSPECTION, 4),
    (re.compile(r"legal.?contract", re.I), ClassifiedType.LEGAL_CONTRACT, 4),
    (re.compile(r"govern.*form|affidavit", re.I), ClassifiedType.GOVERNMENT_FORM, 4),
    (re.compile(r"lease.?deed|lease.?agree", re.I), ClassifiedType.LEASE_AGREEMENT, 4),
    (re.compile(r"subscript", re.I), ClassifiedType.SUBSCRIPTION, 4),
    (re.compile(r"credit.?card.?agree|card.?agree", re.I), ClassifiedType.CREDIT_CARD, 4),
]


def _filename_boosts(filename: str | None) -> dict[str, int]:
    if not filename:
        return {}
    boosts: dict[str, int] = {}
    for pattern, doc_type, weight in _FILENAME_HINTS:
        if pattern.search(filename):
            boosts[doc_type] = boosts.get(doc_type, 0) + weight
    return boosts


def _routing_action(confidence: float) -> str:
    if confidence >= settings.CLASSIFICATION_AUTO_THRESHOLD:
        return "auto"
    if confidence >= settings.CLASSIFICATION_CONFIRM_THRESHOLD:
        return "confirm"
    return "manual"


def _to_confidence(raw_score: int, margin: int, total_candidates: int) -> float:
    base = 0.35 + 0.06 * raw_score + 0.04 * margin
    if total_candidates >= 3:
        base -= 0.10
    return min(0.98, round(base, 2))


class RuleBasedClassifier:
    def classify(self, text: str, filename: str | None = None) -> ClassificationResult:
        low = (text or "").lower()
        scores: dict[str, int] = {}
        matched: dict[str, dict[str, int]] = {}

        for doc_type, signals in SIGNALS.items():
            hit = {kw: w for kw, w in signals if kw in low}
            if hit:
                scores[doc_type] = sum(hit.values())
                matched[doc_type] = hit

        # Apply filename boosts on top of keyword scores.
        for doc_type, boost in _filename_boosts(filename).items():
            scores[doc_type] = scores.get(doc_type, 0) + boost
            if doc_type not in matched:
                matched[doc_type] = {"[filename hint]": boost}

        qualifying = {t: s for t, s in scores.items() if s >= _MIN_SCORE}

        if not qualifying:
            # Partial-match path: score 1-2 → confirm rather than UNKNOWN.
            partial = {t: s for t, s in scores.items() if s > 0}
            if partial:
                ranked_p = sorted(partial.items(), key=lambda x: x[1], reverse=True)
                best_type, _ = ranked_p[0]
                secondary = [
                    SecondaryCandidate(
                        classified_type=t,
                        confidence=round(0.25 + 0.06 * s, 2),
                    )
                    for t, s in ranked_p[1:4]
                ]
                return ClassificationResult(
                    classified_type=best_type,
                    document_family=FAMILY_OF.get(best_type),
                    confidence=0.45,
                    signals=matched.get(best_type, {}),
                    secondary_candidates=secondary,
                    routing_action="confirm",
                )
            return ClassificationResult(
                classified_type=ClassifiedType.UNKNOWN,
                document_family=None,
                confidence=0.15,
                signals={},
                secondary_candidates=[],
                routing_action="manual",
            )

        ranked = sorted(qualifying.items(), key=lambda x: x[1], reverse=True)
        best_type, best_score = ranked[0]
        second_score = ranked[1][1] if len(ranked) > 1 else 0
        margin = best_score - second_score

        confidence = _to_confidence(best_score, margin, len(ranked))

        secondary = [
            SecondaryCandidate(
                classified_type=t,
                confidence=min(0.98, round(0.35 + 0.06 * s, 2)),
            )
            for t, s in ranked[1:4]
        ]

        return ClassificationResult(
            classified_type=best_type,
            document_family=FAMILY_OF.get(best_type),
            confidence=confidence,
            signals=matched[best_type],
            secondary_candidates=secondary,
            routing_action=_routing_action(confidence),
        )


_default = RuleBasedClassifier()


def get_classifier() -> RuleBasedClassifier:
    return _default
