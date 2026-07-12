"use client";
import { m } from "framer-motion";
import { ArrowRight, Check } from "lucide-react";
import { ButtonLink } from "@/components/ui/Button";
import { HeroPreview } from "@/components/HeroPreview";
import { Container } from "@/components/ui/Surface";
import { PageTransition } from "@/components/ui/PageTransition";
import { TopBar } from "@/components/ui/TopBar";
import { staggerContainer, staggerItem, easeSmooth } from "@/components/ui/motion";

const CHECKS = [
  "Hidden processing & service fees",
  "Late-payment and penalty charges",
  "Prepayment & foreclosure penalties",
  "Auto-renew and recurring-debit traps",
  "Hard-to-cancel wording",
  "Bundled insurance & add-ons",
  "Assumed or implied consent",
  "Missing total-cost disclosure",
];

const STEPS = [
  {
    title: "Upload your document",
    body: "Drop a PDF or photo of any loan or subscription agreement. Nothing else to set up.",
  },
  {
    title: "It analyzes automatically",
    body: "ClearClause reads every clause, flags the risks, and estimates the true cost — no buttons, no waiting on you.",
  },
  {
    title: "Get a clear report",
    body: "See a risk score, the exact risky clauses in plain English, and a professional PDF you can keep or share.",
  },
];

const TRUST = [
  {
    title: "Explainable, not a black box",
    body: "Every finding traces to specific wording in your document — never an opaque, model-only verdict.",
  },
  {
    title: "Private by design",
    body: "Only the extracted text is analyzed. Your files are removed after a short retention window.",
  },
  {
    title: "Grounded in consumer protection",
    body: "Built on the fees, penalties, renewals, and consent patterns regulators and advocates flag.",
  },
];

export default function Home() {
  return (
    <>
      <TopBar
        right={
          <>
            <ButtonLink href="/login" variant="ghost">
              Log in
            </ButtonLink>
            <ButtonLink href="/register" variant="primary">
              Get started
            </ButtonLink>
          </>
        }
      />

      <PageTransition>
        <div className="aurora">
          <Container className="pt-32 pb-28 text-center md:pt-44">
            <m.div
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.65, ease: easeSmooth }}
            >
              <p className="eyebrow mb-6">Know before you sign</p>
              <h1 className="t-display mx-auto max-w-4xl text-balance">
                Understand exactly what you&rsquo;re agreeing to.
              </h1>
              <p className="t-body mx-auto mt-7 max-w-xl text-balance">
                ClearClause reviews loan agreements and subscription terms for hidden fees,
                penalties, and auto-renew traps — and explains every risk in plain English.
              </p>
              <m.div
                className="mt-11 flex flex-col items-center justify-center gap-3 sm:flex-row"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.18, duration: 0.55, ease: easeSmooth }}
              >
                <ButtonLink href="/dashboard" variant="primary" size="lg">
                  Analyze a document
                  <ArrowRight className="h-[18px] w-[18px]" strokeWidth={2} />
                </ButtonLink>
                <ButtonLink href="/sample" variant="secondary" size="lg">
                  View a sample report
                </ButtonLink>
              </m.div>
            </m.div>

            <HeroPreview />
          </Container>
        </div>

        <Container className="pb-32">
          <m.div
            className="mx-auto max-w-3xl rounded-3xl border border-line bg-surface px-8 py-12 shadow-raised sm:px-14"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-80px" }}
            transition={{ duration: 0.6, ease: easeSmooth }}
          >
            <p className="eyebrow text-center">Comprehensive review</p>
            <h2 className="t-headline mt-3 text-center text-[1.75rem]">
              Every clause, checked for traps
            </h2>
            <m.ul
              className="mx-auto mt-10 grid max-w-xl grid-cols-1 gap-x-10 gap-y-1 sm:grid-cols-2"
              variants={staggerContainer}
              initial="initial"
              whileInView="animate"
              viewport={{ once: true }}
            >
              {CHECKS.map((c) => (
                <m.li
                  key={c}
                  variants={staggerItem}
                  className="flex items-center gap-3 py-2.5 text-[0.9375rem] text-ink"
                >
                  <span className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-brand text-white">
                    <Check className="h-2.5 w-2.5" strokeWidth={3} />
                  </span>
                  {c}
                </m.li>
              ))}
            </m.ul>
          </m.div>
        </Container>

        <Container className="pb-28">
          <m.div
            className="mx-auto max-w-3xl"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-80px" }}
            transition={{ duration: 0.6, ease: easeSmooth }}
          >
            <p className="eyebrow text-center">How it works</p>
            <h2 className="t-headline mt-3 text-center text-[1.75rem]">
              From upload to answers in seconds
            </h2>
            <m.div
              className="mt-12 grid grid-cols-1 gap-x-12 gap-y-10 sm:grid-cols-3"
              variants={staggerContainer}
              initial="initial"
              whileInView="animate"
              viewport={{ once: true }}
            >
              {STEPS.map((s, i) => (
                <m.div key={s.title} variants={staggerItem}>
                  <div className="text-[2rem] font-semibold tracking-tighter text-brand/25">
                    0{i + 1}
                  </div>
                  <h3 className="mt-3 text-[1.0625rem] font-semibold tracking-tight">{s.title}</h3>
                  <p className="mt-2 text-[0.9375rem] leading-relaxed text-ink-2">{s.body}</p>
                </m.div>
              ))}
            </m.div>
          </m.div>
        </Container>

        <Container className="pb-32">
          <m.div
            className="mx-auto max-w-3xl rounded-3xl bg-brand-deep px-8 py-14 text-white sm:px-14"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-80px" }}
            transition={{ duration: 0.6, ease: easeSmooth }}
          >
            <p className="text-[0.75rem] font-semibold uppercase tracking-[0.16em] text-white/50">
              Built for trust
            </p>
            <h2 className="mt-3 text-[1.75rem] font-semibold leading-tight tracking-tight">
              Designed to protect you, not impress you
            </h2>
            <m.div
              className="mt-10 grid grid-cols-1 gap-x-12 gap-y-8 sm:grid-cols-3"
              variants={staggerContainer}
              initial="initial"
              whileInView="animate"
              viewport={{ once: true }}
            >
              {TRUST.map((t) => (
                <m.div key={t.title} variants={staggerItem}>
                  <h3 className="text-[0.9375rem] font-semibold">{t.title}</h3>
                  <p className="mt-2 text-[0.875rem] leading-relaxed text-white/65">{t.body}</p>
                </m.div>
              ))}
            </m.div>
          </m.div>
        </Container>

        <footer className="border-t border-line">
          <Container className="flex flex-col items-center justify-between gap-3 py-8 sm:flex-row">
            <span className="t-caption">© {new Date().getFullYear()} ClearClause</span>
            <span className="t-caption">
              Informational analysis only — not legal or financial advice.
            </span>
          </Container>
        </footer>
      </PageTransition>
    </>
  );
}
