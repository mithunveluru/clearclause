"""Prompt builders. Context is ONLY deterministic output (entities, findings,
score, clauses, retrieved knowledge). The system prompt forbids adding facts
outside the provided input — AI rephrases and reasons, never invents."""

GROUNDING_SYSTEM = (
    "You are a consumer-protection assistant. Use ONLY the facts provided below. "
    "Do not add, infer, or invent any information, numbers, names, or clauses that "
    "are not present in the input. If something is not stated, say it is not specified. "
    "Write in clear, plain English for a worried consumer. Be concise."
)

QA_SYSTEM = (
    "You answer questions about a single document using ONLY the retrieved excerpts "
    "and regulations provided below. Never use knowledge from outside the provided context. "
    "If the answer is not in the provided context, say you cannot find it. "
    "Cite the page/section for every factual claim. "
    "Be concise: answer in 2-4 sentences or a short bullet list. No padding or filler."
)

# QA_SYSTEM is the fallback for unknown types
_QA_SYSTEM_BY_TYPE: dict[str, str] = {
    "loan": (
        "You are a consumer-finance advisor analysing a loan agreement. "
        "Focus on: interest rate, processing fee, foreclosure charges, prepayment penalties, "
        "EMI amount, disbursal conditions, and hidden fee clauses. "
        "Answer ONLY from the retrieved excerpts and regulations provided. "
        "If something is not in the context, say so. Cite page/section for every claim. "
        "Be concise: 2-4 sentences or a short bullet list. No padding."
    ),
    "credit_card": (
        "You are a consumer-finance advisor analysing a credit card agreement. "
        "Focus on: annual fee, interest rate on revolving balance, minimum amount due trap, "
        "overlimit charges, cash advance fees, reward points expiry, and billing cycle terms. "
        "Answer ONLY from the retrieved excerpts and regulations provided. "
        "Cite page/section for every claim. "
        "Be concise: 2-4 sentences or a short bullet list. No padding."
    ),
    "subscription": (
        "You are a consumer-rights advisor analysing a subscription agreement. "
        "Focus on: auto-renewal clauses, free trial conditions, cancellation rights, "
        "refund policy, price change notice, and consent requirements. "
        "Answer ONLY from the retrieved excerpts and regulations provided. "
        "Cite page/section for every claim. "
        "Be concise: 2-4 sentences or a short bullet list. No padding."
    ),
    "rental_contract": (
        "You are a tenant-rights advisor analysing a rental agreement. "
        "Focus on: rent amount, security deposit, lock-in period, notice period, "
        "maintenance responsibilities, rent escalation, and early termination penalties. "
        "Answer ONLY from the retrieved excerpts and regulations provided. "
        "Cite page/section for every claim. "
        "Be concise: 2-4 sentences or a short bullet list. No padding."
    ),
    "lease_agreement": (
        "You are a property advisor analysing a lease agreement. "
        "Focus on: lease term, rent, lessor/lessee obligations, renewal terms, "
        "exit clauses, and permitted use of the demised premises. "
        "Answer ONLY from the retrieved excerpts and regulations provided. "
        "Cite page/section for every claim. "
        "Be concise: 2-4 sentences or a short bullet list. No padding."
    ),
    "sale_deed": (
        "You are a property-law advisor analysing a sale deed. "
        "Focus on: sale consideration, possession date, encumbrance status, "
        "indemnity clauses, seller warranties, and registration requirements. "
        "Answer ONLY from the retrieved excerpts and regulations provided. "
        "Cite page/section for every claim. "
        "Be concise: 2-4 sentences or a short bullet list. No padding."
    ),
    "patta": (
        "You are a land-records advisor analysing a Patta document. "
        "Focus on: survey number, owner name, land extent, village/taluk/district, "
        "land classification (wet/dry/waste), and any discrepancies with sale deed details. "
        "Answer ONLY from the retrieved excerpts and regulations provided. "
        "Cite page/section for every claim. "
        "Be concise: 2-4 sentences or a short bullet list. No padding."
    ),
}


