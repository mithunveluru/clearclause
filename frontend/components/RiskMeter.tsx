"use client";
import { m } from "framer-motion";
import { bandMeta } from "@/lib/ui";

export function RiskMeter({ total, band }: { total: number; band: string }) {
  const meta = bandMeta(band);
  return (
    <div>
      <div className="flex items-baseline gap-2">
        <span className="text-[3.25rem] font-semibold leading-none tracking-tighter">
          {total}
        </span>
        <span className="text-lg font-medium text-ink-3">/100</span>
        <span
          className="ml-2 inline-flex items-center gap-1.5 rounded-md px-2.5 py-1 text-[0.8125rem] font-semibold"
          style={{ color: meta.color, backgroundColor: meta.tint }}
        >
          <span className="h-1.5 w-1.5 rounded-full" style={{ backgroundColor: meta.color }} />
          {meta.tone}
        </span>
      </div>

      <div className="relative mt-5 h-1.5 w-full overflow-hidden rounded-full bg-line">
        <m.div
          className="absolute inset-y-0 left-0 rounded-full"
          style={{ backgroundColor: meta.color }}
          initial={{ width: 0 }}
          animate={{ width: `${Math.min(100, Math.max(2, total))}%` }}
          transition={{ duration: 0.9, ease: [0.22, 1, 0.36, 1] }}
        />
      </div>
      <div className="mt-2 flex justify-between text-[0.6875rem] font-medium text-ink-3">
        <span>0</span>
        <span>25</span>
        <span>50</span>
        <span>75</span>
        <span>100</span>
      </div>
    </div>
  );
}
