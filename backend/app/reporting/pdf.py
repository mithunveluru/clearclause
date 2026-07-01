"""Purpose-built consumer risk report as a PDF (ReportLab, not HTML->PDF).

Layout: cover, executive summary, risk overview, key findings, clause analysis,
cost impact, recommended actions, appendix — with running header/footer + page
numbers. Built from the report summary dict produced by build_summary().
"""
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    HRFlowable,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

INK = colors.HexColor("#191919")
INK2 = colors.HexColor("#5f5f63")
INK3 = colors.HexColor("#9a9aa0")
LINE = colors.HexColor("#e0e0e4")
WASH = colors.HexColor("#f6f6f7")

BAND = {
    "Low": colors.HexColor("#1a7f5a"),
    "Moderate": colors.HexColor("#b2670a"),
    "High": colors.HexColor("#c0362c"),
    "Critical": colors.HexColor("#7c1d12"),
}
SEV = {
    "critical": colors.HexColor("#7c1d12"),
    "high": colors.HexColor("#c0362c"),
    "medium": colors.HexColor("#b2670a"),
    "low": colors.HexColor("#1a7f5a"),
}
CATEGORY_MAX = {"fee_opacity": 20, "penalty": 15, "renewal": 15, "consent": 15, "cancellation": 10}
CATEGORY_LABEL = {
    "fee_opacity": "Fee opacity",
    "penalty": "Penalty severity",
    "renewal": "Auto-renew risk",
    "consent": "Consent weakness",
    "cancellation": "Cancellation friction",
}


def _label(issue_type: str) -> str:
    return issue_type.replace("_", " ").title()


def _hx(color) -> str:
    return "#" + color.hexval()[2:]  # reportlab markup needs a leading '#'


def _styles():
    s = getSampleStyleSheet()
    base = ParagraphStyle("body", parent=s["BodyText"], fontName="Helvetica",
                          fontSize=10, leading=15, textColor=INK2, spaceAfter=0)
    return {
        "eyebrow": ParagraphStyle("eyebrow", fontName="Helvetica-Bold", fontSize=8.5,
                                  textColor=INK3, leading=12, spaceAfter=4),
        "h1": ParagraphStyle("h1", fontName="Helvetica-Bold", fontSize=15, textColor=INK,
                             leading=19, spaceBefore=6, spaceAfter=10),
        "h2": ParagraphStyle("h2", fontName="Helvetica-Bold", fontSize=11, textColor=INK,
                             leading=15, spaceAfter=3),
        "body": base,
        "small": ParagraphStyle("small", parent=base, fontSize=9, textColor=INK3, leading=13),
        "quote": ParagraphStyle("quote", parent=base, fontName="Helvetica-Oblique",
                                fontSize=9.5, textColor=INK2, leftIndent=10, leading=14),
        "coverTitle": ParagraphStyle("ct", fontName="Helvetica-Bold", fontSize=30,
                                     textColor=INK, leading=34, alignment=TA_CENTER),
        "coverSub": ParagraphStyle("cs", fontName="Helvetica", fontSize=12, textColor=INK2,
                                   leading=18, alignment=TA_CENTER),
    }


def _bar(value: float, maxv: int, color, width: float = 5.2 * cm):
    frac = max(0.0, min(1.0, (value or 0) / maxv))
    filled = max(0.06 * cm, width * frac)
    empty = max(0.0, width - filled)
    t = Table([["", ""]], colWidths=[filled, empty], rowHeights=[0.22 * cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, 0), color),
        ("BACKGROUND", (1, 0), (1, 0), WASH),
        ("LINEBEFORE", (0, 0), (-1, -1), 0, colors.white),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        *[(p, (0, 0), (-1, -1), 0) for p in
          ("LEFTPADDING", "RIGHTPADDING", "TOPPADDING", "BOTTOMPADDING")],
    ]))
    return t


def _finding_box(f: dict, st: dict):
    sev = (f.get("severity") or "low").lower()
    inner = [
        Paragraph(
            f'<font color="{_hx(SEV.get(sev, INK))}"><b>{sev.upper()}</b></font>'
            f'&nbsp;&nbsp;<b><font size="11">{_label(f["issue_type"])}</font></b>',
            st["body"],
        ),
        Spacer(1, 5),
        Paragraph(f["explanation"], st["body"]),
    ]
    if f.get("impact"):
        inner += [Spacer(1, 5),
                  Paragraph(f'<b>Why it matters.</b> {f["impact"]}', st["body"])]
    if f.get("clause_text"):
        inner += [Spacer(1, 6), Paragraph(f'“{f["clause_text"]}”', st["quote"])]
    inner += [Spacer(1, 6),
              Paragraph(f'<b>Recommended action.</b> {f["action_text"]}', st["body"])]

    box = Table([[inner]], colWidths=[16.0 * cm])
    box.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.white),
        ("BOX", (0, 0), (-1, -1), 0.6, LINE),
        ("LINEBEFORE", (0, 0), (0, -1), 2.2, SEV.get(sev, INK)),
        ("LEFTPADDING", (0, 0), (-1, -1), 14),
        ("RIGHTPADDING", (0, 0), (-1, -1), 14),
        ("TOPPADDING", (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
    ]))
    return box


