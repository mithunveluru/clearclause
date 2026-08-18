"use client";
import Link from "next/link";
import { useState } from "react";
import { requestPasswordReset } from "@/lib/api";
import { Button } from "@/components/ui/Button";
import { Logo } from "@/components/ui/Logo";
import { PageTransition } from "@/components/ui/PageTransition";

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [sent, setSent] = useState(false);
  const [err, setErr] = useState("");
  const [busy, setBusy] = useState(false);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setErr("");
    setBusy(true);
    try {
      await requestPasswordReset(email);
      setSent(true);
    } catch (e) {
      setErr((e as Error).message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="flex min-h-screen flex-col items-center justify-center px-6">
      <PageTransition>
        <div className="w-full max-w-sm">
          <div className="mb-10 flex justify-center">
            <Logo />
          </div>
          <h1 className="t-headline text-center">Reset your password</h1>

          {sent ? (
            // Deliberately the same message whether or not the address has an
            // account — the API does not reveal that, and neither should this page
            <>
              <p className="t-body mt-4 text-center text-[0.9375rem]">
                If that address has an account, a reset link is on its way. It expires in
                30 minutes.
              </p>
              <p className="mt-7 text-center text-[0.875rem] text-ink-2">
                <Link href="/login" className="font-medium text-accent hover:underline">
                  Back to log in
                </Link>
              </p>
            </>
          ) : (
            <>
              <p className="t-body mt-2 text-center text-[0.9375rem]">
                We&rsquo;ll email you a link to choose a new one.
              </p>
              <form onSubmit={submit} className="mt-9 flex flex-col gap-3">
                <input
                  className="field"
                  type="email"
                  required
                  aria-label="Email"
                  autoComplete="email"
                  placeholder="Email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                />
                {err && <p className="text-sm text-risk-high">{err}</p>}
                <Button size="lg" disabled={busy} className="mt-3 w-full">
                  {busy ? "Sending…" : "Send reset link"}
                </Button>
              </form>
              <p className="mt-7 text-center text-[0.875rem] text-ink-2">
                Remembered it?{" "}
                <Link href="/login" className="font-medium text-accent hover:underline">
                  Log in
                </Link>
              </p>
            </>
          )}
        </div>
      </PageTransition>
    </div>
  );
}
