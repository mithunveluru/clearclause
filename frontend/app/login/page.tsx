"use client";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { Suspense, useState } from "react";
import { login } from "@/lib/api";
import { Button } from "@/components/ui/Button";
import { AuthShell, Field, Notice, PasswordField } from "@/components/ui/Form";

function ResetNotice() {
  // useSearchParams needs its own boundary or the route opts out of prerendering
  const reset = useSearchParams().get("reset") === "1";
  return reset ? <div className="mb-5"><Notice tone="success">Password updated. Sign in with your new password.</Notice></div> : null;
}

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [err, setErr] = useState("");
  const [busy, setBusy] = useState(false);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setErr("");
    setBusy(true);
    try {
      await login(email, password);
      router.push("/dashboard");
    } catch (e) {
      setErr((e as Error).message);
      setBusy(false);
    }
  }

  return (
    <AuthShell
      title="Sign in"
      subtitle="Continue to your documents."
      footer={<>New to ClearClause? <Link href="/register" className="font-medium text-brand hover:underline">Create an account</Link></>}
    >
      <Suspense fallback={null}><ResetNotice /></Suspense>
      <form onSubmit={submit} className="flex flex-col gap-4">
        <Field label="Email" type="email" required autoComplete="email" value={email} onChange={(e) => setEmail(e.target.value)} />
        <div>
          <PasswordField label="Password" required autoComplete="current-password" value={password} onChange={(e) => setPassword(e.target.value)} />
          <Link href="/forgot-password" className="mt-2 inline-block text-[0.8125rem] text-ink-2 hover:text-brand hover:underline">
            Forgot your password?
          </Link>
        </div>
        <Notice>{err}</Notice>
        <Button size="lg" disabled={busy} className="mt-1 w-full">
          {busy ? "Signing in…" : "Sign in"}
        </Button>
      </form>
    </AuthShell>
  );
}
