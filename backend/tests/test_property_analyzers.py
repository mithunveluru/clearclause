from app.analysis import AnalyzerContext, ClauseRef, get_analyzer
from app.classification import get_classifier
from app.core.constants import ClassifiedType, DocumentFamily

clf = get_classifier()


def _analyze(ttype: str, lines: list[str]):
    a = get_analyzer(ttype)
    ctx = AnalyzerContext(1, ttype, a.document_family, [ClauseRef(i, l) for i, l in enumerate(lines)])
    return a.analyze(ctx)


PATTA = [
    "Patta Number: 1567", "Owner Name: Ramasamy K", "Survey Number: 245/2B",
    "Taluk: Madurai South", "District: Madurai", "Land Classification: Punjai",
    "Extent: 0.45 hectares",
]
SALE = [
    "This sale agreement between seller Vendor A and buyer Purchaser B.",
    "Survey Number: 112/3.", "The sale consideration is Rs 4500000.",
    "The buyer shall bear all costs.",
]
CARD = [
    "Annual fee: Rs 500.", "Interest rate: 42% per annum.", "Minimum due: 5%.",
    "Reward points credited on spends.", "Overlimit fee: Rs 600.",
]


def test_patta_classifies_scores_and_extracts():
    assert clf.classify(" ".join(PATTA)).classified_type == ClassifiedType.PATTA
    r = _analyze(ClassifiedType.PATTA, PATTA)
    assert r.headline_metric.name == "Patta Health"
    assert "incomplete_boundary" in {f.issue_type for f in r.findings}
    assert {e.entity_type for e in r.entities} >= {"survey_number", "owner_name", "extent"}


def test_sale_deed_flags_missing_protections():
    assert clf.classify(" ".join(SALE)).classified_type == ClassifiedType.SALE_DEED
    r = _analyze(ClassifiedType.SALE_DEED, SALE)
    assert r.headline_metric.name == "Sale Agreement Risk"
    t = {f.issue_type for f in r.findings}
    assert {"missing_refund_terms", "unclear_ownership_warranty",
            "missing_encumbrance_declaration"} <= t


def test_credit_card_transparency():
    assert clf.classify(" ".join(CARD)).classified_type == ClassifiedType.CREDIT_CARD
    r = _analyze(ClassifiedType.CREDIT_CARD, CARD)
    assert r.headline_metric.name == "Card Terms Transparency"
    assert r.document_family == DocumentFamily.CONSUMER
    t = {f.issue_type for f in r.findings}
    assert "high_revolving_interest" in t and "reward_expiry_ambiguity" in t
