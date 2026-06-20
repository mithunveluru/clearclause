import type { Finding } from "@/lib/api";

export default function ClauseDrawer({
  finding,
  onClose,
}: {
  finding: Finding | null;
  onClose: () => void;
}) {
  if (!finding) return null;
  return (
    <div className="fixed inset-0 z-50 flex justify-end bg-black/30" onClick={onClose}>
      <aside
        className="h-full w-full max-w-md overflow-y-auto bg-white p-6 shadow-xl"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="mb-4 flex items-center justify-between">
          <h3 className="font-semibold capitalize">
            {finding.issue_type.replace(/_/g, " ")}
          </h3>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-700">
            ✕
          </button>
        </div>
        <p className="mb-2 text-sm text-gray-500">Plain English</p>
        <p className="mb-4">{finding.explanation}</p>
        <p className="mb-2 text-sm text-gray-500">Raw clause</p>
        <blockquote className="border-l-4 border-gray-300 bg-gray-50 p-3 text-sm text-gray-700">
          “{finding.clause_text}”
        </blockquote>
        <p className="mb-2 mt-4 text-sm text-gray-500">Suggested action</p>
        <p className="text-sm">{finding.action_text}</p>
      </aside>
    </div>
  );
}
