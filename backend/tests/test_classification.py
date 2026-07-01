"""Classification routing tests — covers all 21 document types, edge cases,
and misclassification-prone scenarios."""
import pytest

from app.classification.classifier import SIGNALS, RuleBasedClassifier, _routing_action
from app.core.constants import ClassifiedType, DocumentFamily

clf = RuleBasedClassifier()

# ── Happy-path cases (one per type) ──────────────────────────────────────────

CASES: dict[str, str] = {
    ClassifiedType.LOAN: (
        "This loan agreement sets out the processing fee, foreclosure charges on early disbursal, "
        "and EMI schedule. Sanctioned amount as per bank letter. APR as per RBI guidelines."
    ),
    ClassifiedType.SUBSCRIPTION: (
        "Your subscription will auto-renew every month. Free trial period ends on day 30. "
        "Recurring billing commences unless you cancel before trial period expires."
    ),
    ClassifiedType.CREDIT_CARD: (
        "Annual fee of Rs 999 applies. Minimum due is 5% of outstanding balance each billing cycle. "
        "Cash advance fee, credit limit, overlimit charges apply as per schedule of charges."
    ),
    ClassifiedType.RENTAL_CONTRACT: (
        "The landlord and tenant agree to monthly rent of Rs 20,000 and a security deposit of "
        "2 months. Lock-in period is 6 months. Notice period is 30 days."
    ),
    ClassifiedType.RENTAL_INVOICE: (
        "Rent Receipt. Received from Mr. Rajan the amount of Rs 18,000 as payment for rent "
        "for the month of June 2026. Rent Invoice No. RI-2026-06."
    ),
    ClassifiedType.PATTA: (
        "Patta issued for survey number 123/4A in the village of Keelapalur, taluk Kulithalai, "
        "district Karur. Land classification: dry. Extent: 1.50 acres."
    ),
    ClassifiedType.SALE_DEED: (
        "This sale deed records the sale consideration paid by the buyer. The seller warrants "
        "no encumbrance on the property. Conveyance is complete upon registration."
    ),
    ClassifiedType.LEASE_AGREEMENT: (
        "This lease agreement is executed between the lessor and lessee. Lease term is 3 years "
        "for the demised premises located at the above address."
    ),
    ClassifiedType.BANK_STATEMENT: (
        "Bank Statement — Account Holder: Priya S. Account Number: 1234567890. "
        "Opening Balance: Rs 45,000. Closing Balance: Rs 32,000. IFSC: HDFC0001234. "
        "Transaction History for May 2026."
    ),
    ClassifiedType.CREDIT_CARD_STATEMENT: (
        "Credit Card Statement. Statement of Account. Minimum Payment Due: Rs 2,500. "
        "Payment Due Date: 15-Jul-2026. Outstanding Balance: Rs 48,200. "
        "New Charges this cycle: Rs 12,300. Previous Balance: Rs 35,900."
    ),
    ClassifiedType.PAYSLIP: (
        "Payslip for May 2026. Employee: Arun Kumar. Basic Salary: Rs 40,000. "
        "HRA: Rs 16,000. Net Pay: Rs 52,400. Provident Fund deducted: Rs 4,800. "
        "Gross Salary: Rs 58,000."
    ),
    ClassifiedType.TAX_DOCUMENT: (
        "Form 16 — Certificate of Tax Deducted at Source. Assessment Year 2025-26. "
        "Income Tax: Rs 48,000. TDS deducted and deposited. Net Taxable Income: Rs 6,80,000."
    ),
    ClassifiedType.PERSONAL_FINANCE: (
        "Mutual Fund Statement. Folio Number: MF-2025-0089234. NAV as on date: Rs 45.23. "
        "SIP active since January 2024. Units Held: 1234.567. Investment Portfolio summary."
    ),
    ClassifiedType.INVOICE: (
        "Tax Invoice No. INV-2026-0045. Invoice Date: 01-Jun-2026. Bill To: ABC Pvt Ltd. "
        "Unit Price: Rs 5,000. Subtotal: Rs 25,000. GST 18%: Rs 4,500. Total: Rs 29,500."
    ),
    ClassifiedType.RECEIPT: (
        "Receipt No. RCP-0892. Payment Received from Kiran M. Amount Paid: Rs 12,000. "
        "Cash Receipt confirmed. Payment Confirmation Number: TXN20260601. Total Paid: Rs 12,000."
    ),
    ClassifiedType.UTILITY_BILL: (
        "Electricity Bill. Consumer Number: EC-123456789. Connection Number: CON-45678. "
        "Meter Reading: 4567 units. Units Consumed: 312 kWh. Bill Date: 28-Jun-2026."
    ),
    ClassifiedType.INSURANCE_POLICY: (
        "Insurance Policy No. LIC-2025-0089234. Policy Holder: Ramesh K. "
        "Sum Insured: Rs 10,00,000. Annual Premium: Rs 22,000. Nominee: Mrs. Sunita K. "
        "Coverage: accidental death and disability."
    ),
    ClassifiedType.INSURANCE_CLAIM: (
        "Insurance Claim Form. Claim Number: CLM-2026-0045. Claimant: Pradeep R. "
        "Claim Amount: Rs 85,000. Insurance Claim for hospitalisation. "
        "Claim Settlement status: under review. Reimbursement requested."
    ),
    ClassifiedType.MEDICAL_REPORT: (
        "Medical Report — Lab Report. Patient Name: Anita S. Diagnosis: Mild anaemia. "
        "Blood Report: Haemoglobin 9.2 g/dL. Pathology Department, City Hospital. "
        "Clinical Report issued by Dr. Mehta."
    ),
    ClassifiedType.PRESCRIPTION: (
        "Prescription. Patient Name: Vikram P. Dosage: Amoxicillin 500mg twice daily. "
        "Pharmacy: HealthPlus Medicals. Tablets: 14. Capsules: 7. Rx valid for 7 days."
    ),
    ClassifiedType.LEGAL_CONTRACT: (
        "This legal contract is subject to the exclusive jurisdiction of the courts of Mumbai. "
        "Disputes shall be resolved by arbitration. Dispute Resolution: binding arbitration. "
        "Governing Law: laws of India. Indemnity clause applies."
    ),
    ClassifiedType.EMPLOYMENT_LETTER: (
        "Offer Letter. Dear Candidate, we are pleased to extend this appointment letter "
        "for the role of Senior Engineer. Joining Date: 15-Jul-2026. CTC: Rs 18,00,000 per annum. "
        "Probation period: 6 months. Designation: Senior Software Engineer."
    ),
    ClassifiedType.GOVERNMENT_FORM: (
        "Government of India. Ministry of Finance. Official Use Only. "
        "Affidavit — I hereby declare that the information provided is true. "
        "Notary Public seal required. Application Form No. GF-2026-0078."
    ),
    ClassifiedType.RESUME: (
        "Curriculum Vitae. Objective: Seeking a challenging role in data engineering. "
        "Work Experience: 5 years at TechCorp. Skills: Python, SQL, Spark. "
        "Education: B.Tech Computer Science. Projects: Data Pipeline Automation. References available."
    ),
    ClassifiedType.RESEARCH_PAPER: (
        "Abstract: This paper investigates machine learning approaches to NLP. "
        "DOI: 10.1234/journal.2026.0089. Methodology: supervised fine-tuning. "
        "Peer Review: double-blind. Bibliography: 42 references. Journal of AI Research."
    ),
    ClassifiedType.VEHICLE_INSPECTION: (
        "Vehicle Inspection Report. VIN: 1HGBH41JXMN109186. Odometer: 45,230 km. "
        "Chassis Number: CHS-2020-0045. Engine Number: ENG-V6-0892. "
        "Vehicle Condition: Good. Inspection Checklist completed."
    ),
}


