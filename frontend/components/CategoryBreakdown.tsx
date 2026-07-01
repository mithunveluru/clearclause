"use client";
import { m } from "framer-motion";

const ROWS: { key: string; label: string; max: number }[] = [
  { key: "fee_opacity", label: "Fee opacity", max: 20 },
  { key: "penalty", label: "Penalty severity", max: 15 },
  { key: "renewal", label: "Auto-renew risk", max: 15 },
  { key: "consent", label: "Consent weakness", max: 15 },
  { key: "cancellation", label: "Cancellation friction", max: 10 },
];

export function CategoryBreakdown({ breakdown }: { breakdown: Record<string, number> }) {
  return (
    <div className="space-y-4">
      {ROWS.map(({ key, label, max }) => {
        const value = breakdown[key] ?? 0;
        const pct = Math.round((value / max) * 100);
        return (
          <div key={key}>
            <div className="mb-1.5 flex items-center justify-between">
              <span className="text-[0.8125rem] text-ink-2">{label}</span>
              <span className="text-[0.8125rem] font-medium tabular-nums text-ink">
                {value}
                <span className="text-ink-3">/{max}</span>
              </span>
            </div>
            <div className="h-1 w-full overflow-hidden rounded-full bg-line">
              <m.div
                className="h-full rounded-full bg-brand/70"
                initial={{ width: 0 }}
                animate={{ width: `${pct}%` }}
                transition={{ duration: 0.7, ease: [0.22, 1, 0.36, 1] }}
              />
            </div>
          </div>
        );
      })}
    </div>
  );
}
