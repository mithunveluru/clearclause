const STAGES = [
  { key: "uploaded", label: "Uploaded" },
  { key: "ocr", label: "Reading text" },
  { key: "analysis", label: "Analyzing" },
  { key: "report_ready", label: "Report ready" },
];

function stageIndex(status: string): number {
  if (status === "failed") return -1;
  if (status === "uploaded") return 0;
  if (status.startsWith("ocr")) return 1;
  if (status.startsWith("analysis")) return 2;
  if (status === "report_ready") return 3;
  return 0;
}

export default function Stepper({ status }: { status: string }) {
  if (status === "failed")
    return <p className="font-semibold text-red-600">Processing failed.</p>;
  const current = stageIndex(status);
  return (
    <ol className="flex flex-wrap gap-3 text-sm">
      {STAGES.map((s, i) => (
        <li
          key={s.key}
          className={`flex items-center gap-2 ${
            i <= current ? "text-gray-900" : "text-gray-400"
          }`}
        >
          <span
            className={`flex h-6 w-6 items-center justify-center rounded-full text-xs text-white ${
              i < current ? "bg-green-600" : i === current ? "bg-blue-600" : "bg-gray-300"
            }`}
          >
            {i < current ? "✓" : i + 1}
          </span>
          {s.label}
        </li>
      ))}
    </ol>
  );
}
