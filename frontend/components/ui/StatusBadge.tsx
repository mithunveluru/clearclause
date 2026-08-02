import { RISK } from "@/lib/ui";

const META: Record<string, { label: string; color: string; tint: string }> = {
  // Spread first, RISK carries its own label
  report_ready: { ...RISK.low, label: "Reviewed" },
  failed:       { ...RISK.high, label: "Failed" },
  _default:     { ...RISK.medium, label: "Analyzing" },
};

export function StatusBadge({ status }: { status: string }) {
  const m = META[status] ?? META._default;
  return (
    <span
      className="inline-flex items-center gap-1.5 rounded-md px-2.5 py-1 text-[0.75rem] font-medium"
      style={{ color: m.color, backgroundColor: m.tint }}
    >
      <span className="h-1.5 w-1.5 rounded-full" style={{ backgroundColor: m.color }} />
      {m.label}
    </span>
  );
}
