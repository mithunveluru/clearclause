const ROWS: [string, string][] = [
  ["headline_rate", "Headline rate"],
  ["processing_fee", "Processing fee"],
  ["late_fee", "Late fee"],
  ["renewal_fee", "Renewal fee"],
  ["foreclosure_charge", "Foreclosure charge"],
];

export function CostBreakdown({ cost }: { cost: Record<string, number | null> }) {
  const fmt = (v: number | null) => (v != null ? v.toLocaleString() : "—");
  return (
    <div>
      <dl className="divide-y divide-line">
        {ROWS.map(([key, label]) => (
          <div key={key} className="flex items-center justify-between py-3">
            <dt className="text-[0.9375rem] text-ink-2">{label}</dt>
            <dd className="text-[0.9375rem] font-medium tabular-nums text-ink">{fmt(cost[key])}</dd>
          </div>
        ))}
      </dl>
      <div className="mt-4 flex items-baseline justify-between rounded-xl bg-canvas px-4 py-4">
        <span className="text-[0.9375rem] font-medium">Estimated true cost</span>
        <span className="text-xl font-semibold tabular-nums tracking-tight">
          {fmt(cost.estimated_true_cost)}
        </span>
      </div>
      <p className="t-caption mt-3 leading-relaxed">
        Estimated from amounts stated in the document. Percentages are shown as-is and not
        added to the total.
      </p>
    </div>
  );
}
