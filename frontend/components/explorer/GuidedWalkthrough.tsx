"use client";
import { m } from "framer-motion";
import { ArrowLeft, ArrowRight, Lightbulb, X } from "lucide-react";
import { useEffect, useState } from "react";
import type { WalkthroughStep } from "@/lib/api";

export function GuidedWalkthrough({
  steps,
  onClose,
  onGo,
}: {
  steps: WalkthroughStep[];
  onClose: () => void;
  onGo: (sectionId: string) => void;
}) {
  const [idx, setIdx] = useState(0);
  const step = steps[idx];
  const isLast = idx === steps.length - 1;

  function next() {
    if (isLast) { onClose(); } else { setIdx((i) => i + 1); }
  }

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => { if (e.key === "Escape") onClose(); };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onClose]);

  return (
    <div className="fixed inset-0 z-50 flex items-end justify-center sm:items-center p-4">
      <m.div
        className="absolute inset-0 bg-black/40 backdrop-blur-sm"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        onClick={onClose}
      />

      <m.div
        key={idx}
        initial={{ opacity: 0, y: 24, scale: 0.97 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        exit={{ opacity: 0, y: 16 }}
        transition={{ duration: 0.35, ease: [0.22, 1, 0.36, 1] }}
        className="relative z-10 w-full max-w-md rounded-3xl bg-surface p-8 shadow-2xl"
      >
        <button
          onClick={onClose}
          aria-label="Close walkthrough"
          className="absolute right-5 top-5 rounded-full p-1.5 text-ink-3 hover:bg-canvas"
        >
          <X className="h-4 w-4" />
        </button>

        <div className="mb-6 flex gap-1.5">
          {steps.map((_, i) => (
            <span
              key={i}
              className={`h-1 flex-1 rounded-full transition-colors duration-300 ${i <= idx ? "bg-brand" : "bg-line"}`}
            />
          ))}
        </div>

        <p className="t-caption mb-1">Step {idx + 1} of {steps.length}</p>
        <h3 className="text-[1.25rem] font-semibold tracking-tight mb-2">{step.title}</h3>
        <p className="t-body text-ink-2 mb-4">{step.description}</p>
        <div className="flex items-start gap-2.5 rounded-xl border border-line bg-canvas px-4 py-3 text-[0.875rem] leading-relaxed text-ink">
          <Lightbulb className="mt-0.5 h-4 w-4 shrink-0 text-brand" strokeWidth={1.75} aria-hidden />
          {step.insight}
        </div>

        <div className="mt-6 flex items-center gap-2">
          {idx > 0 && (
            <button
              onClick={() => setIdx((i) => i - 1)}
              className="flex items-center gap-1.5 rounded-xl border border-line px-4 py-2.5 text-[0.875rem] font-medium text-ink-2 hover:bg-canvas"
            >
              <ArrowLeft className="h-3.5 w-3.5" /> Back
            </button>
          )}

          {step.section_id !== "questions" && (
            <button
              onClick={() => { onGo(step.section_id); onClose(); }}
              className="rounded-xl border border-brand/20 bg-brand/5 px-4 py-2.5 text-[0.875rem] font-semibold text-brand hover:bg-brand/10"
            >
              View section
            </button>
          )}

          <button
            onClick={next}
            className="ml-auto flex items-center gap-1.5 rounded-xl bg-brand px-5 py-2.5 text-[0.875rem] font-semibold text-white shadow-xs hover:bg-brand-accent"
          >
            {isLast ? "Done" : "Next"}
            {!isLast && <ArrowRight className="h-3.5 w-3.5" />}
          </button>
        </div>
      </m.div>
    </div>
  );
}
