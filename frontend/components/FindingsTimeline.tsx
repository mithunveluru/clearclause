"use client";
import { motion } from "framer-motion";
import { ArrowUpRight } from "lucide-react";
import type { Finding } from "@/lib/api";
import { issueLabel, severityMeta } from "@/lib/ui";

export function FindingsTimeline({
  findings,
  onInspect,
}: {
  findings: Finding[];
  onInspect: (f: Finding) => void;
}) {
  if (findings.length === 0) {
    return (
      <p className="t-body py-10 text-center">No risky clauses were found in this document.</p>
    );
  }
  return (
    <ol className="relative">
      <span className="absolute left-[7px] top-2 bottom-2 w-px bg-line" aria-hidden />
      {findings.map((f, i) => {
        const m = severityMeta(f.severity);
        return (
          <motion.li
            key={f.id}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay: Math.min(i * 0.05, 0.4), ease: [0.22, 1, 0.36, 1] }}
            className="relative pl-9 pb-10 last:pb-0"
          >
            <span
              className="absolute left-0 top-1.5 h-3.5 w-3.5 rounded-full ring-4 ring-surface"
              style={{ backgroundColor: m.color }}
              aria-hidden
            />
            <div className="flex flex-wrap items-baseline gap-x-3 gap-y-0.5">
              <h3 className="text-[1.0625rem] font-semibold tracking-tight">
                {issueLabel(f.issue_type)}
              </h3>
              <span
                className="text-[0.6875rem] font-semibold uppercase tracking-[0.08em]"
                style={{ color: m.color }}
              >
                {m.label} severity
              </span>
              <span className="t-caption">· {Math.round(f.confidence * 100)}% confidence</span>
            </div>

            <p className="mt-2.5 max-w-2xl text-[0.9375rem] leading-relaxed text-ink-2">
              {f.explanation}
            </p>

            {f.impact && (
              <p className="mt-2 max-w-2xl text-[0.9375rem] leading-relaxed text-ink-2">
                <span className="font-medium text-ink">Why it matters. </span>
                {f.impact}
              </p>
            )}

            <div className="mt-4 rounded-xl border border-line bg-canvas px-4 py-3">
              <p className="eyebrow mb-1 text-[0.6875rem]">Recommended action</p>
              <p className="text-[0.9375rem] leading-relaxed text-ink">{f.action_text}</p>
            </div>

            {f.clause_text && (
              <button
                onClick={() => onInspect(f)}
                className="mt-3.5 inline-flex items-center gap-1 text-[0.875rem] font-medium text-accent transition-colors hover:text-ink"
              >
                See where this appears
                <ArrowUpRight className="h-3.5 w-3.5" strokeWidth={2} />
              </button>
            )}
          </motion.li>
        );
      })}
    </ol>
  );
}
