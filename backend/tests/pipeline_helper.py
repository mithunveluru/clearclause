"""Shared helper: run the full analysis pipeline on plain text lines.

Exercises segmentation -> detection -> scoring -> reporting with no DB/OCR, so
it is deterministic and runs anywhere. Not collected by pytest (no test_ prefix).
"""
from app.detection import detect
from app.reporting import build_summary, render_html
from app.scoring import estimate_cost, score_findings
from app.scoring.risk import band, summarize
from app.segmentation import segment


def run_pipeline(lines: list[str], filename: str = "doc.txt") -> dict:
    clauses = segment([(1, line) for line in lines if line.strip()])
    indexed = list(enumerate(clauses))
    findings = detect([(i, c["normalized_text"]) for i, c in indexed])

    fdicts = [
        {"issue_type": f["issue_type"], "severity": f["severity"], "clause_text": f.get("clause_text")}
        for f in findings
    ]
    texts = [c["normalized_text"] for c in clauses]
    cats = score_findings(fdicts, texts)
    cost = estimate_cost(fdicts, texts)

    report_findings = [
        {
            "issue_type": f["issue_type"],
            "severity": f["severity"],
            "confidence": f["confidence"],
            "explanation": f["explanation"],
            "action_text": f["action_text"],
            "clause_text": f.get("clause_text"),
        }
        for f in findings
    ]
    summary = build_summary(
        doc={"id": 1, "filename": filename, "source_type": "text", "doc_type": None},
        findings=report_findings,
        risk={
            "total": cats["total"],
            "band": band(cats["total"]),
            "summary": summarize(cats),
            "breakdown": {k: v for k, v in cats.items() if k != "total"},
        },
        cost=cost,
    )
    return {
        "clauses": clauses,
        "findings": findings,
        "types": {f["issue_type"] for f in findings},
        "cats": cats,
        "band": band(cats["total"]),
        "cost": cost,
        "summary": summary,
        "html": render_html(summary),
    }
