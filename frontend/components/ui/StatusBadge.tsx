const META: Record<string, { label: string; color: string; tint: string }> = {
  report_ready: { label: "Reviewed",  color: "#16a34a", tint: "#f0fdf4" },
  failed:       { label: "Failed",    color: "#dc2626", tint: "#fef2f2" },
  _default:     { label: "Analyzing", color: "#d97706", tint: "#fff7ed" },
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
