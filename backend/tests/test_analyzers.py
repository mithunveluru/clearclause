import pytest

from app.analysis import AnalyzerContext, ClauseRef, get_analyzer
from app.core.constants import ClassifiedType, DocumentFamily
from app.detection import detect
from app.entities.extractors.loan import LoanEntityExtractor

pytestmark = pytest.mark.v1_regression

LOAN_CLAUSES = [
    ClauseRef(1, "A processing fee of 2 percent is deducted upfront at disbursal."),
    ClauseRef(2, "A late payment charge of Rs 500 per month applies."),
    ClauseRef(3, "Foreclosure before 12 months attracts a charge of 4 percent."),
]


def test_registry_returns_consumer_analyzer():
    a = get_analyzer(ClassifiedType.LOAN)
    assert a is not None and a.analyzer_type == ClassifiedType.LOAN
    assert a.document_family == DocumentFamily.CONSUMER
    assert get_analyzer("lease_agreement") is None  # unregistered -> V1 fallback path


def test_consumer_analyzer_preserves_detection_parity():
    a = get_analyzer(ClassifiedType.LOAN)
    ctx = AnalyzerContext(1, ClassifiedType.LOAN, DocumentFamily.CONSUMER, LOAN_CLAUSES)
    result = a.analyze(ctx)

    got = {f.issue_type for f in result.findings}
    expected = {f["issue_type"] for f in detect([(c.id, c.text) for c in LOAN_CLAUSES])}
    assert got == expected  # findings identical to V1 rule engine
    assert {"processing_fee", "late_fee", "foreclosure_charge"} <= got


def test_loan_entities_extracted():
    ents = LoanEntityExtractor().extract(" ".join(c.text for c in LOAN_CLAUSES))
    by_type = {e.entity_type: e.entity_value for e in ents}
    # The unit travels with the number
    assert by_type.get("processing_fee") == "2%"
    assert by_type.get("late_fee") == "₹500"
    assert by_type.get("foreclosure_charge") == "4%"
