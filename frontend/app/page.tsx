"use client";
import { m } from "framer-motion";
import { ArrowRight, ChevronDown } from "lucide-react";
import Link from "next/link";
import { Showcase } from "@/components/Showcase";
import { SiteFooter, SiteHeader } from "@/components/SiteChrome";
import { ButtonLink } from "@/components/ui/Button";
import { Container } from "@/components/ui/Surface";
import { easeSmooth, staggerContainer, staggerItem } from "@/components/ui/motion";

const reveal = {
  initial: { opacity: 0, y: 16 },
  whileInView: { opacity: 1, y: 0 },
  viewport: { once: true, margin: "-80px" },
  transition: { duration: 0.5, ease: easeSmooth },
} as const;

const BENEFITS = [
  {
    n: "01",
    title: "Know what kind of document you have",
    body: "Loan, subscription, credit card, rental, patta or sale agreement — identified from its wording. When the signal is weak, the review says so instead of guessing.",
  },
  {
    n: "02",
    title: "Find the clauses that carry risk",
    body: "Fees, penalties, renewals, discretionary changes, missing buyer protections. Each document type is checked against rules written for that type.",
  },
  {
    n: "03",
    title: "See the wording behind every finding",
    body: "A finding is never a verdict on its own. It shows the exact passage and page it came from, so you can judge it yourself.",
  },
  {
    n: "04",
    title: "Take a structured report onward",
    body: "Download a PDF report of the findings to read later or share with the person advising you.",
  },
];

const STEPS = [
  ["Add a document", "Upload a PDF or a photo of the pages. Analysis starts as soon as it arrives."],
  ["Its type is identified", "The text is read and matched to one of six supported document types."],
  ["Sections are inspected", "Clauses are separated and checked against the rules for that type."],
  ["Review the findings", "Each finding shows severity, evidence and page. Download the report."],
];

const FAMILIES = [
  {
    title: "Consumer finance",
    types: [
      ["Personal & home loans", "Processing fees, foreclosure charges, rate revisions, bundled insurance"],
      ["Subscriptions", "Auto-renewal, cancellation terms, recurring debits"],
      ["Credit cards", "How clearly fees and interest are disclosed"],
    ],
  },
  {
    title: "Property",
    types: [
      ["Rental agreements", "Deposit, lock-in, escalation and exit terms, with a fairness score"],
      ["Sale agreements", "Protections a buyer needs that are missing, with a risk score"],
      ["Patta", "Whether the fields a valid land record should carry are present"],
    ],
  },
];

const FAQ = [
  [
    "Does ClearClause replace a lawyer or financial adviser?",
    "No. It points you to the clauses worth asking about and shows why. The analysis is informational and is not legal or financial advice.",
  ],
  [
    "Where do the findings come from?",
    "From rules written for each document type, applied to the text of your document. Every finding links to the passage that triggered it. Where an optional written summary is shown, it only restates those findings.",
  ],
  [
    "What happens to my file?",
    "Documents are stored encrypted and deleted automatically seven days after upload. You can delete a document, or your whole account, at any time.",
  ],
  [
    "What if my scan is hard to read?",
    "The review tells you when text extraction confidence is low, because a poor scan can hide clauses. A clearer scan or the original PDF gives a more reliable result.",
  ],
  [
    "Which files can I upload?",
    "PDF, PNG or JPG, up to 10 MB per document.",
  ],
];

