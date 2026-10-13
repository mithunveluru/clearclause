"use client";
import { m } from "framer-motion";
import { viewTransition } from "@/components/ui/motion";
import { AlertTriangle, CheckCircle, DollarSign, TrendingUp } from "lucide-react";
import type { ExplorerDoc } from "@/lib/api";
import { bandMeta, docTypeLabel, severityMeta } from "@/lib/ui";

export function OverviewView({
  explorer,
  onSection,
}: {
  explorer: ExplorerDoc;
  onSection: (id: string) => void;
}) {
  const bm = explorer.risk_band ? bandMeta(explorer.risk_band) : null;
  const highestSections = [...explorer.sections].sort(
    (a, b) =>
      (b.clauses.filter((c) => c.risk_level === "high" || c.risk_level === "critical").length) -
      (a.clauses.filter((c) => c.risk_level === "high" || c.risk_level === "critical").length)
  );

  return (
    <m.div {...viewTransition} className="space-y-6">
      {bm && (
        <div
          className="flex items-center gap-4 rounded-xl p-6"
          style={{ backgroundColor: bm.tint, border: `1px solid ${bm.color}30` }}
        >
          <div>
            <p className="text-[0.6875rem] font-semibold uppercase tracking-[0.09em]" style={{ color: bm.color }}>
              {explorer.risk_band} Risk · {docTypeLabel(explorer.doc_type)}
            </p>
            {explorer.risk_score != null && (
              <p className="mt-0.5 text-[2.25rem] font-bold leading-none tracking-tighter" style={{ color: bm.color }}>
                {explorer.risk_score}
                {/* No opacity: it washed the risk colour out to 2.4:1 against its own tint. */}
                <span className="ml-1 text-[1rem] font-normal text-ink-2">/100</span>
              </p>
            )}
            {explorer.analysis_summary && (
              <p className="mt-2 max-w-lg text-[0.9375rem] leading-relaxed text-ink">
                {explorer.analysis_summary}
              </p>
            )}
          </div>
        </div>
      )}

      {explorer.entity_highlights.length > 0 && (
        <div>
          <p className="mb-3 flex items-center gap-1.5 t-caption">
            <DollarSign className="h-3.5 w-3.5" />
            Key figures
          </p>
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
            {explorer.entity_highlights.map((h, i) => (
              <m.div
                key={i}
                initial={{ opacity: 0, scale: 0.97 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: i * 0.05, duration: 0.25 }}
                className="rounded-xl border border-line bg-surface px-4 py-3"
              >
                <p className="t-caption">{h.label}</p>
                <p className="mt-0.5 text-[1.125rem] font-bold tracking-tight">{h.value}</p>
              </m.div>
            ))}
          </div>
        </div>
      )}

      {highestSections.length > 0 && (
        <div>
          <p className="mb-3 flex items-center gap-1.5 t-caption">
            <AlertTriangle className="h-3.5 w-3.5 text-risk-high" />
            Attention required
          </p>
          <div className="space-y-2">
            {highestSections.slice(0, 3).map((s) => {
              const worst = s.clauses.reduce(
                (acc, c) =>
                  (["critical", "high", "medium", "low"].indexOf(c.risk_level) <
                   ["critical", "high", "medium", "low"].indexOf(acc))
                    ? c.risk_level
                    : acc,
                "low"
              );
              const sev = severityMeta(worst);
              return (
                <button
                  key={s.id}
                  onClick={() => onSection(s.id)}
                  className="flex w-full items-center justify-between gap-3 rounded-xl border border-line bg-surface px-4 py-3.5 text-left transition hover:border-brand/30 hover:bg-brand/[0.02]"
                >
                  <div>
                    <p className="font-semibold text-[0.9375rem]">{s.label}</p>
                    <p className="t-caption mt-0.5 line-clamp-1">{s.clauses[0]?.plain_english}</p>
                  </div>
                  <span
                    className="shrink-0 rounded-md px-2.5 py-1 text-[0.6875rem] font-semibold uppercase tracking-wide"
                    style={{ backgroundColor: sev.tint, color: sev.color }}
                  >
                    {s.item_count} {s.item_count === 1 ? "issue" : "issues"}
                  </span>
                </button>
              );
            })}
          </div>
        </div>
      )}

      {explorer.strengths.length > 0 && (
        <div>
          <p className="mb-3 flex items-center gap-1.5 t-caption">
            <CheckCircle className="h-3.5 w-3.5 text-risk-low" />
            What&apos;s in your favour
          </p>
          <ul className="space-y-2">
            {explorer.strengths.map((s, i) => (
              <li key={i} className="flex items-start gap-2.5 text-[0.9375rem] leading-relaxed">
                <CheckCircle className="mt-0.5 h-4 w-4 shrink-0 text-risk-low" strokeWidth={2} />
                {s}
              </li>
            ))}
          </ul>
        </div>
      )}

      {explorer.recommendations.length > 0 && (
        <div>
          <p className="mb-3 flex items-center gap-1.5 t-caption">
            <TrendingUp className="h-3.5 w-3.5" />
            Recommended actions
          </p>
          <ul className="space-y-2">
            {explorer.recommendations.map((r, i) => (
              <li key={i} className="flex items-start gap-2.5 rounded-xl border border-line bg-surface px-4 py-3 text-[0.9375rem] leading-relaxed">
                <span className="shrink-0 font-bold text-brand">{i + 1}.</span>
                {r}
              </li>
            ))}
          </ul>
        </div>
      )}
    </m.div>
  );
}
