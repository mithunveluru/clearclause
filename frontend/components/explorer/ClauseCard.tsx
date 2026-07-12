"use client";
import { m } from "framer-motion";
import { BookOpen, FileText, Lightbulb, MessageSquare } from "lucide-react";
import { issueLabel, severityMeta } from "@/lib/ui";
import type { ExplorerClause } from "@/lib/api";

export type ReadingMode = "consumer" | "professional" | "negotiation" | "financial";

const NEGOTIATION_TIPS: Record<string, string> = {
  processing_fee: "Often negotiable — ask for a 0.5–1% reduction or waiver for existing customers.",
  late_fee: "Request a longer grace period (7 days instead of 3) and a lower penalty cap.",
  prepayment_penalty: "RBI guidelines limit prepayment penalties on floating-rate loans — check if this applies.",
  foreclosure_charge: "Ask for a waiver after the first year, or a sliding-scale charge that reduces over time.",
  auto_renew_trap: "Insist on a written cancellation confirmation and a 30-day reminder before auto-renewal.",
  hard_cancellation: "Ask for a termination window with a fixed exit fee instead of an indefinite lock-in.",
  bundled_addon: "Request an itemized price without the add-on — you may not legally need to accept it.",
  implied_consent: "Ask for an explicit opt-in checkbox for every material term, not an opt-out default.",
  vague_pricing_revision: "Negotiate a cap (e.g. max 5% per year) and a 30-day advance-notice requirement.",
  hidden_fee: "Request a signed 'no hidden charges' declaration before you proceed.",
  missing_cost_disclosure: "Demand a written total-cost disclosure (APR and total repayable) before agreeing.",
  service_fee: "Ask whether this fee is waived for online processing or for customers above a certain value.",
};

export function ClauseCard({
  clause,
  mode,
  index,
}: {
  clause: ExplorerClause;
  mode: ReadingMode;
  index: number;
}) {
  const sev = severityMeta(clause.risk_level);
  const label = issueLabel(clause.issue_type);
  const tip = NEGOTIATION_TIPS[clause.issue_type];

  return (
    <m.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35, delay: Math.min(index * 0.06, 0.3), ease: [0.22, 1, 0.36, 1] }}
      className="rounded-2xl border border-line bg-surface p-6 shadow-xs"
    >
      <div className="mb-4 flex flex-wrap items-center gap-2.5">
        <span
          className="h-2.5 w-2.5 rounded-full shrink-0"
          style={{ backgroundColor: sev.color }}
        />
        <span className="font-semibold tracking-tight text-[1rem]">{label}</span>
        <span
          className="rounded-md px-2 py-0.5 text-[0.6875rem] font-semibold uppercase tracking-[0.08em]"
          style={{ color: sev.color, backgroundColor: sev.tint }}
        >
          {sev.label}
        </span>
        <span className="ml-auto flex items-center gap-1.5">
          <span className="t-caption">{Math.round(clause.confidence * 100)}%</span>
          <span className="w-14 h-1.5 rounded-full bg-canvas overflow-hidden" title={`${Math.round(clause.confidence * 100)}% confidence`}>
            <span
              className="block h-full rounded-full"
              style={{
                width: `${Math.round(clause.confidence * 100)}%`,
                backgroundColor: clause.confidence >= 0.8 ? "#15803d" : clause.confidence >= 0.6 ? "#b45309" : "#b91c1c",
              }}
            />
          </span>
        </span>
      </div>

      {mode === "professional" && clause.original_text && (
        <div className="mb-4 rounded-xl border-l-2 border-brand/30 bg-brand/[0.03] px-4 py-3">
          <p className="mb-1 text-[0.6875rem] font-medium uppercase tracking-wider text-ink-3">
            <FileText className="mr-1 inline h-3 w-3" />
            Original clause{clause.page_number != null ? ` · page ${clause.page_number}` : ""}
          </p>
          <p className="text-[0.875rem] italic leading-relaxed text-ink-2">{clause.original_text}</p>
        </div>
      )}

      {(mode === "consumer" || mode === "professional" || mode === "financial") && (
        <div className="mb-3">
          <p className="mb-1 flex items-center gap-1 text-[0.6875rem] font-medium uppercase tracking-wider text-ink-3">
            <BookOpen className="h-3 w-3" />
            {mode === "professional" ? "Plain English" : "What this means"}
          </p>
          <p className="text-[0.9375rem] leading-relaxed text-ink">{clause.plain_english}</p>
        </div>
      )}

      {clause.why_it_matters && mode !== "negotiation" && (
        <div className="mb-3">
          <p className="mb-1 text-[0.6875rem] font-medium uppercase tracking-wider text-ink-3">
            Why it matters
          </p>
          <p className="text-[0.9375rem] leading-relaxed text-ink-2">{clause.why_it_matters}</p>
        </div>
      )}

      {mode === "negotiation" ? (
        <>
          <div className="mb-3 rounded-xl border border-line bg-canvas px-4 py-3">
            <p className="mb-1 flex items-center gap-1 text-[0.6875rem] font-medium uppercase tracking-wider text-ink-3">
              <MessageSquare className="h-3 w-3" />
              What to ask
            </p>
            <p className="text-[0.9375rem] leading-relaxed">{clause.action_text}</p>
          </div>
          {tip && (
            <div
              className="rounded-xl px-4 py-3"
              style={{ backgroundColor: sev.tint, borderLeft: `3px solid ${sev.color}` }}
            >
              <p className="mb-1 flex items-center gap-1 text-[0.6875rem] font-medium uppercase tracking-wider"
                style={{ color: sev.color }}>
                <Lightbulb className="h-3 w-3" />
                Negotiation angle
              </p>
              <p className="text-[0.875rem] leading-relaxed text-ink">{tip}</p>
            </div>
          )}
        </>
      ) : (
        <div className="mt-4 rounded-xl border border-line bg-canvas px-4 py-3">
          <p className="mb-1 text-[0.6875rem] font-medium uppercase tracking-wider text-ink-3">
            Recommended action
          </p>
          <p className="text-[0.9375rem] leading-relaxed">{clause.action_text}</p>
        </div>
      )}

      {clause.page_number != null && mode !== "professional" && (
        <p className="mt-3 flex items-center gap-1.5 text-[0.8125rem] text-ink-3">
          <FileText className="h-3.5 w-3.5" strokeWidth={1.75} aria-hidden />
          Source: page {clause.page_number}
        </p>
      )}
    </m.div>
  );
}