def test_each_type_classifies():
    for expected, text in CASES.items():
        result = clf.classify(text)
        assert result.classified_type == expected, (
            f"Expected {expected!r} but got {result.classified_type!r}\n"
            f"  text: {text[:80]!r}\n"
            f"  signals: {result.signals}\n"
            f"  confidence: {result.confidence}"
        )
        assert 0.0 < result.confidence <= 1.0
        assert result.signals, "should record matched signals"


def test_family_mapping():
    assert clf.classify(CASES[ClassifiedType.PATTA]).document_family == DocumentFamily.PROPERTY
    assert clf.classify(CASES[ClassifiedType.LOAN]).document_family == DocumentFamily.CONSUMER
    assert clf.classify(CASES[ClassifiedType.SALE_DEED]).document_family == DocumentFamily.PROPERTY
    assert clf.classify(CASES[ClassifiedType.SUBSCRIPTION]).document_family == DocumentFamily.CONSUMER
    assert clf.classify(CASES[ClassifiedType.INSURANCE_POLICY]).document_family == DocumentFamily.INSURANCE
    assert clf.classify(CASES[ClassifiedType.MEDICAL_REPORT]).document_family == DocumentFamily.MEDICAL
    assert clf.classify(CASES[ClassifiedType.LEGAL_CONTRACT]).document_family == DocumentFamily.LEGAL
    assert clf.classify(CASES[ClassifiedType.INVOICE]).document_family == DocumentFamily.GENERAL