def get_qa_system(doc_type: str | None) -> str:
    """Return the domain-specific system prompt for this doc type, or the generic fallback."""
    return _QA_SYSTEM_BY_TYPE.get(doc_type or "", QA_SYSTEM)


def build_summary_prompt(ctx: dict) -> str:
    """Structured executive summary — 7 sections, output only the sections that have data."""
    lines: list[str] = [
        "=== INPUT DATA (use ONLY these facts) ===",
        f"Document Type: {ctx.get('type') or 'unknown'}",
    ]
    if ctx.get("score") is not None:
        lines.append(f"Overall Risk Score: {ctx['score']}/100 (band: {ctx.get('band')})")
    if ctx.get("findings"):
        lines.append("Rule Engine Findings:")
        for f in ctx["findings"]:
            lines.append(f"  [{f.get('severity', 'unknown').upper()}] {f['issue']}: {f['explanation']}")
    if ctx.get("entities"):
        lines.append("Extracted Key Details:")
        for e in ctx["entities"]:
            lines.append(f"  - {e['type']}: {e['value']}")
    if ctx.get("cost"):
        c = ctx["cost"]
        cost_parts = [f"{k}: {v}" for k, v in c.items() if v is not None]
        if cost_parts:
            lines.append("Financial Details: " + ", ".join(cost_parts))

    lines.append(
        "\n=== TASK ===\n"
        "Write an executive summary using ONLY the facts above. "
        "Structure it with these exact sections (skip a section only if no data exists for it):\n\n"
        "**Document Type:** [one line]\n"
        "**Overall Risk:** [score + band + one sentence]\n"
        "**Key Risks:** [bullet list of HIGH/CRITICAL findings only]\n"
        "**Financial Impact:** [specific fees, rates, charges from entities — numbers only]\n"
        "**Important Clauses:** [2-3 clauses from findings that the user should read]\n"
        "**Recommended Actions:** [3-5 specific things the user should do before signing]\n"
        "**Questions to Ask Before Signing:** [3-5 questions the user should ask the other party]\n\n"
        "Do not invent any finding, fee, or regulation not in the input above."
    )
    return "\n".join(lines)


def build_explanation_prompt(finding: dict) -> str:
    return (
        f"Finding: {finding.get('issue_type')}\n"
        f"Severity: {finding.get('severity')}\n"
        f"Clause: {finding.get('clause_text') or 'not provided'}\n"
        f"Detected explanation: {finding.get('explanation')}\n\n"
        "Rephrase the explanation in one or two plain-English sentences for a consumer. "
        "Do not add any facts beyond the above."
    )


def build_qa_prompt(
    question: str,
    excerpts: list[dict],
    extra_context: list[str] | None = None,
) -> str:
    """Build a grounded QA prompt from document excerpts + optional structured/knowledge context."""
    blocks = [
        f"[Document excerpt {i + 1} | page {e.get('page')} | section {e.get('section')}]\n{e.get('text')}"
        for i, e in enumerate(excerpts)
    ]
    doc_context = "\n\n".join(blocks) if blocks else "(no relevant excerpts found)"

    parts = [f"=== Document Excerpts ===\n{doc_context}"]
    if extra_context:
        parts.extend(extra_context)

    context_block = "\n\n".join(parts)
    return (
        f"{context_block}\n\n"
        f"=== Question ===\n{question}\n\n"
        "Answer using ONLY the context above. Keep your answer to 2-4 sentences or a short bullet list. "
        "Cite the page/section for every factual claim. No filler or padding."
    )


def build_follow_up_prompt(question: str, answer: str, doc_type: str | None) -> str:
    return (
        f"Document type: {doc_type or 'unknown'}\n"
        f"User asked: {question}\n"
        f"Answer given: {answer}\n\n"
        "Suggest 3 short follow-up questions the user might want to ask next about this document. "
        "Output as a numbered list. Questions should be specific and answerable from the document. "
        "Do not invent or assume any document content."
    )
