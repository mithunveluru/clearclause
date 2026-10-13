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


# Segmentation returns one block per section, not one per sentence, so several fee
# findings routinely share the same text. This is that text, as OCR actually produced it.
MERGED_BLOCK = (
    "PERSONAL LOAN AGREEMENT A processing fee of 2 percent of the sanctioned amount "
    "shall be deducted at the time of disbursal. A late payment charge of Rs 500 per "
    "month will be levied on any overdue installment. Foreclosure of the loan before "
    "12 months will attract a charge of 4 percent on the outstanding principal."
)


def test_each_fee_is_read_from_its_own_sentence():
    # Reading the first amount in the shared block gave every fee the late payment's
    # Rs 500, and summed it three times into a true cost of Rs 1,500 that no document
    # anywhere stated.
    findings = [
        {"issue_type": t, "severity": "high", "clause_text": MERGED_BLOCK}
        for t in ("processing_fee", "late_fee", "foreclosure_charge")
    ]

    cost = estimate_cost(findings, [MERGED_BLOCK])

    assert (cost["processing_fee"], cost["processing_fee_unit"]) == (2.0, PERCENT)
    assert (cost["late_fee"], cost["late_fee_unit"]) == (500.0, INR)
    assert (cost["foreclosure_charge"], cost["foreclosure_charge_unit"]) == (4.0, PERCENT)
    # Only the one genuine rupee amount is summable
    assert cost["estimated_true_cost"] == 500.0


def test_a_fee_the_block_never_names_still_reads_the_block():
    # The fallback must not regress: a block that is only about one fee has no sentence
    # naming it, and the amount is still there to be found
    cost = estimate_cost(
        [{"issue_type": "processing_fee", "severity": "high", "clause_text": "Rs 750 is payable upfront."}],
        [],
    )
    assert (cost["processing_fee"], cost["processing_fee_unit"]) == (750.0, INR)


# A fee table OCRs as one unpunctuated run: no full stop anywhere to split on, so the
# sentence splitter hands the whole line to every fee and the first rupee figure in it
# wins. Here that figure belongs to the late payment charge, and it was being reported
# as the foreclosure charge too — off by two orders of magnitude and in the wrong unit.
FEE_TABLE = (
    "Processing fee 2 percent of loan amount Late payment charge Rs. 750 per month "
    "Foreclosure charge 4 percent of outstanding principal"
)


def test_each_fee_is_read_from_its_own_span_when_there_are_no_sentences():
    findings = [
        {"issue_type": t, "severity": "high", "clause_text": FEE_TABLE}
        for t in ("processing_fee", "late_fee", "foreclosure_charge")
    ]

    cost = estimate_cost(findings, [FEE_TABLE])

    assert (cost["processing_fee"], cost["processing_fee_unit"]) == (2.0, PERCENT)
    assert (cost["late_fee"], cost["late_fee_unit"]) == (750.0, INR)
    assert (cost["foreclosure_charge"], cost["foreclosure_charge_unit"]) == (4.0, PERCENT)
    assert cost["estimated_true_cost"] == 750.0


def test_a_fee_named_twice_keeps_its_own_amount():
    # Clipping at this fee's *own* second mention would cut the sentence before the
    # figure and report the late fee as having no amount at all.
    cost = estimate_cost(
        [{"issue_type": "late_fee", "severity": "high",
          "clause_text": "Late payment: overdue amounts attract Rs. 500 per month."}],
        [],
    )
    assert (cost["late_fee"], cost["late_fee_unit"]) == (500.0, INR)
