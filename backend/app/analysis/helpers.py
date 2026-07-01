"""Shared analyzer helpers: a missing-field finding factory and a headline risk
metric derived from finding severities (higher value = more risk / less healthy)."""
from app.contracts import FindingDraft, HeadlineMetric
from app.scoring.risk import SEVERITY_POINTS, band


def mk_finding(
    present: bool, issue_type: str, severity: str, explanation: str, impact: str, action: str
) -> FindingDraft | None:
    """Returns a finding only when the thing is missing/triggered (present=False)."""
    if present:
        return None
    return FindingDraft(
        issue_type=issue_type, severity=severity, confidence=0.8,
        explanation=explanation, impact=impact, action_text=action,
    )



def risk_value(findings: list[FindingDraft]) -> int:
    return min(100, sum(SEVERITY_POINTS.get(f.severity, 7) for f in findings))


def headline(name: str, findings: list[FindingDraft]) -> HeadlineMetric:
    v = risk_value(findings)
    return HeadlineMetric(name=name, value=v, band=band(v))
