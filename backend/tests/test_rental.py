from app.analysis import AnalyzerContext, ClauseRef, get_analyzer
from app.core.constants import ClassifiedType, DocumentFamily
from app.entities.extractors.rental import RentalEntityExtractor

RENTAL = [
    ClauseRef(1, "The monthly rent is Rs 25000 payable monthly."),
    ClauseRef(2, "The security deposit is Rs 150000, equal to six months rent."),
    ClauseRef(3, "Lock-in period of 9 months applies."),
    ClauseRef(4, "The landlord may terminate this agreement at any time."),
    ClauseRef(5, "Rent shall be increased by the landlord every year at discretion."),
]


def test_rental_registered_as_property_analyzer():
    a = get_analyzer(ClassifiedType.RENTAL_CONTRACT)
    assert a is not None
    assert a.analyzer_type == ClassifiedType.RENTAL_CONTRACT
    assert a.document_family == DocumentFamily.PROPERTY


def test_rental_findings_and_headline():
    a = get_analyzer(ClassifiedType.RENTAL_CONTRACT)
    res = a.analyze(AnalyzerContext(1, ClassifiedType.RENTAL_CONTRACT, DocumentFamily.PROPERTY, RENTAL))
    types = {f.issue_type for f in res.findings}
    assert {"excessive_deposit", "restrictive_lock_in", "one_sided_termination",
            "uncapped_rent_increase"} <= types
    assert res.headline_metric is not None
    assert res.headline_metric.name == "Rental Fairness"
    assert 0 < res.headline_metric.value <= 100
    assert res.recommendations  # negotiation checklist
    assert res.summary


def test_rental_entities():
    ents = {e.entity_type: e.entity_value for e in RentalEntityExtractor().extract(
        " ".join(c.text for c in RENTAL))}
    assert ents.get("rent_amount") == "25000"
    assert ents.get("deposit_amount") == "150000"
    assert ents.get("lock_in_period") == "9 months"
