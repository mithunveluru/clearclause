import { Check } from "lucide-react";

export function AnalyzerInsights({
  strengths,
  checklist,
}: {
  strengths: string[];
  checklist: string[];
}) {
  if (strengths.length === 0 && checklist.length === 0) return null;
  return (
    <div className="space-y-8">
      {strengths.length > 0 && (
        <div>
          <h3 className="t-section mb-4">Strengths</h3>
          <ul className="space-y-2.5">
            {strengths.map((s, i) => (
              <li key={i} className="flex items-start gap-2.5 text-[0.9375rem] text-ink-2">
                <span className="mt-0.5 flex h-4 w-4 shrink-0 items-center justify-center rounded-full bg-risk-low/10">
                  <Check className="h-2.5 w-2.5 text-risk-low" strokeWidth={3} />
                </span>
                {s}
              </li>
            ))}
          </ul>
        </div>
      )}
      {checklist.length > 0 && (
        <div>
          <h3 className="t-section mb-4">Negotiation checklist</h3>
          <ol className="space-y-2.5">
            {checklist.map((c, i) => (
              <li key={i} className="flex items-start gap-2.5 text-[0.9375rem] text-ink-2">
                <span className="text-[0.8125rem] font-semibold tabular-nums text-ink-3">
                  {i + 1}.
                </span>
                {c}
              </li>
            ))}
          </ol>
        </div>
      )}
    </div>
  );
}
