"""Static knowledge packs — regulations, guidance, and consumer rights per document family.

Each entry is embedded into a separate Qdrant collection at startup and retrieved
during Q&A to ground AI answers in applicable law. Never used as the source of
findings; findings come from the rule engine only.
"""

# id must be stable: hashed into a Qdrant id
# families: consumer_finance | rental | property | insurance
KNOWLEDGE_PACKS: list[dict] = [
    # Consumer Finance
    {
        "id": "cf_rbi_fair_practices",
        "family": "consumer_finance",
        "category": "disclosure",
        "title": "RBI Fair Practices Code — Key Lender Obligations",
        "text": (
            "Under the RBI Fair Practices Code for Banks and NBFCs, lenders must: "
            "(1) Provide a loan application acknowledgment with a time limit for processing. "
            "(2) Communicate loan sanction terms in writing before disbursal. "
            "(3) Disclose all fees, charges, and penalties upfront in the sanction letter. "
            "(4) Not charge prepayment penalties on floating rate loans to individual borrowers. "
            "(5) Release all securities within 30 days of full loan repayment."
        ),
        "tags": ["rbi", "fair_practices", "disclosure", "loan"],
    },
    {
        "id": "cf_processing_fee",
        "family": "consumer_finance",
        "category": "processing_fee",
        "title": "Processing Fee — Disclosure and Deduction Rules",
        "text": (
            "RBI guidelines require lenders to disclose processing fees (also called origination "
            "fees) upfront in the sanction letter. The fee must not be deducted from the disbursed "
            "amount without explicit borrower consent. Processing fees are typically 0.5%–2% of the "
            "loan amount. Undisclosed deduction of processing fees is a prohibited practice under "
            "the Consumer Protection Act 2019 (deficiency of service)."
        ),
        "tags": ["processing_fee", "rbi", "consumer_protection"],
    },
    {
        "id": "cf_foreclosure",
        "family": "consumer_finance",
        "category": "foreclosure",
        "title": "Foreclosure and Prepayment — RBI Rules",
        "text": (
            "RBI circular RBI/2019-20/44 prohibits levy of foreclosure charges or prepayment "
            "penalties on all floating rate term loans sanctioned to individual borrowers. "
            "For fixed rate loans, foreclosure charges may apply but must be disclosed upfront. "
            "Typical industry range for fixed rate foreclosure is 2%–5% of outstanding principal. "
            "A borrower may close a loan early at any time; the lender cannot refuse early repayment."
        ),
        "tags": ["foreclosure", "prepayment", "rbi"],
    },
    {
        "id": "cf_late_fee",
        "family": "consumer_finance",
        "category": "late_fee",
        "title": "Late Payment Fees and Penalty Interest",
        "text": (
            "Lenders may charge penal interest for delayed EMI payments, but the rate must be "
            "disclosed in the loan agreement. RBI expects penal charges to be 'reasonable and not "
            "excessive'. Common practice is 1%–2% per month on the overdue amount. From January 2024, "
            "RBI guidelines mandate that penal charges must not be levied as a percentage of the "
            "entire outstanding loan — only on the overdue installment."
        ),
        "tags": ["late_fee", "penalty", "emi", "rbi"],
    },
    {
        "id": "cf_apr_disclosure",
        "family": "consumer_finance",
        "category": "interest_rate",
        "title": "Annual Percentage Rate (APR) — Disclosure Obligation",
        "text": (
            "Lenders are required to disclose the Annual Percentage Rate (APR) or effective annual "
            "rate, not merely the flat rate. The APR includes processing fees, insurance costs, "
            "and other charges. A flat rate of 10% typically translates to an APR of 18–19%. "
            "Non-disclosure of the true cost is a violation of RBI transparency guidelines and "
            "constitutes an unfair trade practice under the Consumer Protection Act 2019."
        ),
        "tags": ["apr", "interest_rate", "disclosure", "rbi"],
    },
    {
        "id": "cf_insurance_bundling",
        "family": "consumer_finance",
        "category": "insurance",
        "title": "Bundled Insurance — Disclosure and Consent",
        "text": (
            "Banks and NBFCs cannot force-bundle insurance products with loans. IRDAI and RBI "
            "guidelines require explicit written consent from the borrower before any insurance "
            "premium is added to the loan amount. Bundled insurance premiums increase the effective "
            "cost of borrowing. The borrower has the right to refuse insurance bundling without "
            "affecting loan approval."
        ),
        "tags": ["insurance", "bundling", "consent", "rbi", "irdai"],
    },
    {
        "id": "cf_credit_card_min_due",
        "family": "consumer_finance",
        "category": "minimum_due",
        "title": "Credit Card — Minimum Amount Due and Interest Trap",
        "text": (
            "Paying only the Minimum Amount Due (MAD) does not prevent interest from accruing. "
            "Interest is calculated on the full outstanding balance from the transaction date, "
            "not just the unpaid portion. RBI guidelines require card issuers to clearly disclose "
            "in statements: (1) the total outstanding balance, (2) the MAD, (3) the interest "
            "charged if only MAD is paid. Annual interest rates on credit card revolving balances "
            "typically range from 24%–42% p.a."
        ),
        "tags": ["credit_card", "minimum_due", "interest", "rbi"],
    },
    {
        "id": "cf_credit_card_annual_fee",
        "family": "consumer_finance",
        "category": "annual_fee",
        "title": "Credit Card Annual Fee — Waiver and Disclosure",
        "text": (
            "Credit card annual fees must be disclosed before card issuance. RBI mandates that "
            "if the annual fee is not waived as promised, the customer must be informed at least "
            "30 days before the charge. Customers have the right to cancel the card without penalty "
            "if the annual fee is charged contrary to what was communicated at signup. "
            "Most banks waive annual fees upon spending a specified amount in the year."
        ),
        "tags": ["credit_card", "annual_fee", "waiver", "rbi"],
    },
    {
        "id": "cf_credit_card_overlimit",
        "family": "consumer_finance",
        "category": "overlimit",
        "title": "Credit Card Overlimit Charges",
        "text": (
            "Overlimit fees are charged when spending exceeds the approved credit limit. "
            "RBI requires explicit consent from the cardholder before allowing over-limit "
            "transactions. Overlimit charges must be disclosed upfront. The customer must opt-in "
            "to overlimit facilities; it cannot be enabled by default. Typical overlimit charges "
            "range from Rs 500–2.5% of overlimit amount."
        ),
        "tags": ["credit_card", "overlimit", "consent", "rbi"],
    },
    # Rental
    {
        "id": "rental_deposit_limits",
        "family": "rental",
        "category": "security_deposit",
        "title": "Security Deposit — State-Specific Limits",
        "text": (
            "Security deposit limits vary by state. Key limits: Maharashtra — 3 months rent maximum "
            "under the Maharashtra Rent Control Act. Karnataka — no statutory cap but market norm is "
            "2–10 months. Tamil Nadu — Draft Tamil Nadu Regulation of Rights and Responsibilities "
            "of Landlords and Tenants Act caps deposit at 3 months for residential. Delhi — 2–3 "
            "months typical. Andhra/Telangana — 5–10 months. Deposits must be refunded within "
            "30 days of vacancy under Model Tenancy Act 2021."
        ),
        "tags": ["security_deposit", "rental", "tenant_rights"],
    },
    {
        "id": "rental_notice_period",
        "family": "rental",
        "category": "notice_period",
        "title": "Notice Period — Tenant and Landlord Rights",
        "text": (
            "Under the Model Tenancy Act 2021 (MTA), either party must give written notice before "
            "terminating a tenancy. Standard notice is 1 month for residential, 3 months for "
            "commercial. A notice period shorter than 30 days for residential tenancy is non-standard "
            "and may be challenged. If the landlord terminates without adequate notice, the tenant "
            "is entitled to compensation equal to the notice period rent."
        ),
        "tags": ["notice_period", "rental", "termination", "model_tenancy_act"],
    },
    {
        "id": "rental_lockin_period",
        "family": "rental",
        "category": "lock_in",
        "title": "Lock-In Period — Enforceability and Consumer Rights",
        "text": (
            "A lock-in period prevents tenants from vacating without penalty before a fixed date. "
            "Lock-in periods are generally enforceable if clearly stated in the agreement. "
            "However, courts have held that disproportionate penalties (e.g., 6 months rent for "
            "breaking a 1-month lock-in) are unconscionable and may be reduced. Under the Consumer "
            "Protection Act 2019, unfair contract terms in standard form agreements may be voided. "
            "Lock-in periods exceeding 6 months for residential agreements are unusual and warrant scrutiny."
        ),
        "tags": ["lock_in", "rental", "tenant_rights", "consumer_protection"],
    },
    {
        "id": "rental_rent_increase",
        "family": "rental",
        "category": "rent_escalation",
        "title": "Annual Rent Increase — Legal Framework",
        "text": (
            "Many states have rent control laws that cap annual rent increases for older tenancies. "
            "For newer free-market agreements, the agreed escalation clause governs. The Model "
            "Tenancy Act 2021 allows annual rent revision by mutual agreement but requires 3 months "
            "written notice. A rent increase exceeding 5%–10% annually without notice is unusual "
            "and may be challenged. Agreements permitting 'revision at the sole discretion of the "
            "landlord' are one-sided and potentially unfair."
        ),
        "tags": ["rent_increase", "escalation", "rental", "model_tenancy_act"],
    },
    {
        "id": "rental_maintenance",
        "family": "rental",
        "category": "maintenance",
        "title": "Maintenance Responsibilities — Tenant vs Landlord",
        "text": (
            "Generally: structural repairs are the landlord's responsibility; minor day-to-day "
            "maintenance is the tenant's. The Model Tenancy Act 2021 specifies that landlords "
            "must maintain the premises in a habitable condition. Clauses transferring all "
            "maintenance costs to the tenant (including structural) are one-sided. If the property "
            "becomes uninhabitable due to landlord neglect, the tenant may terminate without penalty."
        ),
        "tags": ["maintenance", "rental", "landlord_obligation", "model_tenancy_act"],
    },
    {
        "id": "rental_rera",
        "family": "rental",
        "category": "regulatory",
        "title": "RERA — Applicability to Rental Agreements",
        "text": (
            "RERA (Real Estate Regulation and Development Act 2016) primarily covers sale of "
            "real estate projects. For rental agreements, RERA does not directly apply unless "
            "the unit is part of a regulated project still under development. Rental disputes "
            "are typically handled under State Rent Control Acts or the Model Tenancy Act. "
            "The Model Tenancy Act 2021 mandates registration of all tenancy agreements above "
            "11 months with the Rent Authority."
        ),
        "tags": ["rera", "rental", "regulatory"],
    },
    # Property
    {
        "id": "property_patta_transfer",
        "family": "property",
        "category": "patta",
        "title": "Patta Transfer — Process and Legal Significance",
        "text": (
            "Patta (Record of Rights) is a government document establishing ownership of agricultural "
            "land in Tamil Nadu and other states. It is issued by the Revenue Department (Tehsildar). "
            "For a property transaction to be legally complete, patta must be transferred to the "
            "buyer's name after sale deed registration. Patta alone does not confer ownership — a "
            "registered sale deed is required. Discrepancy between patta details and sale deed "
            "details (survey number, extent, boundaries) is a red flag requiring verification."
        ),
        "tags": ["patta", "property", "land_records", "revenue_department"],
    },
    {
        "id": "property_encumbrance",
        "family": "property",
        "category": "encumbrance",
        "title": "Encumbrance Certificate — Checking Liens and Mortgages",
        "text": (
            "An Encumbrance Certificate (EC) from the Sub-Registrar's office shows all registered "
            "transactions on a property for a specified period. An EC is mandatory before any "
            "property purchase to confirm the property is free from mortgages, charges, or liens. "
            "A clean EC (Form 15) indicates no encumbrances. Form 16 is issued when no transactions "
            "exist. Banks require EC before sanctioning home loans. A sale deed without EC verification "
            "exposes the buyer to risk of third-party claims."
        ),
        "tags": ["encumbrance", "property", "sale_deed", "due_diligence"],
    },
    {
        "id": "property_registration",
        "family": "property",
        "category": "registration",
        "title": "Sale Deed Registration — Mandatory Requirements",
        "text": (
            "Under Section 17 of the Registration Act 1908, sale of immovable property exceeding "
            "Rs 100 in value must be registered. An unregistered sale deed is inadmissible as "
            "evidence of title transfer. Registration requires: executed deed, stamp duty payment, "
            "identity proof of both parties, and presentation at Sub-Registrar's office. Stamp "
            "duty varies by state (4%–8% of market value). Capital Gains tax implications arise "
            "from the transaction date, not registration date."
        ),
        "tags": ["registration", "sale_deed", "stamp_duty", "registration_act"],
    },
    {
        "id": "property_rera_sale",
        "family": "property",
        "category": "regulatory",
        "title": "RERA — Buyer Protections in Apartment/Plot Sales",
        "text": (
            "Under RERA 2016, builders must register projects before advertising or selling. "
            "Key buyer protections: (1) Compensation for delayed possession at RBI lending rate + 2%. "
            "(2) Defect liability period of 5 years for structural defects. "
            "(3) Developer cannot change approved plans without 2/3 allottee consent. "
            "(4) 70% of collections must be kept in a separate escrow account. "
            "(5) Buyers can cancel and get full refund + interest if possession is delayed beyond agreed date."
        ),
        "tags": ["rera", "property", "buyer_rights", "apartment"],
    },
    {
        "id": "property_chitta_adangal",
        "family": "property",
        "category": "land_records",
        "title": "Chitta and Adangal — Tamil Nadu Land Records",
        "text": (
            "Chitta (now merged into Patta in Tamil Nadu) is a revenue record showing ownership. "
            "Adangal (Field Measurement Book) records crop and land classification. Both are "
            "maintained by the Village Administrative Officer. In Tamil Nadu, land records have "
            "been digitized under the TNREGINET system. For agricultural land classified as "
            "'wet' or 'dry', conversion to non-agricultural use requires permission from "
            "the District Collector. Unauthorized conversion is an offense under Tamil Nadu "
            "Agricultural Lands (Prohibition of Alienation) Act."
        ),
        "tags": ["patta", "chitta", "adangal", "land_records", "tamil_nadu"],
    },
    # Insurance
    {
        "id": "insurance_free_look",
        "family": "insurance",
        "category": "cancellation",
        "title": "Free Look Period — IRDAI Regulation",
        "text": (
            "IRDAI mandates a free look period for all life insurance policies: 15 days from receipt "
            "for policies sold through in-person channels; 30 days for policies sold through distance "
            "mode (online). During this period, the policyholder can return the policy and receive "
            "a full refund minus proportionate risk premium and medical examination costs. "
            "Rejection of a free look cancellation request by an insurer is a violation of IRDAI "
            "regulations and should be reported to the IRDAI Ombudsman."
        ),
        "tags": ["insurance", "free_look", "irdai", "cancellation"],
    },
    {
        "id": "insurance_claim_settlement",
        "family": "insurance",
        "category": "claims",
        "title": "Claim Settlement — IRDAI Timelines",
        "text": (
            "IRDAI Regulation 2016 mandates: (1) Claim intimation acknowledgment within 3 days. "
            "(2) Field investigation (if required) within 30 days. (3) Claim settlement or rejection "
            "within 30 days of receipt of all documents. For life insurance: claim must be paid "
            "within 30 days of submission of all documents. Delayed payment attracts interest at "
            "2% above bank rate per annum. IRDAI permits repudiation only on grounds of material "
            "misrepresentation, fraud, or non-disclosure at the time of proposal."
        ),
        "tags": ["insurance", "claim_settlement", "irdai"],
    },
    {
        "id": "insurance_exclusion",
        "family": "insurance",
        "category": "exclusions",
        "title": "Policy Exclusions — Disclosure and Unfair Terms",
        "text": (
            "IRDAI requires all exclusions to be prominently disclosed in the policy document. "
            "Standard exclusions include: suicide (first year), pre-existing disease (typically "
            "excluded for 2–4 years in health policies), acts of war, and criminal acts. "
            "An insurer cannot reject a claim citing an exclusion that was not disclosed at "
            "the time of sale. The Consumer Protection Act 2019 enables consumers to claim "
            "compensation for non-disclosure of material exclusions."
        ),
        "tags": ["insurance", "exclusions", "irdai", "consumer_protection"],
    },
    # Subscription
    {
        "id": "subscription_auto_renewal",
        "family": "subscription",
        "category": "auto_renewal",
        "title": "Auto-Renewal — Disclosure and Consumer Rights",
        "text": (
            "Under the Consumer Protection Act 2019 and DoCA guidelines, auto-renewal clauses must "
            "be explicitly disclosed before subscription. Consumers must be given: (1) Prior notice "
            "(minimum 15 days) before auto-renewal. (2) Easy cancellation mechanism. (3) Refund for "
            "unused period if cancelled within a reasonable time. Charging for auto-renewal without "
            "clear prior notice is an unfair trade practice. The EU GDPR-inspired principle applies "
            "that opt-in must be affirmative; pre-ticked auto-renewal boxes are invalid."
        ),
        "tags": ["subscription", "auto_renewal", "consumer_protection", "disclosure"],
    },
    {
        "id": "subscription_free_trial",
        "family": "subscription",
        "category": "free_trial",
        "title": "Free Trial — Obligation to Disclose Post-Trial Charges",
        "text": (
            "A free trial that automatically converts to a paid subscription without explicit "
            "notification is an unfair trade practice. Companies must: (1) Clearly state trial "
            "period end date. (2) Send email/SMS reminder before charging. (3) Provide easy "
            "cancellation before trial ends. (4) Offer pro-rated refund if charged without "
            "adequate notice. The Consumer Protection Act 2019 defines such practices as "
            "misleading advertisements. Credit card companies are required to flag recurring "
            "transactions for cardholder verification."
        ),
        "tags": ["subscription", "free_trial", "consumer_protection", "auto_renewal"],
    },
    {
        "id": "subscription_cancellation",
        "family": "subscription",
        "category": "cancellation",
        "title": "Subscription Cancellation — Consumer Rights",
        "text": (
            "Consumers have the right to cancel any subscription service. Key protections: "
            "(1) Cancellation process must be as easy as signup. (2) No unreasonable cancellation "
            "fees unless clearly disclosed. (3) Refund for unused prepaid period must be provided "
            "unless explicitly excluded in terms. Under Consumer Protection Act 2019, making "
            "cancellation deliberately difficult (e.g., requiring phone calls, excessive steps) "
            "constitutes restrictive trade practice. DOCA (Department of Consumer Affairs) has "
            "issued advisories against 'roach motel' cancellation designs."
        ),
        "tags": ["subscription", "cancellation", "consumer_protection"],
    },
]

# Map document types to knowledge families for retrieval routing
FAMILY_MAP: dict[str, str] = {
    "loan": "consumer_finance",
    "credit_card": "consumer_finance",
    "subscription": "subscription",
    "rental_contract": "rental",
    "lease_agreement": "rental",
    "sale_deed": "property",
    "patta": "property",
    "insurance_policy": "insurance",
    "unknown": "consumer_finance",  # default fallback
}
