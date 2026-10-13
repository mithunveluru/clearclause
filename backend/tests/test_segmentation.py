from app.segmentation import classify_clause, normalize_text, segment
from app.segmentation.segmenter import is_heading, split_clauses
import pytest
pytestmark = pytest.mark.v1_regression



def test_normalize_strips_junk_and_collapses():
    assert normalize_text("Late   fee​  is  5%.....") == "Late fee is 5%."
    assert normalize_text("“quoted” – dash") == '"quoted" - dash'


def test_is_heading():
    assert is_heading("FEES AND CHARGES")
    assert is_heading("Renewal:")
    assert not is_heading("A processing fee of 2% applies to every disbursal.")


def test_split_clauses_splits_and_drops_fragments():
    text = "A processing fee applies. The loan auto-renews monthly; cancel anytime."
    parts = split_clauses(text)
    assert "A processing fee applies." in parts
    assert any("auto-renews" in p for p in parts)
    assert all(len(p) >= 8 for p in parts)


def test_classify_priority():
    assert classify_clause("A late payment charge of 5% applies") == "penalty"  # not fee
    assert classify_clause("The plan will auto-renew every month") == "renewal"
    assert classify_clause("A non-refundable processing fee applies") == "fee"
    assert classify_clause("Insurance is bundled with this loan") == "add_on"
    assert classify_clause("The sky is blue") == "general"


def test_segment_carries_section_and_classifies():
    blocks = [
        (1, "FEES AND CHARGES"),
        (1, "A processing fee of 2% applies. A late payment charge of 500 is levied."),
        (2, "RENEWAL"),
        (2, "This subscription auto-renews unless cancelled before the trial ends."),
    ]
    clauses = segment(blocks)
    by_text = {c["normalized_text"]: c for c in clauses}

    fee = next(c for c in clauses if c["clause_type"] == "fee")
    assert fee["section_name"] == "FEES AND CHARGES"
    assert fee["page_number"] == 1

    renewal = next(c for c in clauses if c["clause_type"] == "renewal")
    assert renewal["section_name"] == "RENEWAL"
    assert renewal["page_number"] == 2

    assert any(c["clause_type"] == "penalty" for c in clauses)
    # headings themselves are not emitted as clauses
    assert "FEES AND CHARGES" not in by_text


def test_a_rupee_amount_stays_with_the_fee_it_belongs_to():
    # "Rs." is how money is written in these documents. Splitting on it severed the
    # figure from the clause describing it, so the fee read as having no amount at
    # all — the analyzer then reported nothing about a charge that was on the page.
    text = "A late payment charge of Rs. 500 per month will be levied on any overdue amount."

    assert split_clauses(text) == [text]


def test_abbreviations_do_not_end_a_sentence():
    text = "The fee is Rs. 2,500 payable to M/s. Acme Ltd. before disbursal."

    assert split_clauses(text) == [text]


def test_real_sentence_boundaries_still_split():
    text = (
        "A processing fee of 2 percent shall be deducted. "
        "Foreclosure attracts a charge of 4 percent on the principal."
    )

    assert split_clauses(text) == [
        "A processing fee of 2 percent shall be deducted.",
        "Foreclosure attracts a charge of 4 percent on the principal.",
    ]


def test_an_initial_does_not_end_a_sentence():
    text = "This agreement is executed by A. Kumar on behalf of the lender."

    assert split_clauses(text) == [text]


def test_a_semicolon_ends_a_clause():
    # A semicolon never abbreviates, and legal text separates fees with one far more
    # often than with a full stop. Merging here read the processing fee as Rs 500 —
    # the amount belonging to the late payment charge on the other side of the ';'.
    text = "The borrower shall pay a processing fee of 2 percent; a late payment charge of Rs. 500 applies."

    assert split_clauses(text) == [
        "The borrower shall pay a processing fee of 2 percent;",
        "a late payment charge of Rs. 500 applies.",
    ]
