const COLORS: Record<string, string> = {
  Low: "bg-green-600",
  Moderate: "bg-amber-600",
  High: "bg-red-600",
  Critical: "bg-red-900",
};

export default function RiskBadge({ total, band }: { total: number; band: string }) {
  return (
    <span
      className={`inline-block rounded-full px-4 py-1.5 font-bold text-white ${
        COLORS[band] ?? "bg-gray-500"
      }`}
    >
      {total}/100 · {band}
    </span>
  );
}
