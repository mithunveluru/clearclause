"use client";
import { AnimatePresence, m } from "framer-motion";
import { X } from "lucide-react";
import type { Finding } from "@/lib/api";
import { issueLabel, severityMeta } from "@/lib/ui";

export function ClauseInspectionPanel({
  finding,
  onClose,
}: {
  finding: Finding | null;
  onClose: () => void;
}) {
  return (
    <AnimatePresence>
      {finding && (
        <>
          <m.div
            className="fixed inset-0 z-50 bg-brand-deep/10 backdrop-blur-[2px]"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
          />
          <m.aside
            className="fixed right-0 top-0 z-50 flex h-full w-full max-w-md flex-col bg-surface shadow-lift"
            initial={{ x: "100%" }}
            animate={{ x: 0 }}
            exit={{ x: "100%" }}
            transition={{ type: "spring", stiffness: 320, damping: 36 }}
          >
            <div className="flex items-center justify-between border-b border-line px-7 py-5">
              <div className="flex items-center gap-3">
                <span
                  className="h-2.5 w-2.5 rounded-full"
                  style={{ backgroundColor: severityMeta(finding.severity).color }}
                />
                <h2 className="text-lg font-semibold tracking-tight">
                  {issueLabel(finding.issue_type)}
                </h2>
              </div>
              <button
                onClick={onClose}
                className="flex h-9 w-9 items-center justify-center rounded-full text-ink-3 hover:bg-canvas hover:text-ink"
              >
                <X className="h-[18px] w-[18px]" strokeWidth={1.75} />
              </button>
            </div>

            <div className="flex-1 space-y-7 overflow-y-auto px-7 py-7">
              <div className="flex items-center gap-2">
                <span
                  className="text-[0.6875rem] font-semibold uppercase tracking-[0.08em]"
                  style={{ color: severityMeta(finding.severity).color }}
                >
                  {severityMeta(finding.severity).label} severity
                </span>
                <span className="t-caption">· {Math.round(finding.confidence * 100)}% confidence</span>
              </div>

              <Section label="What this means">
                <p className="text-[0.9375rem] leading-relaxed text-ink">{finding.explanation}</p>
              </Section>

              {finding.impact && (
                <Section label="Why it matters">
                  <p className="text-[0.9375rem] leading-relaxed text-ink">{finding.impact}</p>
                </Section>
              )}

              <Section label="Where it appears">
                <blockquote className="rounded-xl border-l-2 border-brand/30 bg-brand/[0.03] px-4 py-3 text-[0.9375rem] italic leading-relaxed text-ink-2">
                  “{finding.clause_text}”
                </blockquote>
              </Section>

              <Section label="What you should do">
                <p className="text-[0.9375rem] leading-relaxed text-ink">{finding.action_text}</p>
              </Section>
            </div>
          </m.aside>
        </>
      )}
    </AnimatePresence>
  );
}

function Section({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div>
      <p className="t-caption mb-2 uppercase">{label}</p>
      {children}
    </div>
  );
}
