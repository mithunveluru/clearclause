"use client";
import { m } from "framer-motion";
import { FileText, TrendingUp } from "lucide-react";
import { BAND, SEVERITY } from "@/lib/ui";

/** Landing hero preview. No external assets, so it stays CSP-safe. */

const FINDINGS: { sev: keyof typeof SEVERITY; label: string; detail: string }[] = [
  { sev: "high", label: "Foreclosure penalty", detail: "4% charge if you repay the loan early" },
  { sev: "medium", label: "Hidden processing fee", detail: "₹4,720 not shown in the headline rate" },
  { sev: "medium", label: "Bundled insurance", detail: "Credit-life premium added to principal" },
];

const band = BAND.High;

const reveal = {
  initial: { opacity: 0, y: 22, scale: 0.98 },
  animate: {
    opacity: 1,
    y: 0,
    scale: 1,
    transition: { duration: 0.7, ease: [0.22, 1, 0.36, 1], delay: 0.35 },
  },
};

export function HeroPreview() {
  return (
    <div className="relative mx-auto mt-20 w-full max-w-2xl [perspective:1400px]">
      {/* soft ground shadow for depth */}
      <div className="pointer-events-none absolute inset-x-10 bottom-2 h-16 rounded-[50%] bg-brand-deep/10 blur-2xl" />

      <m.div {...reveal} className="relative">
        {/* main report card */}
        <div className="relative overflow-hidden rounded-3xl border border-line-strong bg-surface shadow-lift">
          {/* window chrome */}
          <div className="flex items-center gap-3 border-b border-line px-5 py-3.5">
            <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-brand/[0.07] text-brand">
              <FileText className="h-4 w-4" strokeWidth={1.75} />
            </span>
            <div className="min-w-0">
              <p className="truncate text-[0.8125rem] font-medium text-ink">Personal Loan Agreement.pdf</p>
              <p className="text-[0.6875rem] text-ink-3">Analyzed just now</p>
            </div>
            <span
              className="ml-auto inline-flex items-center gap-1.5 rounded-md px-2.5 py-1 text-[0.6875rem] font-semibold"
              style={{ color: band.color, backgroundColor: band.tint }}
            >
              <span className="h-1.5 w-1.5 rounded-full" style={{ backgroundColor: band.color }} />
              {band.tone}
            </span>
          </div>

          <div className="grid gap-6 p-6 sm:grid-cols-[auto,1fr] sm:gap-8">
            {/* score */}
            <div className="sm:border-r sm:border-line sm:pr-8">
              <p className="eyebrow mb-2">Risk score</p>
              <div className="flex items-baseline gap-1">
                <span className="text-[3rem] font-semibold leading-none tracking-tighter" style={{ color: band.color }}>
                  71
                </span>
                <span className="text-base font-medium text-ink-3">/100</span>
              </div>
              <div className="mt-4 h-1.5 w-full overflow-hidden rounded-full bg-line sm:w-36">
                <m.div
                  className="h-full rounded-full"
                  style={{ backgroundColor: band.color }}
                  initial={{ width: 0 }}
                  animate={{ width: "71%" }}
                  transition={{ duration: 0.9, ease: [0.22, 1, 0.36, 1], delay: 0.9 }}
                />
              </div>
            </div>

            {/* findings */}
            <ul className="space-y-3.5">
              {FINDINGS.map((f) => {
                const meta = SEVERITY[f.sev];
                return (
                  <li key={f.label} className="flex gap-3">
                    <span
                      className="mt-1.5 h-2 w-2 shrink-0 rounded-full"
                      style={{ backgroundColor: meta.color }}
                    />
                    <div className="min-w-0">
                      <p className="text-[0.875rem] font-medium text-ink">{f.label}</p>
                      <p className="text-[0.8125rem] leading-snug text-ink-2">{f.detail}</p>
                    </div>
                  </li>
                );
              })}
            </ul>
          </div>
        </div>

        {/* floating hidden-cost accent — the product's core insight, given depth */}
        <m.div
          initial={{ opacity: 0, y: 14, scale: 0.9 }}
          animate={{ opacity: 1, y: 0, scale: 1, transition: { duration: 0.6, ease: [0.22, 1, 0.36, 1], delay: 0.95 } }}
          className="absolute -right-3 -top-6 flex items-center gap-2.5 rounded-2xl border border-line bg-surface/95 px-4 py-3 shadow-raised backdrop-blur-sm sm:-right-8"
        >
          <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-risk-high/[0.08] text-risk-high">
            <TrendingUp className="h-4 w-4" strokeWidth={2} />
          </span>
          <div>
            <p className="text-[0.6875rem] font-medium text-ink-3">True cost vs headline</p>
            <p className="text-[0.9375rem] font-semibold tracking-tight text-ink">+₹41,200</p>
          </div>
        </m.div>
      </m.div>
    </div>
  );
}
