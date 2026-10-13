import type { ExplorerDoc } from "@/lib/api";

// Uses the product's own explorer components; no drift
export const SAMPLE: ExplorerDoc = {
  doc_id: 0,
  doc_type: "personal_loan",
  document_family: "loan",
  risk_score: 62,
  risk_band: "High",
  analysis_summary:
    "This loan looks high risk because several fees are not clearly disclosed and the agreement allows charges to be revised at the lender’s discretion.",
  entity_highlights: [
    { label: "Headline rate", value: "14% p.a.", type: "rate" },
    { label: "Processing fee", value: "2% of amount", type: "fee" },
    { label: "Late fee", value: "₹500 / instance", type: "fee" },
  ],
  sections: [
    {
      id: "fees",
      label: "Fees & Charges",
      icon: "DollarSign",
      risk_level: "high",
      item_count: 2,
      summary: "Charges that reduce what you receive or inflate what you repay.",
      clauses: [
        {
          clause_id: 1,
          finding_id: 1,
          issue_type: "hidden_fee",
          risk_level: "high",
          confidence: 0.7,
          original_text: "Other charges may apply as determined by the lender from time to time.",
          plain_english:
            "The agreement points to charges that are not clearly itemized, which can hide the true cost of the loan.",
          why_it_matters:
            "Unitemized charges can surface later and inflate the total you actually pay.",
          action_text: "Demand an itemized, total list of all charges in writing before agreeing.",
          page_number: 2,
        },
        {
          clause_id: 2,
          finding_id: 2,
          issue_type: "processing_fee",
          risk_level: "medium",
          confidence: 0.9,
          original_text:
            "A processing fee of 2% of the sanctioned amount shall be deducted at disbursal.",
          plain_english:
            "A processing fee is deducted upfront from the disbursed amount, so you receive less than the headline loan.",
          why_it_matters:
            "You receive less than the headline loan amount, raising your effective borrowing cost.",
          action_text:
            "Ask for the exact processing fee amount and confirm whether it is deducted before disbursal.",
          page_number: 3,
        },
      ],
    },
    {
      id: "penalties",
      label: "Penalties",
      icon: "AlertTriangle",
      risk_level: "high",
      item_count: 1,
      summary: "Charges triggered by early exit or missed payments.",
      clauses: [
        {
          clause_id: 3,
          finding_id: 3,
          issue_type: "foreclosure_charge",
          risk_level: "high",
          confidence: 0.85,
          original_text:
            "Foreclosure of the loan before 12 months will attract a charge of 4% on the outstanding principal.",
          plain_english:
            "Closing the loan before the tenure ends attracts a foreclosure charge, reducing the benefit of early repayment.",
          why_it_matters: "Exiting the loan early costs a percentage of the outstanding balance.",
          action_text: "Get the exact foreclosure charge and the conditions under which it is waived.",
          page_number: 5,
        },
      ],
    },
    {
      id: "consent",
      label: "Consent & Changes",
      icon: "Eye",
      risk_level: "high",
      item_count: 1,
      summary: "Terms the lender can change without asking you.",
      clauses: [
        {
          clause_id: 4,
          finding_id: 4,
          issue_type: "vague_pricing_revision",
          risk_level: "high",
          confidence: 0.8,
          original_text:
            "Charges and interest rates may be revised at the sole discretion of the company.",
          plain_english:
            "Prices or terms can be changed unilaterally, often without clear notice to the borrower.",
          why_it_matters: "Your costs can rise after you sign, with little or no notice.",
          action_text:
            "Ask for advance-notice guarantees and a cap on how much fees or rates can rise.",
          page_number: 6,
        },
      ],
    },
  ],
  financial_impact: {
    upfront_costs: [{ label: "Processing fee", value: "2% of sanctioned amount" }],
    recurring_costs: [{ label: "Interest", value: "14% p.a. (headline)" }],
    penalties: [
      { label: "Late fee", value: "₹500 per instance" },
      { label: "Foreclosure charge", value: "4% of outstanding principal" },
    ],
    hidden_risks: ["Charges and interest rates may be revised at the lender’s sole discretion."],
    total_note:
      "Estimated from amounts stated in the document. Percentages are shown as-is and depend on the sanctioned amount.",
  },
  timeline: [
    {
      label: "Monthly EMI",
      value: "14% p.a.",
      entity_type: "rate",
      event_type: "recurring",
      description: "Interest accrues at the headline rate over the full tenure.",
    },
    {
      label: "Foreclosure window",
      value: "First 12 months",
      entity_type: "period",
      event_type: "deadline",
      description: "Closing the loan in this period attracts the 4% foreclosure charge.",
    },
  ],
  suggested_questions: [
    {
      question: "What is the complete, itemized list of charges I will pay?",
      category: "cost",
      finding_id: 1,
    },
    {
      question: "Under what conditions is the foreclosure charge waived?",
      category: "penalty",
      finding_id: 3,
    },
    {
      question: "How much notice will I get before fees or rates change?",
      category: "rights",
      finding_id: 4,
    },
  ],
  walkthrough: [
    {
      step: 1,
      title: "Start with the fees",
      description: "Two charges reduce what you receive or inflate what you repay.",
      section_id: "fees",
      insight: "The processing fee is deducted before you receive the money.",
    },
    {
      step: 2,
      title: "Check the exit cost",
      description: "Repaying early is penalized in the first year.",
      section_id: "penalties",
      insight: "A 4% foreclosure charge can erase the savings of early repayment.",
    },
    {
      step: 3,
      title: "Watch the moving parts",
      description: "The lender can revise charges without your consent.",
      section_id: "consent",
      insight: "Ask for a written cap and advance notice before signing.",
    },
  ],
  strengths: [
    "No auto-renewal or recurring-debit clauses were detected.",
    "The late fee is a fixed amount rather than a compounding percentage.",
  ],
  recommendations: [
    "Demand an itemized, written list of all charges before agreeing.",
    "Negotiate a cap and a 30-day notice period for any revision of charges.",
    "Ask for the foreclosure charge to be waived after the first year.",
  ],
};
