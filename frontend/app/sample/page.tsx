"use client";
import { AnimatePresence } from "framer-motion";
import { ArrowLeft, CheckCircle, HelpCircle } from "lucide-react";
import Link from "next/link";
import { useState } from "react";
import type { ExplorerDoc } from "@/lib/api";
import { type ReadingMode } from "@/components/explorer/ClauseCard";
import { ExplorerNav } from "@/components/explorer/ExplorerNav";
import { FinancialView } from "@/components/explorer/FinancialView";
import { GuidedWalkthrough } from "@/components/explorer/GuidedWalkthrough";
import { OverviewView } from "@/components/explorer/OverviewView";
import { SectionView } from "@/components/explorer/SectionView";
import { TimelineView } from "@/components/explorer/TimelineView";
import { ButtonLink } from "@/components/ui/Button";
import { PageTransition } from "@/components/ui/PageTransition";
import { TopBar } from "@/components/ui/TopBar";

// Static preview of a real analysis, rendered through the same explorer
// components the product uses — the sample and the product never drift apart.
const SAMPLE: ExplorerDoc = {
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

export default function SamplePage() {
  const [active, setActive] = useState("overview");
  const [mode, setMode] = useState<ReadingMode>("consumer");
  const [walkthrough, setWalkthrough] = useState(false);

  return (
    <>
      <TopBar
        right={
          <Link
            href="/"
            className="inline-flex items-center gap-1.5 text-[0.875rem] font-medium text-ink-2 hover:text-ink"
          >
            <ArrowLeft className="h-4 w-4" strokeWidth={1.75} />
            Home
          </Link>
        }
      />
      <PageTransition>
        <div className="flex min-h-[calc(100vh-64px)]">
          <aside className="hidden w-64 shrink-0 border-r border-line bg-surface lg:block xl:w-72">
            <div className="sticky top-16 max-h-[calc(100vh-64px)] overflow-y-auto px-4">
              <ExplorerNav
                explorer={SAMPLE}
                active={active}
                onSelect={setActive}
                mode={mode}
                onMode={setMode}
                onWalkthrough={() => setWalkthrough(true)}
              />
            </div>
          </aside>

          <main className="min-w-0 flex-1">
            <div className="sticky top-16 z-20 border-b border-line bg-surface/95 backdrop-blur-md">
              <div className="flex items-center justify-between gap-4 px-6 py-3.5">
                <div className="min-w-0">
                  <p className="truncate text-[0.9375rem] font-semibold leading-snug">
                    Personal Loan Agreement.pdf
                  </p>
                  <p className="t-caption">Sample report · static preview of a real analysis</p>
                </div>
                <ButtonLink href="/register" variant="primary" className="shrink-0">
                  Analyze your own
                </ButtonLink>
              </div>

              <nav
                aria-label="Document sections"
                className="lg:hidden flex gap-1.5 overflow-x-auto px-4 pb-2.5 scrollbar-none"
              >
                {[
                  { id: "overview", label: "Overview" },
                  { id: "financial", label: "Financial" },
                  { id: "timeline", label: "Timeline" },
                  { id: "questions", label: "Questions" },
                  ...SAMPLE.sections.map((s) => ({ id: s.id, label: s.label })),
                ].map(({ id, label }) => (
                  <button
                    key={id}
                    onClick={() => setActive(id)}
                    className={`shrink-0 rounded-lg px-3 py-1.5 text-[0.8125rem] font-medium transition whitespace-nowrap ${
                      active === id ? "bg-brand text-white" : "bg-canvas text-ink-2 hover:text-ink"
                    }`}
                  >
                    {label}
                  </button>
                ))}
              </nav>
            </div>

            <div className="mx-auto max-w-3xl px-6 py-10">
              <SamplePane active={active} mode={mode} onSection={setActive} />
            </div>
          </main>
        </div>
      </PageTransition>

      <AnimatePresence>
        {walkthrough && (
          <GuidedWalkthrough
            steps={SAMPLE.walkthrough}
            onClose={() => setWalkthrough(false)}
            onGo={(sid) => {
              setActive(sid);
              setWalkthrough(false);
            }}
          />
        )}
      </AnimatePresence>
    </>
  );
}

function SamplePane({
  active,
  mode,
  onSection,
}: {
  active: string;
  mode: ReadingMode;
  onSection: (id: string) => void;
}) {
  if (active === "financial") return <FinancialView impact={SAMPLE.financial_impact} />;
  if (active === "timeline") return <TimelineView events={SAMPLE.timeline} />;
  if (active === "strengths") {
    return (
      <div>
        <h2 className="mb-4 text-[1.375rem] font-semibold tracking-tight">In your favour</h2>
        <ul className="space-y-3">
          {SAMPLE.strengths.map((s, i) => (
            <li
              key={i}
              className="flex items-start gap-3 rounded-xl border border-[#15803d]/20 bg-[#f0fdf4] px-4 py-3 text-[0.9375rem] leading-relaxed"
            >
              <CheckCircle className="mt-0.5 h-4 w-4 shrink-0 text-[#15803d]" strokeWidth={2} />
              {s}
            </li>
          ))}
        </ul>
      </div>
    );
  }
  if (active === "questions" || active === "qa") {
    // The sample has no live Q&A backend; show the detected questions with a
    // conversion path instead of the product's "embeddings loading" state.
    return (
      <div>
        <h2 className="mb-1 text-[1.375rem] font-semibold tracking-tight">Questions to Ask</h2>
        <p className="t-body mb-6 text-ink-2">
          Detected from this document. In a full analysis you can ask your own — every answer
          cites the page and clause it came from.
        </p>
        <div className="space-y-2">
          {SAMPLE.suggested_questions.map((q, i) => (
            <div
              key={i}
              className="flex items-start gap-3 rounded-xl border border-line bg-surface px-4 py-3.5"
            >
              <HelpCircle className="mt-0.5 h-4 w-4 shrink-0 text-brand" strokeWidth={1.75} />
              <span className="text-[0.9375rem] leading-relaxed">{q.question}</span>
            </div>
          ))}
        </div>
        <div className="mt-8">
          <ButtonLink href="/register" variant="secondary">
            Create an account to ask your own
          </ButtonLink>
        </div>
      </div>
    );
  }

  const section = SAMPLE.sections.find((s) => s.id === active);
  if (section) return <SectionView section={section} mode={mode} />;

  return <OverviewView explorer={SAMPLE} onSection={onSection} />;
}