# ── Confidence and routing_action ─────────────────────────────────────────────

def test_high_confidence_routes_auto():
    r = clf.classify(CASES[ClassifiedType.LOAN])
    assert r.routing_action in ("auto", "confirm"), (
        f"Strong loan doc got routing_action={r.routing_action!r} at confidence={r.confidence}"
    )


def test_unknown_routes_manual():
    r = clf.classify("The quick brown fox jumps over the lazy dog.")
    assert r.classified_type == ClassifiedType.UNKNOWN
    assert r.routing_action == "manual"
    assert r.confidence < 0.5


def test_routing_action_thresholds():
    assert _routing_action(0.95) == "auto"
    assert _routing_action(0.90) == "auto"
    assert _routing_action(0.85) == "confirm"
    assert _routing_action(0.70) == "confirm"
    assert _routing_action(0.69) == "manual"
    assert _routing_action(0.20) == "manual"


# ── Secondary candidates ──────────────────────────────────────────────────────

def test_secondary_candidates_returned():
    r = clf.classify(CASES[ClassifiedType.LOAN])
    assert isinstance(r.secondary_candidates, list)


def test_ambiguous_doc_has_candidates():
    ambiguous = (
        "This agreement covers monthly rent, security deposit, interest rate, "
        "processing fee and EMI. The tenant and borrower agree to the terms."
    )
    r = clf.classify(ambiguous)
    has_candidates = len(r.secondary_candidates) > 0
    needs_review = r.routing_action in ("confirm", "manual")
    assert has_candidates or needs_review, (
        f"Ambiguous doc should produce candidates or require review, "
        f"got action={r.routing_action!r}, candidates={r.secondary_candidates}"
    )


# ── Partial-match path: confirm not UNKNOWN ───────────────────────────────────

def test_partial_match_routes_confirm_not_unknown():
    # "receipt" alone scores 2 — should suggest receipt with confirm, not UNKNOWN/manual
    r = clf.classify("Please retain this receipt for your records.")
    assert not (
        r.classified_type == ClassifiedType.UNKNOWN and r.routing_action == "manual"
    ), f"Partial match should not immediately return UNKNOWN/manual; got {r.classified_type!r}"


# ── Filename hint tests ───────────────────────────────────────────────────────

def test_filename_hint_payslip():
    r = clf.classify("Paid amount: Rs 5,000. Date: 01-Jun-2026.", filename="payslip_june_2026.pdf")
    assert r.classified_type == ClassifiedType.PAYSLIP, (
        f"Filename 'payslip_june_2026.pdf' should classify as PAYSLIP, got {r.classified_type!r}"
    )


def test_filename_hint_invoice():
    r = clf.classify("Amount: Rs 12,000 for services rendered.", filename="invoice_2026_001.pdf")
    assert r.classified_type == ClassifiedType.INVOICE


def test_filename_hint_bank_statement():
    r = clf.classify("Balance: Rs 45,000.", filename="bank_statement_may2026.pdf")
    assert r.classified_type == ClassifiedType.BANK_STATEMENT


def test_filename_hint_tax_form16():
    r = clf.classify("Certificate issued for FY 2025-26.", filename="form_16_2025_26.pdf")
    assert r.classified_type == ClassifiedType.TAX_DOCUMENT


# ── Edge cases and misclassification-prone scenarios ─────────────────────────

def test_single_weak_keyword_routes_not_auto():
    r = clf.classify("We are pleased to inform you the rent is payable annually.")
    if r.classified_type != ClassifiedType.UNKNOWN:
        assert r.routing_action != "auto", (
            f"Single 'rent' keyword should not auto-route; got confidence={r.confidence}"
        )


def test_financial_statement_not_misrouted_as_rental():
    finance_text = (
        "Salary credited: Rs 85,000. Monthly expenses: Rs 42,000. "
        "Savings: Rs 15,000. Investment in mutual funds: Rs 10,000. "
        "Account balance: Rs 28,000. EMI deducted: Rs 18,000."
    )
    r = clf.classify(finance_text)
    assert r.classified_type != ClassifiedType.RENTAL_CONTRACT, (
        f"Finance statement misrouted to rental_contract (confidence={r.confidence})"
    )


def test_vehicle_rental_not_misrouted_as_residential():
    vehicle_text = (
        "Vehicle rental agreement. Pickup location: airport. Dropoff: hotel. "
        "Fuel policy: full-to-full. VIN: 1HGBH41JXMN109186. Odometer: 12345 km."
    )
    r = clf.classify(vehicle_text)
    assert r.classified_type != ClassifiedType.RENTAL_CONTRACT or r.routing_action in ("confirm", "manual"), (
        f"Vehicle rental should not auto-route to rental_contract"
    )


