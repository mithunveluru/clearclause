"use client";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { login, register } from "@/lib/api";
import { Button } from "@/components/ui/Button";
import { AuthShell, Field, Notice, PasswordField } from "@/components/ui/Form";

const MIN_LENGTH = 8;

export default function RegisterPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [touched, setTouched] = useState(false);
  const [err, setErr] = useState("");
  const [busy, setBusy] = useState(false);

  const tooShort = touched && password.length > 0 && password.length < MIN_LENGTH;

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setErr("");
    setBusy(true);
    try {
      await register(email, password);
      await login(email, password);
      router.push("/dashboard");
    } catch (e) {
      setErr((e as Error).message);
      setBusy(false);
    }
  }

  return (
    <AuthShell
      title="Create your account"
      subtitle="Upload a document and see its findings in a few moments."
      footer={<>Already have an account? <Link href="/login" className="font-medium text-brand hover:underline">Sign in</Link></>}
    >
      <form onSubmit={submit} className="flex flex-col gap-4">
        <Field label="Email" type="email" required autoComplete="email" value={email} onChange={(e) => setEmail(e.target.value)} />
        <PasswordField
          label="Password"
          required
          minLength={MIN_LENGTH}
          autoComplete="new-password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          onBlur={() => setTouched(true)}
          hint={`At least ${MIN_LENGTH} characters.`}
          error={tooShort ? `Use at least ${MIN_LENGTH} characters.` : undefined}
        />
        <Notice>{err}</Notice>
        <Button size="lg" disabled={busy} className="mt-1 w-full">
          {busy ? "Creating account…" : "Create account"}
        </Button>
        <p className="text-center text-[0.75rem] leading-relaxed text-ink-3">
          By continuing you agree to the{" "}
          <Link href="/legal/terms" className="font-medium text-ink-2 hover:text-brand">Terms</Link> and{" "}
          <Link href="/legal/privacy" className="font-medium text-ink-2 hover:text-brand">Privacy Policy</Link>.
        </p>
      </form>
    </AuthShell>
  );
}
