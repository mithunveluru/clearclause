import { ArrowRight, Check } from "lucide-react";
import { ButtonLink } from "@/components/ui/Button";
import { Container } from "@/components/ui/Surface";
import { PageTransition } from "@/components/ui/PageTransition";
import { TopBar } from "@/components/ui/TopBar";

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
        <Container className="pt-32 pb-28 text-center md:pt-44">
          <p className="eyebrow mb-6">Know before you sign</p>
          <h1 className="t-display mx-auto max-w-4xl text-balance">
            Understand exactly what you’re agreeing to.
          </h1>
          <p className="t-body mx-auto mt-7 max-w-xl text-balance">
            ClearClause reviews loan agreements and subscription terms for hidden fees,
            penalties, and auto-renew traps — and explains every risk in plain English.
          </p>
          <div className="mt-11 flex flex-col items-center justify-center gap-3 sm:flex-row">
            <ButtonLink href="/dashboard" variant="primary" size="lg">
              Analyze a document
              <ArrowRight className="h-[18px] w-[18px]" strokeWidth={2} />
            </ButtonLink>
            <ButtonLink href="/sample" variant="secondary" size="lg">
              View a sample report
            </ButtonLink>
          </div>
        </Container>

        <Container className="pb-32">
          <div className="mx-auto max-w-3xl rounded-3xl border border-line bg-surface px-8 py-12 shadow-soft sm:px-14">
            <p className="eyebrow text-center">Comprehensive review</p>
            <h2 className="t-headline mt-3 text-center text-[1.75rem]">
              Every clause, checked for traps
            </h2>
            <ul className="mx-auto mt-10 grid max-w-xl grid-cols-1 gap-x-10 gap-y-1 sm:grid-cols-2">
              {CHECKS.map((c) => (
                <li key={c} className="flex items-center gap-3 py-2.5 text-[0.9375rem] text-ink">
                  <span className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-risk-low/10">
                    <Check className="h-3 w-3 text-risk-low" strokeWidth={2.5} />
                  </span>
                  {c}
                </li>
              ))}
            </ul>
          </div>
        </Container>

        <Container className="pb-28">
          <div className="mx-auto max-w-3xl">
            <p className="eyebrow text-center">How it works</p>
            <h2 className="t-headline mt-3 text-center text-[1.75rem]">
              From upload to answers in seconds
            </h2>
            <div className="mt-12 grid grid-cols-1 gap-x-12 gap-y-10 sm:grid-cols-3">
              {STEPS.map((s, i) => (
                <div key={s.title}>
                  <div className="text-[2rem] font-semibold tracking-tighter text-ink-3">
                    0{i + 1}
                  </div>
                  <h3 className="mt-3 text-[1.0625rem] font-semibold tracking-tight">{s.title}</h3>
                  <p className="mt-2 text-[0.9375rem] leading-relaxed text-ink-2">{s.body}</p>
                </div>
              ))}
            </div>
          </div>
        </Container>

        <Container className="pb-32">
          <div className="mx-auto max-w-3xl rounded-3xl border border-line bg-ink px-8 py-14 text-white sm:px-14">
            <p className="text-[0.75rem] font-semibold uppercase tracking-[0.16em] text-white/50">
              Built for trust
            </p>
            <h2 className="mt-3 text-[1.75rem] font-semibold leading-tight tracking-tight">
              Designed to protect you, not impress you
            </h2>
            <div className="mt-10 grid grid-cols-1 gap-x-12 gap-y-8 sm:grid-cols-3">
              {TRUST.map((t) => (
                <div key={t.title}>
                  <h3 className="text-[0.9375rem] font-semibold">{t.title}</h3>
                  <p className="mt-2 text-[0.875rem] leading-relaxed text-white/65">{t.body}</p>
                </div>
              ))}
            </div>
          </div>
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
