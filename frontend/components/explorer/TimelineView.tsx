"use client";
import { m } from "framer-motion";
import { Calendar, Clock, DollarSign, ShieldCheck, AlertCircle } from "lucide-react";
import type { TimelineEvent } from "@/lib/api";

const EVENT_ICON: Record<string, React.ElementType> = {
  payment: DollarSign,
  period: Clock,
  deadline: Calendar,
  obligation: AlertCircle,
  rights: ShieldCheck,
  recurring: DollarSign,
};

const EVENT_COLOR: Record<string, string> = {
  payment: "#b45309",
  period: "#4f46e5",
  deadline: "#b91c1c",
  obligation: "#6b7280",
  rights: "#15803d",
  recurring: "#b45309",
};

export function TimelineView({ events }: { events: TimelineEvent[] }) {
  if (!events.length) {
    return (
      <div className="py-12 text-center t-body text-ink-3">
        No timeline events detected in this document.
      </div>
    );
  }

  // Sort: payments first, then periods, deadlines, obligations
  const order = ["payment", "recurring", "period", "deadline", "obligation", "rights"];
  const sorted = [...events].sort(
    (a, b) => order.indexOf(a.event_type) - order.indexOf(b.event_type)
  );

  return (
    <m.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.3 }}
    >
      <h2 className="mb-1 text-[1.375rem] font-semibold tracking-tight">Timeline</h2>
      <p className="mb-8 t-body text-ink-2">Key dates, periods, and financial events extracted from the document.</p>

      <ol className="relative space-y-0">
        <span className="absolute left-[17px] top-4 bottom-4 w-px bg-line" aria-hidden />
        {sorted.map((e, i) => {
          const Icon = EVENT_ICON[e.event_type] ?? Calendar;
          const color = EVENT_COLOR[e.event_type] ?? "#6b7280";
          return (
            <m.li
              key={i}
              initial={{ opacity: 0, x: -8 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.05, duration: 0.3, ease: [0.22, 1, 0.36, 1] }}
              className="relative flex gap-5 pb-7 pl-10 last:pb-0"
            >
              <span
                className="absolute left-0 top-1 flex h-[34px] w-[34px] items-center justify-center rounded-full ring-4 ring-surface"
                style={{ backgroundColor: color }}
              >
                <Icon className="h-[15px] w-[15px] text-white" strokeWidth={2} />
              </span>

              <div className="flex-1 rounded-2xl border border-line bg-surface px-5 py-4">
                <div className="flex flex-wrap items-baseline gap-3">
                  <h3 className="font-semibold text-[1rem] tracking-tight">{e.label}</h3>
                  <span
                    className="rounded-md px-2.5 py-0.5 text-[0.75rem] font-bold"
                    style={{ backgroundColor: `${color}18`, color }}
                  >
                    {e.value}
                  </span>
                </div>
                <p className="mt-1.5 text-[0.875rem] leading-relaxed text-ink-2">{e.description}</p>
              </div>
            </m.li>
          );
        })}
      </ol>
    </m.div>
  );
}
