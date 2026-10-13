"use client";
import { AnimatePresence, m } from "framer-motion";
import { Menu, X } from "lucide-react";
import Link from "next/link";
import { useEffect, useState } from "react";
import { ButtonLink } from "@/components/ui/Button";
import { Logo } from "@/components/ui/Logo";
import { Container } from "@/components/ui/Surface";
import { easeSmooth } from "@/components/ui/motion";

const NAV = [
  ["Product", "/#product"],
  ["How it works", "/#how-it-works"],
  ["Document types", "/#documents"],
  ["Sample analysis", "/sample"],
] as const;

export function SiteHeader() {
  const [open, setOpen] = useState(false);

  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && setOpen(false);
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open]);

  return (
    <header className="sticky top-0 z-40 border-b border-line/70 bg-canvas/85 backdrop-blur-md print:hidden">
      <Container className="flex h-16 items-center justify-between gap-6">
        <Logo />
        <nav aria-label="Main" className="hidden items-center gap-1 md:flex">
          {NAV.map(([label, href]) => (
            <Link
              key={href}
              href={href}
              className="rounded-md px-3 py-2 text-[0.875rem] font-medium text-ink-2 transition-colors duration-150 hover:text-ink"
            >
              {label}
            </Link>
          ))}
        </nav>
        <div className="hidden items-center gap-1 md:flex">
          <ButtonLink href="/login" variant="ghost">Sign in</ButtonLink>
          <ButtonLink href="/dashboard">Analyze a document</ButtonLink>
        </div>
        <button
          className="-mr-2 flex h-11 w-11 items-center justify-center rounded-lg text-ink md:hidden"
          aria-label={open ? "Close menu" : "Open menu"}
          aria-expanded={open}
          aria-controls="mobile-nav"
          onClick={() => setOpen((o) => !o)}
        >
          {open ? <X className="h-5 w-5" strokeWidth={1.75} /> : <Menu className="h-5 w-5" strokeWidth={1.75} />}
        </button>
      </Container>
      <AnimatePresence>
        {open && (
          <m.nav
            id="mobile-nav"
            aria-label="Main"
            initial={{ opacity: 0, y: -6 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -6 }}
            transition={{ duration: 0.2, ease: easeSmooth }}
            className="border-t border-line bg-canvas md:hidden"
          >
            <Container className="flex flex-col py-3">
              {NAV.map(([label, href]) => (
                <Link
                  key={href}
                  href={href}
                  onClick={() => setOpen(false)}
                  className="border-b border-line py-3.5 text-[0.9375rem] font-medium text-ink"
                >
                  {label}
                </Link>
              ))}
              <div className="mt-4 grid grid-cols-2 gap-2 pb-2">
                <ButtonLink href="/login" variant="secondary">Sign in</ButtonLink>
                <ButtonLink href="/dashboard">Analyze</ButtonLink>
              </div>
            </Container>
          </m.nav>
        )}
      </AnimatePresence>
    </header>
  );
}

const FOOTER: { title: string; links: [string, string][] }[] = [
  {
    title: "Product",
    links: [
      ["How it works", "/#how-it-works"],
      ["Document types", "/#documents"],
      ["Sample analysis", "/sample"],
      ["Workspace", "/dashboard"],
    ],
  },
  {
    title: "Policies",
    links: [
      ["Terms", "/legal/terms"],
      ["Privacy", "/legal/privacy"],
      ["Cookies", "/legal/cookies"],
      ["AI disclaimer", "/legal/ai-disclaimer"],
    ],
  },
  {
    title: "Company",
    links: [
      ["Security", "/legal/security"],
      ["Contact", "/legal/contact"],
    ],
  },
];

export function SiteFooter() {
  return (
    <footer className="border-t border-line bg-sunken/60 print:hidden">
      <Container className="grid gap-10 py-14 sm:grid-cols-[1.4fr_repeat(3,1fr)]">
        <div>
          <Logo />
          <p className="mt-4 max-w-xs text-[0.8125rem] leading-relaxed text-ink-2">
            Structured review of financial and property documents. Informational analysis
            only — not legal or financial advice.
          </p>
        </div>
        {FOOTER.map((col) => (
          <nav key={col.title} aria-label={col.title}>
            <p className="text-[0.75rem] font-semibold text-ink">{col.title}</p>
            <ul className="mt-3 space-y-2.5">
              {col.links.map(([label, href]) => (
                <li key={href}>
                  <Link href={href} className="text-[0.8125rem] text-ink-2 transition-colors hover:text-ink">
                    {label}
                  </Link>
                </li>
              ))}
            </ul>
          </nav>
        ))}
      </Container>
      <Container className="border-t border-line py-6">
        <p className="t-caption tabular-nums">© {new Date().getFullYear()} ClearClause</p>
      </Container>
    </footer>
  );
}
