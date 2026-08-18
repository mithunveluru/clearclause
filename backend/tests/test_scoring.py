from app.scoring import INR, PERCENT, estimate_cost, score_findings, summarize
from app.scoring.risk import band
from app.reporting.pdf import _cost_value
import pytest
pytestmark = pytest.mark.v1_regression


BAD = [
    {"issue_type": "processing_fee", "severity": "medium", "clause_text": "processing fee of 2 percent applies"},
    {"issue_type": "hidden_fee", "severity": "high", "clause_text": "other charges may apply"},
    {"issue_type": "late_fee", "severity": "medium", "clause_text": "late payment charge of 500 rupees per month"},
    {"issue_type": "foreclosure_charge", "severity": "high", "clause_text": "foreclosure charge of 4 percent"},
    {"issue_type": "auto_renew_trap", "severity": "high", "clause_text": "auto-renews monthly"},
    {"issue_type": "implied_consent", "severity": "high", "clause_text": "deemed to have consented"},
]


def test_band_thresholds():
    assert band(0) == "Low" and band(24) == "Low"
    assert band(25) == "Moderate" and band(49) == "Moderate"
    assert band(50) == "High" and band(74) == "High"
    assert band(75) == "Critical" and band(100) == "Critical"


def test_score_caps_and_total():
    cats = score_findings(BAD, ["a clause"] * 3)
    assert cats["fee_opacity"] <= 20 and cats["penalty"] <= 15
    assert cats["total"] == min(100, sum(v for k, v in cats.items() if k != "total"))
    assert cats["total"] > 0


def test_empty_is_low_and_quiet():
    cats = score_findings([], [])
    assert cats["total"] == 0
    assert summarize(cats).startswith("No significant risks")


def test_summary_names_top_category():
    cats = score_findings(BAD, ["x"])
    assert summarize(cats).startswith("This document looks")


def test_cost_extraction_currency_vs_percent():
    cost = estimate_cost(BAD, ["interest rate of 18% per annum"])
    assert cost["late_fee"] == 500.0            # currency -> summed
    assert cost["processing_fee"] == 2.0         # percent -> stored, not summed
    assert cost["estimated_true_cost"] == 500.0  # only the currency amount
    assert cost["headline_rate"] == 18.0


def test_each_fee_carries_the_unit_it_was_written_in():
    # Rs 4 and 4% differ by orders of magnitude; the number alone cannot be shown
    cost = estimate_cost(BAD, [])

    assert (cost["late_fee"], cost["late_fee_unit"]) == (500.0, INR)
    assert (cost["processing_fee"], cost["processing_fee_unit"]) == (2.0, PERCENT)
    assert (cost["foreclosure_charge"], cost["foreclosure_charge_unit"]) == (4.0, PERCENT)
    # Stated with no figure at all: no value, and so no unit to claim
    assert (cost["renewal_fee"], cost["renewal_fee_unit"]) == (None, None)


def test_a_fee_with_no_unit_is_rendered_without_one():
    # A row written before units were recorded must not be given a guessed unit
    assert _cost_value("processing_fee", 4.0, None) == "4"
    assert _cost_value("processing_fee", 4.0, PERCENT) == "4%"
    assert _cost_value("processing_fee", 4.0, INR) == "Rs. 4"
    assert _cost_value("headline_rate", 18.0, None) == "18% p.a."
