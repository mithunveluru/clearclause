from app.reporting import build_summary, render_html

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


def test_render_html_contains_key_sections():
    html = render_html(build_summary(DOC, FINDINGS, RISK, COST))
    assert "72/100" in html and "High" in html
    assert "foreclosure charge" in html.lower()
    assert "High-risk terms detected" in html  # warning banner present
    assert "Ask the exact fee." in html
