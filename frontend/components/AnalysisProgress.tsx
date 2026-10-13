"use client";
import { m } from "framer-motion";
import { easeSmooth } from "@/components/ui/motion";
import { Check, RotateCcw } from "lucide-react";
import { useState } from "react";
import { reprocessDocument } from "@/lib/api";

/** One entry per real backend status, in the order `pipeline.py` writes them.
 *
 * These used to be four invented labels with a caption that cycled on a 2.2s timer,
 * independent of the backend — so a slow document read as a healthy one. Every line
 * below now corresponds to a status the pipeline actually sets. */
const STAGES = [
  { status: "uploaded",            label: "Document received",    sub: "Safely stored and queued" },
  { status: "ocr_processing",      label: "Reading the pages",    sub: "Extracting every word of the agreement" },
  { status: "ocr_done",            label: "Understanding it",     sub: "Identifying the document type and its clauses" },
  { status: "analysis_processing", label: "Reviewing the clauses", sub: "Checking for fees, penalties, and traps" },
  { status: "analysis_done",       label: "Compiling your report", sub: "Scoring the findings and writing them up" },
];

function stageIndex(status: string): number {
  const i = STAGES.findIndex((s) => s.status === status);
  // Unknown status is still in flight, hold at first step
  return i === -1 ? 0 : i;
}

export function AnalysisProgress({
  docId,
  status,
  onRetried,
}: {
  docId: number;
  status: string;
  /** Polling stops on `failed`, so the page has to be told to start watching again. */
  onRetried: () => void;
}) {
  const [retrying, setRetrying] = useState(false);
  const [retryError, setRetryError] = useState("");

  if (status === "failed") {
    async function retry() {
      setRetryError("");
      setRetrying(true);
      try {
        await reprocessDocument(docId);
        onRetried();
      } catch (e) {
        setRetryError((e as Error).message);
        setRetrying(false);
      }
    }

    return (
      <div>
        <p className="text-[0.9375rem] font-medium text-risk-high">
          We couldn&apos;t finish analyzing this document.
        </p>
        <p className="mt-1.5 text-[0.875rem] leading-relaxed text-ink-2">
          This is usually temporary. Trying again re-runs the full analysis — you don&apos;t
          need to upload the file a second time.
        </p>
        <button
          onClick={retry}
          disabled={retrying}
          className="mt-5 inline-flex h-10 items-center gap-2 rounded-[10px] bg-brand px-[18px] text-[0.9375rem] font-medium text-white shadow-xs transition-all duration-200 ease-smooth hover:bg-brand-accent disabled:pointer-events-none disabled:opacity-40 focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-brand/25"
        >
          <RotateCcw className="h-4 w-4" strokeWidth={1.75} aria-hidden />
          {retrying ? "Starting over…" : "Try again"}
        </button>
        {retryError && (
          <p role="alert" className="mt-3 text-[0.875rem] text-risk-high">
            {retryError}
          </p>
        )}
      </div>
    );
  }

  const done = status === "report_ready";
  const current = done ? STAGES.length : stageIndex(status);
  const pct = Math.round((current / STAGES.length) * 100);

  return (
    <div>
      <div
        className="mb-6 h-1 overflow-hidden rounded-full bg-canvas"
        role="progressbar"
        aria-valuenow={pct}
        aria-valuemin={0}
        aria-valuemax={100}
        aria-label="Analysis progress"
      >
        <m.div
          className="h-full rounded-full bg-brand"
          initial={false}
          animate={{ width: `${pct}%` }}
          transition={{ duration: 0.5, ease: easeSmooth }}
        />
      </div>

      <ol className="space-y-5">
        {STAGES.map((s, i) => {
          const isDone = i < current;
          const isActive = i === current;
          return (
            <m.li
              key={s.status}
              initial={{ opacity: 0, x: -8 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.07, duration: 0.45, ease: easeSmooth }}
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
    </div>
  );
}
