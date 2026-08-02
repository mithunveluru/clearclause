"use client";
import { m } from "framer-motion";
import { ArrowRight, Check, Lock } from "lucide-react";
import Link from "next/link";
import { ButtonLink } from "@/components/ui/Button";
import { HeroPreview } from "@/components/HeroPreview";
import { WorkflowStory } from "@/components/WorkflowStory";
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
                {/* The sample leads. The primary CTA used to point at /dashboard, which
                    bounces a logged-out visitor to /login — the most prominent action on the
                    page produced a signup form before showing a single thing the product does. */}
                <ButtonLink href="/sample" variant="primary" size="lg">
                  See a real analysis
                  <ArrowRight className="h-[18px] w-[18px]" strokeWidth={2} />
                </ButtonLink>
                <ButtonLink href="/dashboard" variant="secondary" size="lg">
                  Analyze your document
                </ButtonLink>
              </m.div>
              <m.p
                className="mt-6 flex items-center justify-center gap-1.5 text-[0.8125rem] text-ink-3"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.35, duration: 0.55, ease: easeSmooth }}
              >
                <Lock className="h-3.5 w-3.5" strokeWidth={2} aria-hidden />
                Your documents stay private · every finding cites the exact clause
              </m.p>
            </m.div>

            <HeroPreview />
          </Container>
        </div>

        <Container className="pb-32">
          <m.div
            className="mx-auto max-w-4xl"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-80px" }}
            transition={{ duration: 0.6, ease: easeSmooth }}
          >
            <p className="eyebrow text-center">How it works</p>
            <h2 className="t-headline mt-3 text-center text-[1.75rem]">
              From upload to answers in seconds
            </h2>
            <div className="mt-12">
              <WorkflowStory />
            </div>
          </m.div>
        </Container>

        <Container className="pb-32">
          <div className="mx-auto grid max-w-4xl items-start gap-10 lg:grid-cols-[1fr_1.15fr] lg:gap-20">
            <m.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-80px" }}
              transition={{ duration: 0.6, ease: easeSmooth }}
              className="lg:sticky lg:top-28"
            >
              <p className="eyebrow">Comprehensive review</p>
              <h2 className="t-headline mt-3 text-[1.75rem]">
                Every clause, checked for traps
              </h2>
              <p className="t-body mt-4 text-[0.9375rem]">
                The patterns regulators and consumer advocates flag — fees that hide,
                penalties that bite, renewals that never end — checked against every
                clause in your agreement.
              </p>
            </m.div>
            <m.ul
              className="divide-y divide-line border-y border-line"
              variants={staggerContainer}
              initial="initial"
              whileInView="animate"
              viewport={{ once: true }}
            >
              {CHECKS.map((c) => (
                <m.li
                  key={c}
                  variants={staggerItem}
                  className="flex items-center gap-3 py-3.5 text-[0.9375rem] text-ink"
                >
                  <span className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-brand text-white">
                    <Check className="h-2.5 w-2.5" strokeWidth={3} />
                  </span>
                  {c}
                </m.li>
              ))}
            </m.ul>
          </div>
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
          <Container className="py-8">
            <nav
              aria-label="Legal"
              className="flex flex-wrap items-center justify-center gap-x-6 gap-y-2 sm:justify-start"
            >
              {[
                ["Terms", "/legal/terms"],
                ["Privacy", "/legal/privacy"],
                ["AI Disclaimer", "/legal/ai-disclaimer"],
                ["Security", "/legal/security"],
                ["Cookies", "/legal/cookies"],
                ["Contact", "/legal/contact"],
              ].map(([label, href]) => (
                <Link
                  key={href}
                  href={href}
                  className="text-[0.8125rem] font-medium text-ink-2 transition hover:text-ink"
                >
                  {label}
                </Link>
              ))}
            </nav>
            <div className="mt-5 flex flex-col items-center justify-between gap-3 sm:flex-row">
              <span className="t-caption">© {new Date().getFullYear()} ClearClause</span>
              <span className="t-caption">
                Informational analysis only — not legal or financial advice.
              </span>
            </div>
          </Container>
        </footer>
      </PageTransition>
    </>
  );
}
