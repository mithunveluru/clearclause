"use client";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { Suspense, useState } from "react";
import { resetPassword } from "@/lib/api";
import { Button } from "@/components/ui/Button";
import { Logo } from "@/components/ui/Logo";
import { PageTransition } from "@/components/ui/PageTransition";

const MIN_LENGTH = 8;

function ResetForm() {
  const router = useRouter();
  const token = useSearchParams().get("token") ?? "";
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [err, setErr] = useState("");
  const [busy, setBusy] = useState(false);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    if (password !== confirm) {
      setErr("Those two passwords don't match.");
      return;
    }
    setErr("");
    setBusy(true);
    try {
      await resetPassword(token, password);
      router.push("/login?reset=1");
    } catch (e) {
      setErr((e as Error).message);
    } finally {
      setBusy(false);
    }
  }

  if (!token) {
    return (
      <>
        <h1 className="t-headline text-center">This link is incomplete</h1>
        <p className="t-body mt-4 text-center text-[0.9375rem]">
          Open the link exactly as it appears in the email, or request a new one.
        </p>
        <p className="mt-7 text-center text-[0.875rem] text-ink-2">
          <Link href="/forgot-password" className="font-medium text-accent hover:underline">
            Request a new link
          </Link>
        </p>
      </>
    );
  }

  return (
    <>
      <h1 className="t-headline text-center">Choose a new password</h1>
      <p className="t-body mt-2 text-center text-[0.9375rem]">
        At least {MIN_LENGTH} characters. A short phrase beats a short password.
      </p>
      <form onSubmit={submit} className="mt-9 flex flex-col gap-3">
        <input
          className="field"
          type="password"
          required
          minLength={MIN_LENGTH}
          aria-label="New password"
          autoComplete="new-password"
          placeholder="New password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        <input
          className="field"
          type="password"
          required
          minLength={MIN_LENGTH}
          aria-label="Confirm new password"
          autoComplete="new-password"
          placeholder="Confirm new password"
          value={confirm}
          onChange={(e) => setConfirm(e.target.value)}
        />
        {err && <p className="text-sm text-risk-high">{err}</p>}
        <Button size="lg" disabled={busy} className="mt-3 w-full">
          {busy ? "Saving…" : "Set new password"}
        </Button>
      </form>
      <p className="mt-7 text-center text-[0.875rem] text-ink-2">
        <Link href="/forgot-password" className="font-medium text-accent hover:underline">
          Request a new link
        </Link>
      </p>
    </>
  );
}

export default function ResetPasswordPage() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center px-6">
      <PageTransition>
        <div className="w-full max-w-sm">
          <div className="mb-10 flex justify-center">
            <Logo />
          </div>
          {/* useSearchParams needs a boundary or the whole route opts out of prerendering */}
          <Suspense fallback={<p className="t-body text-center">Loading…</p>}>
            <ResetForm />
          </Suspense>
        </div>
      </PageTransition>
    </div>
  );
}
