from app.detection import detect

BAD_CLAUSES = [
    (1, "A processing fee of 2% is deducted upfront from every disbursal."),
    (2, "A late payment charge of Rs 500 per month applies on overdue amounts."),
    (3, "Foreclosure charge of 4% applies if the loan is closed early."),
    (4, "This subscription will auto-renew every month unless you cancel."),
    (5, "Insurance is bundled with this loan and is mandatory."),
    (6, "You shall be deemed to have consented by continuing to use the service."),
    (7, "Charges may be revised at the company's sole discretion without notice."),
]


def _types(findings):
    return {f["issue_type"] for f in findings}


def test_bad_document_returns_expected_findings():
    found = _types(detect(BAD_CLAUSES))
    for expected in (
        "processing_fee", "late_fee", "foreclosure_charge", "auto_renew_trap",
        "bundled_addon", "implied_consent", "vague_pricing_revision",
    ):
        assert expected in found, f"missing {expected}: {found}"
    # no APR/total-cost language anywhere -> doc-level finding fires
    assert "missing_cost_disclosure" in found


def test_every_finding_is_fully_explainable():
    for f in detect(BAD_CLAUSES):
        for field in ("issue_type", "severity", "confidence", "explanation", "action_text"):
            assert f[field] not in (None, ""), f
        assert 0.0 < f["confidence"] <= 1.0


def test_clean_document_with_disclosure_is_quiet():
    clean = [
        (1, "The APR is 12% and the total amount payable is Rs 1,10,000."),
        (2, "You may cancel anytime with a full refund."),
    ]
    assert detect(clean) == []


def test_space_tolerant_match():
    # OCR dropped the space; rule must still catch it.
    assert "processing_fee" in _types(detect([(1, "a processingfee applies")]))
