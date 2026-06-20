"use client";
import { AnimatePresence, motion } from "framer-motion";
import { Check, Loader2 } from "lucide-react";
import { useEffect, useState } from "react";

const STAGES = [
  { key: "uploaded", label: "Document received" },
  { key: "ocr", label: "Extracting content" },
  { key: "analysis", label: "Reviewing clauses" },
  { key: "report_ready", label: "Report ready" },
];

// Investigative lines that cycle while analysis runs — makes the work feel real.
const ACTIVITY = [
  "Extracting the document text…",
  "Splitting the agreement into individual clauses…",
  "Identifying fee and processing charges…",
  "Checking cancellation and auto-renewal terms…",
  "Detecting penalty and consent risks…",
  "Estimating the true all-in cost…",
  "Compiling your consumer report…",
];

function stageIndex(status: string): number {
  if (status === "uploaded") return 0;
  if (status.startsWith("ocr")) return 1;
  if (status.startsWith("analysis")) return 2;
  if (status === "report_ready") return 3;
  return 0;
}

export function AnalysisProgress({ status }: { status: string }) {
  const running = status !== "report_ready" && status !== "failed";
  const [tick, setTick] = useState(0);

  useEffect(() => {
    if (!running) return;
    const id = setInterval(() => setTick((t) => t + 1), 2000);
    return () => clearInterval(id);
  }, [running]);

  if (status === "failed") {
    return (
      <p className="text-[0.9375rem] font-medium text-risk-high">
        We couldn’t finish analyzing this document. Please try uploading it again.
      </p>
    );
  }

  const current = stageIndex(status);
  const done = status === "report_ready";

  return (
    <div>
      <ol className="space-y-4">
        {STAGES.map((s, i) => {
          const isDone = i < current || done;
          const isActive = i === current && !done;
          return (
            <li key={s.key} className="flex items-center gap-3.5">
              <span
                className={`flex h-7 w-7 items-center justify-center rounded-full transition-colors ${
                  isDone ? "bg-ink text-white" : "border border-line bg-surface text-ink-3"
                }`}
              >
                {isDone ? (
                  <Check className="h-4 w-4" strokeWidth={2.5} />
                ) : isActive ? (
                  <Loader2 className="h-3.5 w-3.5 animate-spin text-ink" strokeWidth={2.5} />
                ) : (
                  <span className="text-[0.6875rem] font-semibold">{i + 1}</span>
                )}
              </span>
              <span
                className={`text-[0.9375rem] tracking-tight ${
                  i <= current || done ? "text-ink" : "text-ink-3"
                }`}
              >
                {s.label}
              </span>
            </li>
          );
        })}
      </ol>

      {running && (
        <div className="mt-7 border-t border-line pt-5">
          <AnimatePresence mode="wait">
            <motion.p
              key={tick % ACTIVITY.length}
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -6 }}
              transition={{ duration: 0.4, ease: [0.22, 1, 0.36, 1] }}
              className="text-[0.875rem] text-ink-2"
            >
              {ACTIVITY[tick % ACTIVITY.length]}
            </motion.p>
          </AnimatePresence>
        </div>
      )}
    </div>
  );
}