def build_pdf(summary: dict, out_path: str) -> str:
    st = _styles()
    doc_meta = summary["document"]
    score = summary["score"]
    cost = summary["cost"]
    findings = summary["findings"]
    band = score["band"]
    band_color = BAND.get(band, INK)
    generated = datetime.utcnow().strftime("%d %b %Y")

    def decorate(canvas, _doc):
        canvas.saveState()
        w, h = A4
        if canvas.getPageNumber() > 1:
            canvas.setFont("Helvetica", 8)
            canvas.setFillColor(INK3)
            canvas.drawString(2 * cm, h - 1.25 * cm, "ClearClause  ·  Consumer Risk Report")
            canvas.drawRightString(w - 2 * cm, h - 1.25 * cm, "Confidential")
            canvas.setStrokeColor(LINE)
            canvas.line(2 * cm, h - 1.4 * cm, w - 2 * cm, h - 1.4 * cm)
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(INK3)
        canvas.drawString(2 * cm, 1.2 * cm, f"Generated {generated}")
        canvas.drawRightString(w - 2 * cm, 1.2 * cm, f"Page {canvas.getPageNumber()}")
        canvas.restoreState()

    story = []

    # Cover
    story += [Spacer(1, 5.5 * cm)]
    story += [Paragraph("CONSUMER RISK REPORT", st["eyebrow"])]
    story += [Spacer(1, 6), Paragraph("Document Risk Assessment", st["coverTitle"])]
    story += [Spacer(1, 14), Paragraph(doc_meta["filename"], st["coverSub"])]
    story += [Spacer(1, 1.4 * cm)]
    badge = Table([[Paragraph(
        f'<font color="white"><b>{score["total"]} / 100&nbsp;&nbsp;·&nbsp;&nbsp;{band.upper()} RISK</b></font>',
        ParagraphStyle("b", fontName="Helvetica-Bold", fontSize=13, alignment=TA_CENTER,
                       textColor=colors.white))]], colWidths=[9 * cm])
    badge.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), band_color),
        ("TOPPADDING", (0, 0), (-1, -1), 12), ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    ]))
    story += [badge, Spacer(1, 1.0 * cm)]
    story += [Paragraph(f"Prepared by ClearClause · {generated}", st["coverSub"])]
    story += [Spacer(1, 2.4 * cm),
              Paragraph("This assessment is informational and does not constitute legal or "
                        "financial advice.", st["small"])]
    story += [PageBreak()]

    # Executive summary
    story += [Paragraph("Executive Summary", st["h1"]),
              Paragraph(score["summary"], st["body"]), Spacer(1, 10)]
    stat = Table([[
        Paragraph(f'<b><font size="18">{score["total"]}</font></b>/100<br/><font color="#888888">'
                  f'Risk score</font>', st["body"]),
        Paragraph(f'<b><font size="18">{len(findings)}</font></b><br/><font color="#888888">'
                  f'Issues found</font>', st["body"]),
        Paragraph(f'<b><font size="18">{band}</font></b><br/><font color="#888888">'
                  f'Overall band</font>', st["body"]),
    ]], colWidths=[5.3 * cm, 5.3 * cm, 5.3 * cm])
    stat.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.6, LINE), ("INNERGRID", (0, 0), (-1, -1), 0.6, LINE),
        ("TOPPADDING", (0, 0), (-1, -1), 12), ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
        ("LEFTPADDING", (0, 0), (-1, -1), 14), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story += [stat, Spacer(1, 18)]

    # Risk overview
    story += [Paragraph("Risk Overview", st["h1"])]
    rows = []
    for key, maxv in CATEGORY_MAX.items():
        val = score["breakdown"].get(key, 0)
        rows.append([Paragraph(CATEGORY_LABEL[key], st["body"]), _bar(val, maxv, band_color),
                     Paragraph(f"{val}/{maxv}", st["small"])])
    overview = Table(rows, colWidths=[5.5 * cm, 6.0 * cm, 4.5 * cm])
    overview.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LINEBELOW", (0, 0), (-1, -2), 0.5, LINE),
    ]))
    story += [overview, Spacer(1, 18)]

    # Key findings
    story += [Paragraph("Key Findings", st["h1"])]
    if summary["top_findings"]:
        for f in summary["top_findings"]:
            sev = (f.get("severity") or "low").lower()
            story += [Paragraph(
                f'<font color="{_hx(SEV.get(sev, INK))}"><b>•</b></font>&nbsp;&nbsp;'
                f'<b>{_label(f["issue_type"])}</b> — {f["explanation"]}', st["body"]),
                Spacer(1, 6)]
    else:
        story += [Paragraph("No material risks were detected.", st["body"])]
    story += [Spacer(1, 8), PageBreak()]

    # Clause analysis
    story += [Paragraph("Clause Analysis", st["h1"]),
              Paragraph("Every flagged clause, with the exact wording, why it matters, and "
                        "what to do.", st["small"]), Spacer(1, 12)]
    if findings:
        for f in findings:
            story += [_finding_box(f, st), Spacer(1, 10)]
    else:
        story += [Paragraph("No risky clauses were found in this document.", st["body"])]

    # Cost impact
    story += [Spacer(1, 8), Paragraph("Cost Impact Assessment", st["h1"])]
    cost_rows = [["Component", "Stated value"]]
    for key, label in [("headline_rate", "Headline rate"), ("processing_fee", "Processing fee"),
                       ("late_fee", "Late fee"), ("renewal_fee", "Renewal fee"),
                       ("foreclosure_charge", "Foreclosure charge"),
                       ("estimated_true_cost", "Estimated true cost")]:
        v = cost.get(key)
        cost_rows.append([label, f"{v:,}" if v is not None else "—"])
    ctab = Table(cost_rows, colWidths=[10 * cm, 6 * cm])
    ctab.setStyle(TableStyle([
        ("FONT", (0, 0), (-1, 0), "Helvetica-Bold", 9), ("TEXTCOLOR", (0, 0), (-1, 0), INK),
        ("FONT", (0, 1), (-1, -1), "Helvetica", 10), ("TEXTCOLOR", (0, 1), (-1, -1), INK2),
        ("LINEBELOW", (0, 0), (-1, 0), 0.8, LINE), ("LINEBELOW", (0, 1), (-1, -2), 0.4, LINE),
        ("BACKGROUND", (0, -1), (-1, -1), WASH), ("FONT", (0, -1), (-1, -1), "Helvetica-Bold", 10),
        ("TEXTCOLOR", (0, -1), (-1, -1), INK), ("ALIGN", (1, 0), (1, -1), "RIGHT"),
        ("TOPPADDING", (0, 0), (-1, -1), 7), ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("LEFTPADDING", (0, 0), (-1, -1), 10), ("RIGHTPADDING", (0, 0), (-1, -1), 10),
    ]))
    story += [ctab, Spacer(1, 6),
              Paragraph("Percentages are shown as stated and are not added to the estimated "
                        "true cost, which sums known currency amounts only.", st["small"])]

    # Recommended actions
    story += [Spacer(1, 16), Paragraph("Recommended Actions", st["h1"])]
    for i, q in enumerate(summary["questions"], 1):
        story += [Paragraph(f"<b>{i}.</b>&nbsp;&nbsp;{q}", st["body"]), Spacer(1, 5)]
    if not summary["questions"]:
        story += [Paragraph("No specific actions required.", st["body"])]

    # Appendix
    story += [Spacer(1, 16), HRFlowable(width="100%", thickness=0.5, color=LINE),
              Spacer(1, 10), Paragraph("Appendix · Methodology", st["h2"]),
              Paragraph("ClearClause extracts the document text, segments it into individual "
                        "clauses, and applies an explainable rule engine. Every finding traces "
                        "to specific wording in the document — there are no opaque, model-only "
                        "judgements. The risk score is a weighted sum across fee opacity, "
                        "penalties, auto-renewal, consent, and cancellation friction.", st["small"]),
              Spacer(1, 8),
              Paragraph("This report is informational and does not constitute legal or financial "
                        "advice. Always read the full agreement before signing.", st["small"])]

    SimpleDocTemplate(
        out_path, pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm,
        topMargin=2 * cm, bottomMargin=2 * cm, title="ClearClause Consumer Risk Report",
    ).build(story, onFirstPage=decorate, onLaterPages=decorate)
    return out_path
