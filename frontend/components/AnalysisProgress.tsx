"use client";
import { AnimatePresence, m } from "framer-motion";
import { Check } from "lucide-react";
import { useEffect, useState } from "react";

const STAGES = [
  { key: "uploaded",      label: "Document received",     sub: "Safely stored and queued" },
  { key: "ocr",          label: "Extracting content",     sub: "Reading every word in the agreement" },
  { key: "analysis",     label: "Reviewing clauses",      sub: "Flagging fees, risks, and traps" },
  { key: "report_ready", label: "Report ready",           sub: "Your findings are compiled" },
];

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
    const id = setInterval(() => setTick((t) => t + 1), 2200);
    return () => clearInterval(id);
  }, [running]);

  if (status === "failed") {
    return (
      <p className="text-[0.9375rem] font-medium text-risk-high">
        We couldn&apos;t finish analyzing this document. Please try uploading it again.
      </p>
    );
  }

  const current = stageIndex(status);
  const done = status === "report_ready";

  return (
    <div>
      <ol className="space-y-5">
        {STAGES.map((s, i) => {
          const isDone = i < current || done;
          const isActive = i === current && !done;
          return (
            <m.li
              key={s.key}
              initial={{ opacity: 0, x: -8 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.07, duration: 0.45, ease: [0.22, 1, 0.36, 1] }}
              className="flex items-start gap-3.5"
            >
              <span
                className={`mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center rounded-full transition-all duration-300 ${
                  isDone
                    ? "bg-brand text-white"
                    : isActive
                    ? "border-2 border-brand bg-brand/[0.08]"
                    : "border border-line bg-surface"
                }`}
              >
                {isDone ? (
                  <Check className="h-3.5 w-3.5" strokeWidth={2.5} />
                ) : isActive ? (
                  <span className="h-2 w-2 animate-pulse rounded-full bg-brand" />
                ) : (
                  <span className="text-[0.625rem] font-semibold text-ink-3">{i + 1}</span>
                )}
              </span>
              <div>
                <p
                  className={`text-[0.9375rem] font-medium tracking-tight transition-colors duration-200 ${
                    isDone ? "text-brand" : isActive ? "text-ink" : "text-ink-3"
                  }`}
                >
                  {s.label}
                </p>
                {(isDone || isActive) && (
                  <p className="mt-0.5 text-[0.8125rem] text-ink-3">{s.sub}</p>
                )}
              </div>
            </m.li>
          );
        })}
      </ol>

      {running && (
        <div className="mt-7 border-t border-line pt-5">
          <AnimatePresence mode="wait">
            <m.p
              key={tick % ACTIVITY.length}
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -6 }}
              transition={{ duration: 0.4, ease: [0.22, 1, 0.36, 1] }}
              className="text-[0.875rem] font-medium text-brand"
            >
              {ACTIVITY[tick % ACTIVITY.length]}
            </m.p>
          </AnimatePresence>
        </div>
      )}
    </div>
  );
}
