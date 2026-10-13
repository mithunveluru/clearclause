"use client";
import { AnimatePresence, m } from "framer-motion";
import { FileText } from "lucide-react";
import { useState } from "react";
import { easeSmooth } from "@/components/ui/motion";
import { SAMPLE } from "@/lib/sample";
import { bandMeta, docTypeLabel, issueLabel, severityMeta } from "@/lib/ui";

/** The homepage product shot, built from the same sample the /sample explorer uses.
 *  Passages between findings are representative filler, not analysed text. */

const CLAUSES = SAMPLE.sections.flatMap((s) => s.clauses);

const PAGE: (string | number)[] = [
  "4.1 The Borrower shall repay the Loan in equated monthly instalments on the due date set out in Schedule I.",
  1, // processing fee
  0, // other charges
  "4.4 All payments shall be made by electronic debit from the account nominated by the Borrower.",
  2, // foreclosure
  3, // discretionary revision
];

export function Showcase() {
  const [sel, setSel] = useState(0);
  const band = bandMeta(SAMPLE.risk_band ?? "Low");
  const active = CLAUSES[sel];

  return (
    <div
      className="overflow-hidden rounded-xl border border-line-strong bg-surface shadow-lift"
    >
      {/* window bar */}
      <div className="flex flex-wrap items-center gap-x-3 gap-y-2 border-b border-line bg-canvas px-4 py-3">
        <FileText className="h-4 w-4 shrink-0 text-ink-3" strokeWidth={1.75} aria-hidden />
        <p className="min-w-0 truncate text-[0.8125rem] font-medium text-ink">Personal Loan Agreement.pdf</p>
        <span className="rounded border border-line-strong px-1.5 py-0.5 text-[0.6875rem] font-medium text-ink-2">
          Sample document
        </span>
        <span className="ml-auto inline-flex items-center gap-1.5 text-[0.75rem] text-ink-2">
          Identified as <span className="font-medium text-ink">{docTypeLabel(SAMPLE.doc_type)}</span>
        </span>
      </div>

      <div className="grid md:grid-cols-[1.25fr_1fr]">
        {/* document page */}
        <div className="border-b border-line bg-[#fdfcfa] px-6 py-6 md:border-b-0 md:border-r sm:px-8">
          <p className="text-[0.6875rem] font-medium uppercase tracking-[0.12em] text-ink-3">
            Section 4 · Repayment and charges
          </p>
          <div className="mt-4 space-y-3 font-serif text-[0.9375rem] leading-[1.65] text-ink-2">
            {PAGE.map((p, i) => {
              if (typeof p === "string") return <p key={i}>{p}</p>;
              const c = CLAUSES[p];
              const meta = severityMeta(c.risk_level);
              const on = p === sel;
              return (
                <p key={i}>
                  <button
                    type="button"
                    onClick={() => setSel(p)}
                    aria-pressed={on}
                    className="rounded-sm text-left transition-colors duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand/40"
                    style={{
                      backgroundColor: on ? meta.tint : "transparent",
                      boxShadow: `inset 0 -2px 0 ${on ? meta.color : meta.color + "55"}`,
                      color: on ? "#20231f" : undefined,
                    }}
                  >
                    {c.original_text}
                  </button>
                </p>
              );
            })}
          </div>
        </div>

        {/* findings */}
        <div className="flex flex-col">
          <div className="flex items-baseline justify-between border-b border-line px-5 py-3.5">
            <p className="text-[0.8125rem] font-semibold text-ink">
              Findings <span className="font-normal tabular-nums text-ink-3">· {CLAUSES.length}</span>
            </p>
            <p className="text-[0.75rem] text-ink-2">
              Score <span className="font-semibold tabular-nums" style={{ color: band.color }}>{SAMPLE.risk_score}</span>
              <span className="text-ink-3">/100 · {band.tone}</span>
            </p>
          </div>
          <ul className="divide-y divide-line">
            {CLAUSES.map((c, i) => {
              const meta = severityMeta(c.risk_level);
              const on = i === sel;
              return (
                <li key={c.clause_id}>
                  <button
                    type="button"
                    onClick={() => setSel(i)}
                    aria-pressed={on}
                    className={`flex w-full items-start gap-3 px-5 py-3 text-left transition-colors duration-150 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-brand/40 ${on ? "bg-sunken/70" : "hover:bg-sunken/40"}`}
                  >
                    <span className="mt-[7px] h-1.5 w-1.5 shrink-0 rounded-full" style={{ backgroundColor: meta.color }} aria-hidden />
                    <span className="min-w-0 flex-1">
                      <span className="block text-[0.8125rem] font-medium text-ink">{issueLabel(c.issue_type)}</span>
                      <span className="text-[0.6875rem] tabular-nums text-ink-3">
                        {meta.label} · page {c.page_number}
                      </span>
                    </span>
                  </button>
                </li>
              );
            })}
          </ul>
          <div className="mt-auto border-t border-line bg-canvas px-5 py-4">
            <AnimatePresence mode="wait">
              <m.div
                key={sel}
                initial={{ opacity: 0, y: 4 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.18, ease: easeSmooth }}
              >
                <p className="text-[0.6875rem] font-medium uppercase tracking-[0.12em] text-ink-3">Why it matters</p>
                <p className="mt-1.5 text-[0.8125rem] leading-relaxed text-ink">{active.why_it_matters}</p>
              </m.div>
            </AnimatePresence>
          </div>
        </div>
      </div>
    </div>
  );
}
