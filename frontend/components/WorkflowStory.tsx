"use client";
import { animate, m, useInView, useReducedMotion } from "framer-motion";
import { ArrowRight, Check, FileUp } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { easeSmooth } from "@/components/ui/motion";

/** Scroll-driven walkthrough of the real pipeline stages. */

const STAGES = ["Reading pages", "Extracting clauses", "Checking risks"];

const FINDINGS = [
  { color: "#b91c1c", label: "Foreclosure penalty" },
  { color: "#b45309", label: "Hidden processing fee" },
];

const panel = {
  initial: { opacity: 0, y: 24 },
  animate: { opacity: 1, y: 0, transition: { duration: 0.6, ease: easeSmooth } },
};

function Panel({
  step,
  title,
  caption,
  children,
}: {
  step: string;
  title: string;
  caption: string;
  children: React.ReactNode;
}) {
  return (
    <m.div variants={panel} className="flex flex-col rounded-2xl border border-line bg-surface p-6 shadow-soft">
      <p className="eyebrow">{step}</p>
      <h3 className="mt-2 text-[1.0625rem] font-semibold tracking-tight">{title}</h3>
      <div className="my-6 flex flex-1 items-center">{children}</div>
      <p className="text-[0.875rem] leading-relaxed text-ink-2">{caption}</p>
    </m.div>
  );
}

/** Counts up on scroll; jumps straight there under reduced motion. */
function CountUpScore({ value, color }: { value: number; color: string }) {
  const ref = useRef<HTMLSpanElement>(null);
  const inView = useInView(ref, { once: true, margin: "-40px" });
  const reduce = useReducedMotion();
  const [n, setN] = useState(0);

  useEffect(() => {
    if (!inView) return;
    if (reduce) {
      setN(value);
      return;
    }
    const controls = animate(0, value, {
      duration: 1.1,
      ease: easeSmooth,
      onUpdate: (v) => setN(Math.round(v)),
    });
    return () => controls.stop();
  }, [inView, reduce, value]);

  return (
    <span ref={ref} className="text-[2.25rem] font-semibold leading-none tracking-tighter tabular-nums" style={{ color }}>
      {n}
    </span>
  );
}

export function WorkflowStory() {
  return (
    <m.div
      className="grid grid-cols-1 items-stretch gap-4 sm:grid-cols-[1fr_auto_1fr_auto_1fr]"
      variants={{ animate: { transition: { staggerChildren: 0.18 } } }}
      initial="initial"
      whileInView="animate"
      viewport={{ once: true, margin: "-80px" }}
    >
      <Panel
        step="Step 01"
        title="Drop your agreement"
        caption="A PDF or a photo. Analysis starts the moment it lands — there is no analyze button."
      >
        <div className="flex w-full flex-col items-center rounded-xl border border-dashed border-line-strong bg-canvas px-4 py-6">
          <m.span
            variants={{
              initial: { opacity: 0, y: -14 },
              animate: { opacity: 1, y: 0, transition: { duration: 0.5, ease: easeSmooth, delay: 0.35 } },
            }}
            className="flex h-11 w-11 items-center justify-center rounded-xl bg-brand/[0.07] text-brand"
          >
            <FileUp className="h-5 w-5" strokeWidth={1.75} />
          </m.span>
          <p className="mt-3 text-[0.8125rem] font-medium text-ink-2">Personal Loan Agreement.pdf</p>
        </div>
      </Panel>

      <Divider />

      <Panel
        step="Step 02"
        title="Every clause is read"
        caption="Pages are read, clauses split apart, and each one checked for fees, penalties, and traps."
      >
        <ul className="w-full space-y-3">
          {STAGES.map((s, i) => (
            <li key={s} className="flex items-center gap-2.5 text-[0.875rem] font-medium text-ink">
              <m.span
                variants={{
                  initial: { scale: 0, opacity: 0 },
                  animate: {
                    scale: 1,
                    opacity: 1,
                    transition: { duration: 0.35, ease: easeSmooth, delay: 0.5 + i * 0.4 },
                  },
                }}
                className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-brand text-white"
              >
                <Check className="h-3 w-3" strokeWidth={3} />
              </m.span>
              {s}
            </li>
          ))}
        </ul>
      </Panel>

      <Divider />

      <Panel
        step="Step 03"
        title="Explore the findings"
        caption="A risk score, plain-English findings, and answers — each traced to the exact clause and page."
      >
        <div className="w-full rounded-xl border border-line bg-canvas px-4 py-4">
          <div className="flex items-baseline gap-1">
            <CountUpScore value={71} color="#b91c1c" />
            <span className="text-[0.8125rem] font-medium text-ink-3">/100 · High risk</span>
          </div>
          <ul className="mt-3 space-y-1.5">
            {FINDINGS.map((f) => (
              <li key={f.label} className="flex items-center gap-2 text-[0.8125rem] text-ink-2">
                <span className="h-1.5 w-1.5 shrink-0 rounded-full" style={{ backgroundColor: f.color }} />
                {f.label}
              </li>
            ))}
          </ul>
        </div>
      </Panel>
    </m.div>
  );
}

function Divider() {
  return (
    <div className="hidden items-center sm:flex" aria-hidden>
      <ArrowRight className="h-4 w-4 text-ink-3" strokeWidth={1.75} />
    </div>
  );
}
