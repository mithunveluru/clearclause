"use client";
import { m } from "framer-motion";
import type { FinancialImpact } from "@/lib/api";

function Table({ title, items }: { title: string; items: { label: string; value: string }[] }) {
  if (!items.length) return null;
  return (
    <div className="mb-6">
      <p className="t-caption mb-3">{title}</p>
      <div className="rounded-xl border border-line overflow-hidden">
        {items.map((item, i) => (
          <div
            key={i}
            className={`flex items-center justify-between px-4 py-3 text-[0.9375rem] ${
              i % 2 === 0 ? "bg-surface" : "bg-canvas"
            }`}
          >
            <span className="text-ink-2">{item.label}</span>
            <span className="font-semibold">{item.value}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

export function FinancialView({ impact }: { impact: FinancialImpact }) {
  const hasData =
    impact.upfront_costs.length > 0 ||
    impact.recurring_costs.length > 0 ||
    impact.penalties.length > 0 ||
    impact.hidden_risks.length > 0;

  return (
    <m.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.3 }}>
      <h2 className="mb-1 text-[1.375rem] font-semibold tracking-tight">Financial Impact</h2>
      <p className="mb-6 t-body text-ink-2">
        All monetary terms extracted from the document, grouped by type.
      </p>

      {!hasData ? (
        <p className="rounded-xl border border-line bg-canvas px-4 py-4 t-body text-ink-3">
          No financial terms were detected in this document.
        </p>
      ) : (
        <>
          <Table title="Upfront costs" items={impact.upfront_costs} />
          <Table title="Recurring costs" items={impact.recurring_costs} />
          <Table title="Penalties" items={impact.penalties} />

          {impact.hidden_risks.length > 0 && (
            <div>
              <p className="t-caption mb-3">Hidden / undisclosed risks</p>
              <ul className="space-y-2">
                {impact.hidden_risks.map((r, i) => (
                  <li
                    key={i}
                    className="flex items-start gap-2.5 rounded-xl border border-[#b91c1c]/20 bg-[#fef2f2] px-4 py-3 text-[0.9375rem] leading-relaxed"
                  >
                    <span className="shrink-0 mt-0.5 text-[#b91c1c]">⚠</span>
                    {r}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {impact.total_note && (
            <p className="mt-6 rounded-xl border border-line bg-canvas px-4 py-3 t-body text-ink-2">
              {impact.total_note}
            </p>
          )}
        </>
      )}
    </m.div>
  );
}
