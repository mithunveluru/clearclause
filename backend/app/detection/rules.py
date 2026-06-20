"""Explainable detection rules as data. One row = one issue type.

Patterns are whitespace-tolerant so OCR dropping/adding spaces
("processingfee", "auto renew") still matches. Match runs on lowercased text.
"""
import re

# (issue_type, regex, severity, confidence, explanation, action)
_RAW: list[tuple[str, str, str, float, str, str]] = [
    ("processing_fee", r"processing\s*fee", "medium", 0.9,
     "A processing fee is charged, often deducted upfront from the disbursed amount so you receive less than the headline loan.",
     "Ask for the exact processing fee amount and confirm whether it is deducted before disbursal."),
    ("service_fee", r"(service|convenience|handling)\s*(fee|charge)", "medium", 0.85,
     "A service/convenience fee adds to the real cost beyond the advertised price.",
     "Request a full breakdown of every service or convenience charge."),
    ("hidden_fee", r"(hidden|undisclosed)\s*(fee|charge)|other\s+charges\s+may\s+apply|non[-\s]*refundable", "high", 0.7,
     "Wording points to charges that are not clearly itemized, which can hide the true cost.",
     "Demand an itemized, total list of all charges in writing before agreeing."),
    ("late_fee", r"late\s*(payment\s*)?(fee|charge|penalty)|overdue\s+(charge|interest)|penal\s+interest", "medium", 0.9,
     "Late or overdue payments trigger extra penalty charges.",
     "Confirm the late fee amount, grace period, and how it compounds."),
    ("prepayment_penalty", r"pre[-\s]*payment\s*(charge|penalty|fee)|prepayment\s+(charge|penalty)", "high", 0.85,
     "Paying the loan off early incurs a penalty, reducing the benefit of early repayment.",
     "Ask whether early repayment is penalty-free and get the prepayment charge in writing."),
    ("foreclosure_charge", r"fore[-\s]*closure\s*(charge|fee|penalty)?", "high", 0.85,
     "Closing the loan before tenure ends attracts a foreclosure charge.",
     "Get the exact foreclosure charge and the conditions under which it is waived."),
    ("auto_renew_trap", r"auto[-\s]*renew|automatically\s+renew|renews\s+automatically|recurring\s+(payment|debit|charge)|auto[-\s]*debit|auto\s*pay|standing\s+instruction|e[-\s]*mandate", "high", 0.9,
     "The plan renews and charges you automatically unless you actively stop it.",
     "Note the renewal date and cancel before it if you do not want to continue; check how to revoke the mandate."),
    ("hard_cancellation", r"cannot\s+be\s+cancel|non[-\s]*cancellable|unless\s+(you\s+)?cancel|cancellation\s+(is\s+)?(not\s+|only\s+)|no\s+refund\s+on\s+cancel", "high", 0.8,
     "Cancelling appears restricted or one-sided, making it hard to exit.",
     "Find the exact cancellation steps, notice period, and any cancellation fee before signing up."),
    ("bundled_addon", r"insurance\s+(is\s+)?(included|bundled|added|mandatory)|add[-\s]*on|bundled\s+with|pre[-\s]*(selected|ticked|checked)", "medium", 0.8,
     "An add-on (often insurance) is bundled in, increasing cost — sometimes pre-selected without clear opt-in.",
     "Ask to remove any bundled add-on you did not explicitly choose and see the price without it."),
    ("implied_consent", r"deemed\s+(to\s+have\s+)?(consent|accept|agree)|implied\s+consent|by\s+continuing[, ]+you\s+agree|shall\s+be\s+deemed", "high", 0.8,
     "Consent is assumed from inaction rather than an explicit, informed choice.",
     "Do not rely on silence — give or withhold consent explicitly and in writing."),
    ("vague_pricing_revision", r"(charges|fees|prices|rates|terms)\s+may\s+be\s+(revised|changed|amended|modified)|subject\s+to\s+change\s+without\s+notice|at\s+(its|our|the\s+company'?s)\s+(sole\s+)?discretion", "high", 0.8,
     "Prices or terms can be changed unilaterally, often without clear notice.",
     "Ask for advance-notice guarantees and a cap on how much fees/rates can rise."),
]

# Potential impact ("what it could cost you") — first-class, shared by API + PDF.
IMPACT = {
    "processing_fee": "You receive less than the headline loan amount, raising your effective borrowing cost.",
    "service_fee": "The real price is higher than advertised once these add-on charges are included.",
    "hidden_fee": "Unitemized charges can surface later and inflate the total you actually pay.",
    "late_fee": "A single missed or delayed payment can add a recurring penalty on top of interest.",
    "prepayment_penalty": "Paying early to save on interest is partly cancelled out by this penalty.",
    "foreclosure_charge": "Exiting the loan early costs a percentage of the outstanding balance.",
    "auto_renew_trap": "You keep being charged after the trial or term unless you actively cancel in time.",
    "hard_cancellation": "Leaving is restricted, so you may be locked into paying for longer than you want.",
    "bundled_addon": "You pay for an add-on you may not need, often without an explicit opt-in.",
    "implied_consent": "You can be bound to terms you never actively agreed to.",
    "vague_pricing_revision": "Your costs can rise after you sign, with little or no notice.",
}

RULES = [
    {
        "issue_type": t, "pattern": re.compile(p, re.IGNORECASE),
        "severity": s, "confidence": c, "explanation": e, "action_text": a,
        "impact": IMPACT[t],
    }
    for (t, p, s, c, e, a) in _RAW
]

# Document-level: a clear total-cost disclosure should be present. Its ABSENCE
# is the finding, so this is checked once over the whole document.
DISCLOSURE_RE = re.compile(
    r"\b(apr|annual\s+percentage\s+rate|total\s+(amount|cost)\s+payable"
    r"|total\s+repayment|effective\s+(annual\s+)?interest\s+rate)\b",
    re.IGNORECASE,
)
MISSING_DISCLOSURE = {
    "issue_type": "missing_cost_disclosure",
    "severity": "high",
    "confidence": 0.6,
    "explanation": "No clear total-cost or APR-style disclosure was found, so the true all-in cost is not stated upfront.",
    "action_text": "Ask for the APR and the total amount payable (principal + all fees + interest) before agreeing.",
    "impact": "Without a stated all-in cost, you cannot compare this offer fairly or know what you will really pay.",
}
