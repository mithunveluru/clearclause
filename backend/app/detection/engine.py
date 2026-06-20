from app.detection.rules import DISCLOSURE_RE, MISSING_DISCLOSURE, RULES


def detect(clauses: list[tuple[int, str]]) -> list[dict]:
    """clauses: (clause_id, normalized_text). Returns finding dicts.

    Each clause is tested against every rule; a match emits one finding carrying
    that rule's issue_type/severity/confidence/explanation/action plus the exact
    clause text and id. Missing cost disclosure is a single document-level check.
    """
    findings: list[dict] = []
    for clause_id, text in clauses:
        low = text.lower()
        for rule in RULES:
            if rule["pattern"].search(low):
                findings.append(
                    {
                        "clause_id": clause_id,
                        "issue_type": rule["issue_type"],
                        "severity": rule["severity"],
                        "confidence": rule["confidence"],
                        "explanation": rule["explanation"],
                        "action_text": rule["action_text"],
                        "impact": rule["impact"],
                        "clause_text": text,
                    }
                )

    full_text = " ".join(t for _, t in clauses)
    if clauses and not DISCLOSURE_RE.search(full_text.lower()):
        findings.append({"clause_id": None, "clause_text": None, **MISSING_DISCLOSURE})
    return findings
