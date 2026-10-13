import { AlertCircle, Check, Loader2 } from "lucide-react";
import { RISK } from "@/lib/ui";

// Icon + text carry the meaning; colour only reinforces it
const META: Record<string, { label: string; color: string; tint: string; icon: typeof Check }> = {
  report_ready: { ...RISK.low, label: "Reviewed", icon: Check },
  failed:       { ...RISK.high, label: "Failed", icon: AlertCircle },
  _default:     { color: "#5a6b8a", tint: "#eef1f6", label: "Analyzing", icon: Loader2 },
};

export function StatusBadge({ status }: { status: string }) {
  const m = META[status] ?? META._default;
  const Icon = m.icon;
  return (
    <span
      className="inline-flex shrink-0 items-center gap-1 rounded-md px-2 py-0.5 text-[0.75rem] font-medium"
      style={{ color: m.color, backgroundColor: m.tint }}
    >
      <Icon className={`h-3 w-3 ${Icon === Loader2 ? "animate-spin [animation-duration:1.6s]" : ""}`} strokeWidth={2.25} aria-hidden />
      {m.label}
    </span>
  );
}
