"use client";
import { AnimatePresence, m } from "framer-motion";
import { AlertCircle, Eye, EyeOff } from "lucide-react";
import Link from "next/link";
import { useId, useState, type ComponentProps, type ReactNode } from "react";
import { Logo } from "@/components/ui/Logo";
import { easeSmooth } from "@/components/ui/motion";

/** Centered single-column layout shared by every sign-in / recovery screen. */
export function AuthShell({
  title,
  subtitle,
  children,
  footer,
}: {
  title: string;
  subtitle?: ReactNode;
  children: ReactNode;
  footer?: ReactNode;
}) {
  return (
    <div className="flex min-h-screen flex-col bg-canvas">
      <header className="px-6 py-5">
        <Logo />
      </header>
      <main className="flex flex-1 items-start justify-center px-5 pb-16 pt-6 sm:items-center sm:pt-0">
        <m.div
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, ease: easeSmooth }}
          className="w-full max-w-[400px]"
        >
          <div className="rounded-xl border border-line bg-surface px-6 py-8 shadow-soft sm:px-8">
            <h1 className="text-[1.375rem] font-semibold tracking-tight">{title}</h1>
            {subtitle && <p className="mt-1.5 text-[0.9375rem] leading-relaxed text-ink-2">{subtitle}</p>}
            <div className="mt-7">{children}</div>
          </div>
          {footer && <div className="mt-6 text-center text-[0.875rem] text-ink-2">{footer}</div>}
        </m.div>
      </main>
      <footer className="flex flex-wrap justify-center gap-x-5 gap-y-1 px-6 pb-6 text-[0.75rem] text-ink-3">
        <Link href="/legal/terms" className="hover:text-ink">Terms</Link>
        <Link href="/legal/privacy" className="hover:text-ink">Privacy</Link>
        <Link href="/legal/security" className="hover:text-ink">Security</Link>
      </footer>
    </div>
  );
}

type FieldProps = { label: string; hint?: string; error?: string } & ComponentProps<"input">;

export function Field({ label, hint, error, id, ...props }: FieldProps) {
  const auto = useId();
  const fid = id ?? auto;
  const describedBy = [hint && `${fid}-hint`, error && `${fid}-err`].filter(Boolean).join(" ") || undefined;
  return (
    <div>
      <label htmlFor={fid} className="label">{label}</label>
      <input id={fid} className="field" aria-invalid={!!error} aria-describedby={describedBy} {...props} />
      {hint && !error && <p id={`${fid}-hint`} className="mt-1.5 text-[0.75rem] text-ink-3">{hint}</p>}
      {error && <p id={`${fid}-err`} className="mt-1.5 text-[0.8125rem] text-risk-high">{error}</p>}
    </div>
  );
}

export function PasswordField({ label, hint, error, id, ...props }: FieldProps) {
  const auto = useId();
  const fid = id ?? auto;
  const [show, setShow] = useState(false);
  const describedBy = [hint && `${fid}-hint`, error && `${fid}-err`].filter(Boolean).join(" ") || undefined;
  return (
    <div>
      <label htmlFor={fid} className="label">{label}</label>
      <div className="relative">
        <input
          id={fid}
          type={show ? "text" : "password"}
          className="field pr-11"
          aria-invalid={!!error}
          aria-describedby={describedBy}
          {...props}
        />
        <button
          type="button"
          onClick={() => setShow((s) => !s)}
          aria-label={show ? "Hide password" : "Show password"}
          aria-pressed={show}
          className="absolute right-1 top-1/2 flex h-9 w-9 -translate-y-1/2 items-center justify-center rounded-md text-ink-3 transition-colors hover:text-ink focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand/30"
        >
          {show ? <EyeOff className="h-4 w-4" strokeWidth={1.75} /> : <Eye className="h-4 w-4" strokeWidth={1.75} />}
        </button>
      </div>
      {hint && !error && <p id={`${fid}-hint`} className="mt-1.5 text-[0.75rem] text-ink-3">{hint}</p>}
      {error && <p id={`${fid}-err`} className="mt-1.5 text-[0.8125rem] text-risk-high">{error}</p>}
    </div>
  );
}

/** Form-level message (server errors, success notes). Announced when it appears. */
export function Notice({ tone = "error", children }: { tone?: "error" | "success"; children: ReactNode }) {
  const err = tone === "error";
  return (
    <AnimatePresence>
      {children && (
        <m.div
          role={err ? "alert" : "status"}
          initial={{ opacity: 0, y: -4 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.18, ease: easeSmooth }}
          className={`flex items-start gap-2.5 rounded-lg border px-3 py-2.5 text-[0.8125rem] leading-relaxed ${
            err ? "border-risk-high/25 bg-risk-high-tint text-risk-high" : "border-risk-low/25 bg-risk-low-tint text-risk-low"
          }`}
        >
          {err && <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" strokeWidth={1.75} aria-hidden />}
          <span>{children}</span>
        </m.div>
      )}
    </AnimatePresence>
  );
}