export default function Home() {
  return (
    <>
      <SiteHeader />
      <main>
        {/* Hero */}
        <section className="paper">
          <Container className="pb-20 pt-16 md:pb-28 md:pt-24">
            <div className="mx-auto max-w-3xl text-center">
              <p className="eyebrow animate-rise">
                Financial &amp; property documents
              </p>
              <h1 className="t-display mt-5 animate-rise text-balance [animation-delay:60ms]">
                Understand the details that matter.
              </h1>
              <p className="t-body mx-auto mt-6 max-w-xl animate-rise text-balance [animation-delay:120ms]">
                ClearClause identifies what kind of document you have, surfaces the clauses that
                carry risk, and shows you the exact wording behind every finding — without
                reading every page yourself.
              </p>
              <div className="mt-9 flex animate-rise flex-col items-center justify-center gap-3 [animation-delay:180ms] sm:flex-row">
                <ButtonLink href="/dashboard" size="lg">
                  Analyze a document
                  <ArrowRight className="h-4 w-4" strokeWidth={2} aria-hidden />
                </ButtonLink>
                <ButtonLink href="/sample" variant="secondary" size="lg">
                  Explore a sample analysis
                </ButtonLink>
              </div>
            </div>
            <div id="product" className="mx-auto mt-16 max-w-5xl scroll-mt-24 animate-rise [animation-delay:280ms]">
              <Showcase />
              <p className="mt-3 text-center text-[0.75rem] text-ink-3">
                Sample agreement and findings for illustration. Select a passage or a finding.
              </p>
            </div>
          </Container>
        </section>

        {/* Benefits */}
        <section className="border-t border-line">
          <Container className="py-20 md:py-28">
            <m.div {...reveal} className="max-w-xl">
              <p className="eyebrow">What you get</p>
              <h2 className="t-display-2 mt-3">A careful second read, with its working shown.</h2>
            </m.div>
            <m.dl
              {...reveal}
              className="mt-14 grid gap-px overflow-hidden rounded-xl border border-line bg-line sm:grid-cols-2"
            >
              {BENEFITS.map((b) => (
                <div key={b.n} className="bg-surface p-7 sm:p-8">
                  <dt>
                    <span className="block font-serif text-[0.9375rem] tabular-nums text-ochre">{b.n}</span>
                    <span className="mt-3 block text-[1.0625rem] font-semibold tracking-tight">{b.title}</span>
                  </dt>
                  <dd className="mt-2 text-[0.9375rem] leading-relaxed text-ink-2">{b.body}</dd>
                </div>
              ))}
            </m.dl>
          </Container>
        </section>

        {/* How it works */}
        <section id="how-it-works" className="scroll-mt-16 border-t border-line bg-sunken/50">
          <Container className="py-20 md:py-28">
            <m.div {...reveal} className="max-w-xl">
              <p className="eyebrow">How it works</p>
              <h2 className="t-display-2 mt-3">Four steps, all of them visible.</h2>
            </m.div>
            <m.ol
              variants={staggerContainer}
              initial="initial"
              whileInView="animate"
              viewport={{ once: true, margin: "-60px" }}
              className="relative mt-14 grid gap-10 md:grid-cols-4 md:gap-8"
            >
              {/* the thin rule the steps hang from */}
              <span aria-hidden className="absolute left-[15px] top-4 bottom-4 w-px bg-line-strong md:left-4 md:right-4 md:top-[15px] md:bottom-auto md:h-px md:w-auto" />
              {STEPS.map(([title, body], i) => (
                <m.li key={title} variants={staggerItem} className="relative flex gap-5 md:block">
                  <span className="relative flex h-8 w-8 shrink-0 items-center justify-center rounded-full border border-line-strong bg-canvas text-[0.8125rem] font-semibold tabular-nums text-brand">
                    {i + 1}
                  </span>
                  <div className="md:mt-6">
                    <h3 className="text-[1rem] font-semibold tracking-tight">{title}</h3>
                    <p className="mt-1.5 text-[0.9375rem] leading-relaxed text-ink-2">{body}</p>
                  </div>
                </m.li>
              ))}
            </m.ol>
          </Container>
        </section>

        {/* Document types */}
        <section id="documents" className="scroll-mt-16 border-t border-line">
          <Container className="py-20 md:py-28">
            <div className="grid gap-12 lg:grid-cols-[1fr_1.6fr] lg:gap-20">
              <m.div {...reveal}>
                <p className="eyebrow">Supported documents</p>
                <h2 className="t-display-2 mt-3">Six document types, each with its own checks.</h2>
                <p className="t-body mt-5 text-[0.9375rem]">
                  Documents outside these types still get a general review for fees, penalties
                  and consent wording, and are labelled as unclassified.
                </p>
              </m.div>
              <div className="grid gap-10 sm:grid-cols-2">
                {FAMILIES.map((f) => (
                  <m.div key={f.title} {...reveal}>
                    <h3 className="border-b border-ink pb-3 text-[0.8125rem] font-semibold uppercase tracking-[0.1em]">
                      {f.title}
                    </h3>
                    <ul className="divide-y divide-line">
                      {f.types.map(([t, d]) => (
                        <li key={t} className="py-4">
                          <p className="text-[0.9375rem] font-medium">{t}</p>
                          <p className="mt-1 text-[0.875rem] leading-relaxed text-ink-2">{d}</p>
                        </li>
                      ))}
                    </ul>
                  </m.div>
                ))}
              </div>
            </div>
          </Container>
        </section>

        {/* Transparency */}
        <section className="bg-brand-deep text-white">
          <Container className="py-20 md:py-24">
            <m.div {...reveal} className="grid gap-12 lg:grid-cols-[1fr_1.6fr] lg:gap-20">
              <div>
                <p className="text-[0.6875rem] font-semibold uppercase tracking-[0.14em] text-ochre">
                  Transparency
                </p>
                <h2 className="t-display-2 mt-3 text-white">What it does, and what it doesn&rsquo;t.</h2>
              </div>
              <div className="grid gap-8 sm:grid-cols-2">
                {[
                  ["Rules first", "Findings come from deterministic checks on your document's text. Nothing is reported that can't be traced to a passage."],
                  ["Honest about limits", "A finding marks something worth asking about, not a legal conclusion. Low-quality scans are flagged as possibly incomplete."],
                  ["Short retention", "Files are deleted seven days after upload, and sooner if you delete them. Account deletion removes everything."],
                  ["Protected in storage", "Served over HTTPS, with documents encrypted at rest. The security page has the details."],
                ].map(([t, b]) => (
                  <div key={t} className="border-t border-white/15 pt-5">
                    <h3 className="text-[0.9375rem] font-semibold">{t}</h3>
                    <p className="mt-2 text-[0.875rem] leading-relaxed text-white/70">{b}</p>
                  </div>
                ))}
                <Link href="/legal/security" className="text-[0.875rem] font-medium text-ochre underline-offset-4 hover:underline sm:col-span-2">
                  Read the security page →
                </Link>
              </div>
            </m.div>
          </Container>
        </section>

        {/* FAQ */}
        <section className="border-b border-line">
          <Container className="grid gap-12 py-20 md:py-28 lg:grid-cols-[1fr_1.6fr] lg:gap-20">
            <m.div {...reveal}>
              <p className="eyebrow">Questions</p>
              <h2 className="t-display-2 mt-3">Before you upload.</h2>
            </m.div>
            <div className="divide-y divide-line border-y border-line">
              {FAQ.map(([q, a]) => (
                <details key={q} className="group">
                  <summary className="flex cursor-pointer list-none items-center justify-between gap-6 py-5 text-[1rem] font-medium marker:hidden focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand/30 [&::-webkit-details-marker]:hidden">
                    {q}
                    <ChevronDown
                      className="h-4 w-4 shrink-0 text-ink-3 transition-transform duration-200 group-open:rotate-180"
                      strokeWidth={1.75}
                      aria-hidden
                    />
                  </summary>
                  <p className="-mt-1 pb-5 pr-10 text-[0.9375rem] leading-relaxed text-ink-2">{a}</p>
                </details>
              ))}
            </div>
          </Container>
        </section>

        {/* Final CTA */}
        <section>
          <Container className="py-20 text-center md:py-28">
            <m.div {...reveal}>
              <h2 className="t-display-2 mx-auto max-w-2xl text-balance">
                Read the fine print before it reads you.
              </h2>
              <div className="mt-9 flex flex-col items-center justify-center gap-3 sm:flex-row">
                <ButtonLink href="/register" size="lg">Create an account</ButtonLink>
                <ButtonLink href="/sample" variant="ghost" size="lg">
                  Or explore the sample first
                </ButtonLink>
              </div>
            </m.div>
          </Container>
        </section>
      </main>
      <SiteFooter />
    </>
  );
}
