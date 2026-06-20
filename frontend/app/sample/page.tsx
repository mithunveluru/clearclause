"use client";
import { ArrowLeft } from "lucide-react";
import Link from "next/link";
import { useState } from "react";
import type { Finding, Score } from "@/lib/api";
import { CategoryBreakdown } from "@/components/CategoryBreakdown";
import { ClauseInspectionPanel } from "@/components/ClauseInspectionPanel";
import { CostBreakdown } from "@/components/CostBreakdown";
import { FindingsTimeline } from "@/components/FindingsTimeline";
import { RiskMeter } from "@/components/RiskMeter";
import { Container, Surface } from "@/components/ui/Surface";
import { PageTransition } from "@/components/ui/PageTransition";
import { TopBar } from "@/components/ui/TopBar";

const SCORE: Score = {
  total_score: 62,
  band: "High",
  summary:
    "This loan looks high risk because several fees are not clearly disclosed and the agreement allows charges to be revised at the lender’s discretion.",
  breakdown: { fee_opacity: 18, penalty: 15, renewal: 0, consent: 12, cancellation: 0 },
  cost: {
    headline_rate: 14,
    processing_fee: 2,
    late_fee: 500,
    renewal_fee: null,
    foreclosure_charge: 4,
    estimated_true_cost: 500,
  },
};

const FINDINGS: Finding[] = [
  {
    id: 1, clause_id: 1, issue_type: "hidden_fee", severity: "high", confidence: 0.7,
    explanation: "Wording points to charges that are not clearly itemized, which can hide the true cost of the loan.",
    impact: "Unitemized charges can surface later and inflate the total you actually pay.",
    action_text: "Demand an itemized, total list of all charges in writing before agreeing.",
    clause_text: "Other charges may apply as determined by the lender from time to time.",
  },
  {
    id: 2, clause_id: 2, issue_type: "processing_fee", severity: "medium", confidence: 0.9,
    explanation: "A processing fee is charged, often deducted upfront from the disbursed amount so you receive less than the headline loan.",
    impact: "You receive less than the headline loan amount, raising your effective borrowing cost.",
    action_text: "Ask for the exact processing fee amount and confirm whether it is deducted before disbursal.",
    clause_text: "A processing fee of 2% of the sanctioned amount shall be deducted at disbursal.",
  },
  {
    id: 3, clause_id: 3, issue_type: "foreclosure_charge", severity: "high", confidence: 0.85,
    explanation: "Closing the loan before tenure ends attracts a foreclosure charge, reducing the benefit of early repayment.",
    impact: "Exiting the loan early costs a percentage of the outstanding balance.",
    action_text: "Get the exact foreclosure charge and the conditions under which it is waived.",
    clause_text: "Foreclosure of the loan before 12 months will attract a charge of 4% on the outstanding principal.",
  },
  {
    id: 4, clause_id: 4, issue_type: "vague_pricing_revision", severity: "high", confidence: 0.8,
    explanation: "Prices or terms can be changed unilaterally, often without clear notice to the borrower.",
    impact: "Your costs can rise after you sign, with little or no notice.",
    action_text: "Ask for advance-notice guarantees and a cap on how much fees or rates can rise.",
    clause_text: "Charges and interest rates may be revised at the sole discretion of the company.",
  },
];

export default function SamplePage() {
  const [inspect, setInspect] = useState<Finding | null>(null);
  return (
    <>
      <TopBar
        right={
          <Link href="/" className="inline-flex items-center gap-1.5 text-[0.875rem] font-medium text-ink-2 hover:text-ink">
            <ArrowLeft className="h-4 w-4" strokeWidth={1.75} />
            Home
          </Link>
        }
      />
      <PageTransition>
        <Container className="py-12">
          <p className="eyebrow">Sample report</p>
          <h1 className="t-headline mt-2.5">Personal Loan Agreement.pdf</h1>

          <Surface className="mt-8 px-8 py-8">
            <div className="max-w-md">
              <RiskMeter total={SCORE.total_score} band={SCORE.band} />
              <p className="t-body mt-5 text-[1rem]">{SCORE.summary}</p>
            </div>
          </Surface>

          <div className="mt-8 grid grid-cols-1 gap-8 lg:grid-cols-[1fr_320px]">
            <Surface className="px-8 py-8">
              <h2 className="t-section mb-7">Findings · {FINDINGS.length}</h2>
              <FindingsTimeline findings={FINDINGS} onInspect={setInspect} />
            </Surface>
            <div className="space-y-8">
              <Surface className="px-7 py-7">
                <h3 className="t-section mb-6 text-[1.0625rem]">True cost</h3>
                <CostBreakdown cost={SCORE.cost} />
              </Surface>
              <Surface className="px-7 py-7">
                <h3 className="t-section mb-6 text-[1.0625rem]">Risk by category</h3>
                <CategoryBreakdown breakdown={SCORE.breakdown} />
              </Surface>
            </div>
          </div>
        </Container>
      </PageTransition>
      <ClauseInspectionPanel finding={inspect} onClose={() => setInspect(null)} />
    </>
  );
}
