class DocStatus:
    """Document processing states."""

    UPLOADED = "uploaded"
    OCR_PROCESSING = "ocr_processing"
    OCR_DONE = "ocr_done"
    ANALYSIS_PROCESSING = "analysis_processing"
    ANALYSIS_DONE = "analysis_done"
    REPORT_READY = "report_ready"
    FAILED = "failed"


class JobStatus:
    PENDING = "pending"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"


class DocumentFamily:
    CONSUMER = "consumer"
    PROPERTY = "property"
    INSURANCE = "insurance"
    MEDICAL = "medical"
    LEGAL = "legal"
    GENERAL = "general"


class ClassifiedType:
    # Financial / consumer agreements
    LOAN = "loan"
    SUBSCRIPTION = "subscription"
    CREDIT_CARD = "credit_card"
    # Financial statements & records
    BANK_STATEMENT = "bank_statement"
    CREDIT_CARD_STATEMENT = "credit_card_statement"
    PAYSLIP = "payslip"
    TAX_DOCUMENT = "tax_document"
    PERSONAL_FINANCE = "personal_finance"
    # Property
    RENTAL_CONTRACT = "rental_contract"
    RENTAL_INVOICE = "rental_invoice"
    LEASE_AGREEMENT = "lease_agreement"
    SALE_DEED = "sale_deed"
    PATTA = "patta"
    # Commercial
    INVOICE = "invoice"
    RECEIPT = "receipt"
    UTILITY_BILL = "utility_bill"
    # Insurance
    INSURANCE_POLICY = "insurance_policy"
    INSURANCE_CLAIM = "insurance_claim"
    # Medical
    MEDICAL_REPORT = "medical_report"
    PRESCRIPTION = "prescription"
    # Legal & employment
    LEGAL_CONTRACT = "legal_contract"
    EMPLOYMENT_LETTER = "employment_letter"
    GOVERNMENT_FORM = "government_form"
    # Personal & research
    RESUME = "resume"
    RESEARCH_PAPER = "research_paper"
    VEHICLE_INSPECTION = "vehicle_inspection"
    # Catch-alls (not auto-classified, available for user override)
    OTHER = "other"
    UNKNOWN = "unknown"


FAMILY_OF = {
    ClassifiedType.LOAN: DocumentFamily.CONSUMER,
    ClassifiedType.SUBSCRIPTION: DocumentFamily.CONSUMER,
    ClassifiedType.CREDIT_CARD: DocumentFamily.CONSUMER,
    ClassifiedType.BANK_STATEMENT: DocumentFamily.CONSUMER,
    ClassifiedType.CREDIT_CARD_STATEMENT: DocumentFamily.CONSUMER,
    ClassifiedType.PAYSLIP: DocumentFamily.CONSUMER,
    ClassifiedType.TAX_DOCUMENT: DocumentFamily.CONSUMER,
    ClassifiedType.PERSONAL_FINANCE: DocumentFamily.CONSUMER,
    ClassifiedType.RENTAL_CONTRACT: DocumentFamily.PROPERTY,
    ClassifiedType.RENTAL_INVOICE: DocumentFamily.PROPERTY,
    ClassifiedType.LEASE_AGREEMENT: DocumentFamily.PROPERTY,
    ClassifiedType.SALE_DEED: DocumentFamily.PROPERTY,
    ClassifiedType.PATTA: DocumentFamily.PROPERTY,
    ClassifiedType.INVOICE: DocumentFamily.GENERAL,
    ClassifiedType.RECEIPT: DocumentFamily.GENERAL,
    ClassifiedType.UTILITY_BILL: DocumentFamily.GENERAL,
    ClassifiedType.INSURANCE_POLICY: DocumentFamily.INSURANCE,
    ClassifiedType.INSURANCE_CLAIM: DocumentFamily.INSURANCE,
    ClassifiedType.MEDICAL_REPORT: DocumentFamily.MEDICAL,
    ClassifiedType.PRESCRIPTION: DocumentFamily.MEDICAL,
    ClassifiedType.LEGAL_CONTRACT: DocumentFamily.LEGAL,
    ClassifiedType.EMPLOYMENT_LETTER: DocumentFamily.LEGAL,
    ClassifiedType.GOVERNMENT_FORM: DocumentFamily.LEGAL,
    ClassifiedType.RESUME: DocumentFamily.GENERAL,
    ClassifiedType.RESEARCH_PAPER: DocumentFamily.GENERAL,
    ClassifiedType.VEHICLE_INSPECTION: DocumentFamily.GENERAL,
    ClassifiedType.OTHER: DocumentFamily.GENERAL,
}

