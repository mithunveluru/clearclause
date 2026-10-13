"use client";
import Link from "next/link";
import { useState } from "react";
import { requestPasswordReset } from "@/lib/api";
import { Button } from "@/components/ui/Button";
import { AuthShell, Field, Notice } from "@/components/ui/Form";

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

  const back = <Link href="/login" className="font-medium text-brand hover:underline">Back to sign in</Link>;

  // Deliberately the same message whether or not the address has an
  // account — the API does not reveal that, and neither should this page
  if (sent) {
    return (
      <AuthShell title="Check your email" footer={back}>
        <Notice tone="success">
          If that address has an account, a reset link is on its way. It expires in 30 minutes.
        </Notice>
      </AuthShell>
    );
  }

  return (
    <AuthShell title="Reset your password" subtitle="We'll email you a link to choose a new one." footer={back}>
      <form onSubmit={submit} className="flex flex-col gap-4">
        <Field label="Email" type="email" required autoComplete="email" value={email} onChange={(e) => setEmail(e.target.value)} />
        <Notice>{err}</Notice>
        <Button size="lg" disabled={busy} className="mt-1 w-full">
          {busy ? "Sending…" : "Send reset link"}
        </Button>
      </form>
    </AuthShell>
  );
}
