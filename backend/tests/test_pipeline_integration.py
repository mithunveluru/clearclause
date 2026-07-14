"""Integration: full analysis pipeline (segment -> detect -> score -> report)."""
from tests.pipeline_helper import run_pipeline
import pytest
pytestmark = pytest.mark.v1_regression


RISKY = [
    "PERSONAL LOAN AGREEMENT",
    "A processing fee of 2 percent is deducted upfront at disbursal.",
    "A late payment charge of Rs 500 per month applies on overdue amounts.",
    "Foreclosure before 12 months attracts a charge of 4 percent.",
    "Charges may be revised at the sole discretion of the company.",
]


def test_risky_document_full_pipeline():
    r = run_pipeline(RISKY, "loan.txt")

    # detection found the expected issue types
    assert {"processing_fee", "late_fee", "foreclosure_charge", "vague_pricing_revision"} <= r["types"]
    # no APR/total-cost language -> missing disclosure fires
    assert "missing_cost_disclosure" in r["types"]

    # scoring produced a non-trivial, capped score
    assert r["cats"]["total"] >= 25
    assert r["band"] in ("Moderate", "High", "Critical")
    assert r["cats"]["fee_opacity"] <= 20 and r["cats"]["penalty"] <= 15

    # true-cost takes the currency amount, not percentages
    assert r["cost"]["late_fee"] == 500.0

    # report renders with the score and an action
    html = r["html"]
    assert f"{r['cats']['total']}/100" in html
    assert "processing fee" in html.lower()


def test_clean_document_is_quiet():
    clean = [
        "PERSONAL LOAN SUMMARY",
        "The annual percentage rate (APR) for this loan is 11.5 percent.",
        "The total amount payable over the full term is Rs 1,12,000.",
        "You may repay the loan early at any time with no extra cost.",
    ]
    r = run_pipeline(clean)
    assert r["findings"] == []
    assert r["band"] == "Low"
    assert r["cats"]["total"] == 0