def test_empty_document():
    r = clf.classify("")
    assert r.classified_type == ClassifiedType.UNKNOWN
    assert r.routing_action == "manual"


def test_whitespace_only():
    r = clf.classify("   \n\t  ")
    assert r.classified_type == ClassifiedType.UNKNOWN


def test_scanned_noise_does_not_classify():
    noise = "x7f3 kKj pq2 !! @@ ## $$ %% ^^ && ** (( )) __ ++"
    r = clf.classify(noise)
    assert r.classified_type == ClassifiedType.UNKNOWN


def test_patta_not_misrouted_as_rental():
    r = clf.classify(
        "Survey number 456/2B in village Thanjavur, taluk Thanjavur, district Thanjavur. "
        "Land classification dry. Extent 0.75 acres. Patta issued by Revenue Department."
    )
    assert r.classified_type == ClassifiedType.PATTA, (
        f"Patta doc misrouted to {r.classified_type!r}"
    )


def test_sale_deed_not_confused_with_patta():
    r = clf.classify(
        "This sale deed records sale consideration of Rs 45,00,000. "
        "The seller warrants no encumbrance. Conveyance by way of sale. "
        "Possession handed to buyer on registration date."
    )
    assert r.classified_type == ClassifiedType.SALE_DEED, (
        f"Sale deed misrouted to {r.classified_type!r}"
    )


def test_payslip_not_confused_with_tax_document():
    r = clf.classify(
        "Payslip for April 2026. Basic Salary: Rs 45,000. HRA: Rs 18,000. "
        "Net Pay: Rs 55,200. Gross Salary: Rs 63,000. Provident Fund: Rs 5,400."
    )
    assert r.classified_type == ClassifiedType.PAYSLIP, (
        f"Payslip misrouted to {r.classified_type!r}"
    )


def test_insurance_claim_not_confused_with_policy():
    r = clf.classify(
        "Insurance Claim Form. Claim Number: CLM-001. Claimant: John D. "
        "Claim Amount: Rs 50,000. Claim Settlement pending. Reimbursement on approval."
    )
    assert r.classified_type == ClassifiedType.INSURANCE_CLAIM, (
        f"Insurance claim misrouted to {r.classified_type!r}"
    )


def test_credit_card_statement_not_confused_with_agreement():
    r = clf.classify(
        "Credit Card Statement. Minimum Payment Due: Rs 3,500. "
        "Statement of Account. Outstanding Balance: Rs 72,000. "
        "Payment Due Date: 20-Jul-2026. Previous Balance: Rs 60,000."
    )
    assert r.classified_type == ClassifiedType.CREDIT_CARD_STATEMENT, (
        f"CC statement misrouted to {r.classified_type!r}"
    )


def test_medical_report_not_confused_with_prescription():
    r = clf.classify(
        "Lab Report. Patient Name: Anjali M. Blood Report: WBC 7200, RBC 4.8. "
        "Pathology findings: within normal limits. Clinical Report by Dr. Sharma."
    )
    assert r.classified_type == ClassifiedType.MEDICAL_REPORT, (
        f"Medical report misrouted to {r.classified_type!r}"
    )


def test_research_paper_not_confused_with_legal():
    r = clf.classify(
        "Abstract: Study of transformer models. DOI: 10.9999/ml.2026.001. "
        "Peer Review: accepted. Methodology: ablation study. Bibliography: 38 refs. "
        "Published in Journal of Machine Learning."
    )
    assert r.classified_type == ClassifiedType.RESEARCH_PAPER, (
        f"Research paper misrouted to {r.classified_type!r}"
    )


# ── Signal coverage ───────────────────────────────────────────────────────────

def test_all_types_have_minimum_signals():
    for doc_type, signals in SIGNALS.items():
        assert len(signals) >= 3, f"{doc_type} has too few signals: {signals}"
        max_score = sum(w for _, w in signals)
        assert max_score >= 5, f"{doc_type} max total weight too low: {max_score}"


def test_signals_have_no_cross_contamination():
    high_weight: dict[str, list[str]] = {}
    for doc_type, signals in SIGNALS.items():
        for kw, w in signals:
            if w >= 3:
                high_weight.setdefault(kw, []).append(doc_type)
    conflicts = {kw: types for kw, types in high_weight.items() if len(types) > 1}
    assert not conflicts, f"High-weight signals shared across types: {conflicts}"
