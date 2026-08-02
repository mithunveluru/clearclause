import re

import pdfplumber

from app.reporting import build_pdf, build_summary, render_html

DOC = {"id": 1, "filename": "loan.pdf", "source_type": "pdf", "doc_type": "loan"}
RISK = {
    "total": 72,
    "band": "High",
    "summary": "This document looks high risk because penalty charges are significant.",
    "breakdown": {"fee_opacity": 14, "penalty": 15, "renewal": 12, "consent": 0, "cancellation": 10},
}
COST = {"headline_rate": 18.0, "processing_fee": 2.0, "late_fee": 500.0,
        "renewal_fee": None, "foreclosure_charge": 4.0, "estimated_true_cost": 500.0}
FINDINGS = [
    {"issue_type": "processing_fee", "severity": "medium", "confidence": 0.9,
     "explanation": "A processing fee is charged.", "action_text": "Ask the exact fee.",
     "clause_text": "processing fee of 2% applies"},
    {"issue_type": "foreclosure_charge", "severity": "high", "confidence": 0.85,
     "explanation": "Early closure attracts a charge.", "action_text": "Ask the foreclosure charge.",
     "clause_text": "foreclosure charge of 4%"},
]


def test_build_summary_orders_and_flags():
    s = build_summary(DOC, FINDINGS, RISK, COST)
    # high severity sorts first
    assert s["findings"][0]["issue_type"] == "foreclosure_charge"
    assert s["high_risk"] is True
    assert len(s["top_findings"]) == 2
    # questions deduped from action_text
    assert s["questions"] == ["Ask the foreclosure charge.", "Ask the exact fee."]


def test_build_summary_low_risk_not_flagged():
    s = build_summary(DOC, [], {**RISK, "band": "Low"}, COST)
    assert s["high_risk"] is False
    assert s["findings"] == []


def test_pdf_has_contents_and_traceable_evidence(tmp_path):
    """The contents page resolves, and every quote says where it came from.

    The table of contents is built by a two-pass `multiBuild`; if the entry keys are not
    stable across passes ReportLab gives up, so this exercises a real failure mode.
    """
    located = [dict(f, page_number=3, section_name="Schedule of Charges") for f in FINDINGS]
    summary = build_summary(
        DOC, located, RISK, COST,
        key_dates=[{"label": "Loan Tenure", "value": "60 months",
                    "description": "Duration over which you repay this loan"}],
    )
    out = str(tmp_path / "report.pdf")
    build_pdf(summary, out)

    with pdfplumber.open(out) as pdf:
        pages = [p.extract_text() or "" for p in pdf.pages]
    text = "\n".join(pages)

    assert "Contents" in text
    # A contents line is useless without a resolved page number
    assert re.search(r"Clause Analysis\s*[. ]*\s*\d+", text), "contents entry never resolved"
    assert "Page 3" in text and "Schedule of Charges" in text
    assert "Key Dates and Periods" in text
    assert "Rs. 500" in text  # estimated true cost carries the unit it is known to have


def test_pdf_omits_key_dates_when_there_are_none():
    """No entities extracted must not leave an empty section stranded in the contents."""
    import tempfile

    with tempfile.NamedTemporaryFile(suffix=".pdf") as f:
        build_pdf(build_summary(DOC, FINDINGS, RISK, COST), f.name)
        with pdfplumber.open(f.name) as pdf:
            text = "\n".join(p.extract_text() or "" for p in pdf.pages)
    assert "Key Dates and Periods" not in text


def test_render_html_contains_key_sections():
    html = render_html(build_summary(DOC, FINDINGS, RISK, COST))
    assert "72/100" in html and "High" in html
    assert "foreclosure charge" in html.lower()
    assert "High-risk terms detected" in html  # warning banner present
    assert "Ask the exact fee." in html
