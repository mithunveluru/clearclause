import Link from "next/link";
import type { ReactNode } from "react";
import { Container } from "@/components/ui/Surface";

export const LEGAL_DOCS = [
  { href: "/legal/terms", label: "Terms of Service" },
  { href: "/legal/privacy", label: "Privacy Policy" },
  { href: "/legal/ai-disclaimer", label: "AI Disclaimer" },
  { href: "/legal/security", label: "Security" },
  { href: "/legal/cookies", label: "Cookie Policy" },
  { href: "/legal/contact", label: "Contact" },
];

export type LegalSection = { id: string; title: string; body: ReactNode };

export function LegalDoc({
  title,
  updated,
  intro,
  sections,
  current,
}: {
  title: string;
  updated: string;
  intro?: ReactNode;
  sections: LegalSection[];
  current: string;
}) {
  return (
    <Container className="py-14">
      <div className="grid gap-12 lg:grid-cols-[230px_minmax(0,1fr)]">
        <aside className="print:hidden">
          <div className="space-y-9 lg:sticky lg:top-24">
            <nav aria-label="Legal documents">
              <p className="eyebrow mb-3">Legal</p>
              <ul className="space-y-0.5">
                {LEGAL_DOCS.map((d) => (
                  <li key={d.href}>
                    <Link
                      href={d.href}
                      aria-current={d.href === current ? "page" : undefined}
                      className={`block rounded-lg px-3 py-1.5 text-[0.875rem] transition ${
                        d.href === current
                          ? "bg-brand/[0.08] font-semibold text-brand"
                          : "text-ink-2 hover:bg-sunken hover:text-ink"
                      }`}
                    >
                      {d.label}
                    </Link>
                  </li>
                ))}
              </ul>
            </nav>
            <nav aria-label="On this page" className="hidden lg:block">
              <p className="mb-3 px-3 text-[0.6875rem] font-semibold uppercase tracking-[0.09em] text-ink-3">
                On this page
              </p>
              <ul className="space-y-0.5 border-l border-line">
                {sections.map((s, i) => (
                  <li key={s.id}>
                    <a
                      href={`#${s.id}`}
                      className="block px-3 py-1 text-[0.8125rem] leading-snug text-ink-2 transition hover:text-brand"
                    >
                      {i + 1}. {s.title}
                    </a>
                  </li>
                ))}
              </ul>
            </nav>
          </div>
        </aside>

        <article className="max-w-[70ch]">
          <p className="eyebrow">ClearClause Legal</p>
          <h1 className="t-headline mt-2">{title}</h1>
          <p className="t-caption mt-3">Last updated: {updated}</p>
          {intro && <div className="prose-legal mt-7">{intro}</div>}
          {sections.map((s, i) => (
            <section key={s.id} id={s.id} className="mt-11 scroll-mt-24">
              <h2 className="text-[1.125rem] font-semibold tracking-tight text-ink">
                {i + 1}. {s.title}
              </h2>
              <div className="prose-legal mt-3">{s.body}</div>
            </section>
          ))}
          <p className="mt-14 border-t border-line pt-6 text-[0.8125rem] leading-relaxed text-ink-3">
            ClearClause is a demonstration product built to showcase document-intelligence
            engineering. It is not offered as a commercial service, and the contact addresses
            on these pages are illustrative.
          </p>
        </article>
      </div>
    </Container>
  );
}
