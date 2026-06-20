import type { Finding } from "@/lib/api";

const SEV_COLOR: Record<string, string> = {
  critical: "text-red-700",
  high: "text-red-600",
  medium: "text-amber-600",
  low: "text-green-600",
};

export default function FindingCard({
  f,
  onOpen,
}: {
  f: Finding;
  onOpen: (f: Finding) => void;
}) {
  return (
    <div className="rounded-xl border bg-white p-4">
      <div className={`text-xs font-bold uppercase tracking-wide ${SEV_COLOR[f.severity] ?? ""}`}>
        {f.severity} · {f.issue_type.replace(/_/g, " ")} · {Math.round(f.confidence * 100)}% confidence
      </div>
      <p className="mt-1.5">{f.explanation}</p>
      <p className="mt-1 text-sm">
        <strong>What to do:</strong> {f.action_text}
      </p>
      {f.clause_text && (
        <button
          onClick={() => onOpen(f)}
          className="mt-2 text-sm text-blue-600 underline"
        >
          View clause
        </button>
      )}
    </div>
  );
}
