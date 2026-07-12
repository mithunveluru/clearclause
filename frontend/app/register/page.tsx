"use client";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { Lock } from "lucide-react";
import { login, register } from "@/lib/api";
import { Button } from "@/components/ui/Button";
import { Logo } from "@/components/ui/Logo";
import { PageTransition } from "@/components/ui/PageTransition";

export default function RegisterPage() {
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
      await register(email, password);
      await login(email, password);
      router.push("/dashboard");
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
          <h1 className="t-headline text-center">Create your account</h1>
          <p className="t-body mt-2 text-center text-[0.9375rem]">
            Start reviewing documents in seconds.
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
            <input
              className="field"
              type="password"
              required
              minLength={8}
              aria-label="Password"
              autoComplete="new-password"
              placeholder="Password (min 8 characters)"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
            {err && <p className="text-sm text-risk-high">{err}</p>}
            <Button size="lg" disabled={busy} className="mt-3 w-full">
              {busy ? "Creating…" : "Create account"}
            </Button>
            <p className="mt-1 text-center text-[0.75rem] leading-relaxed text-ink-3">
              By creating an account you agree to the{" "}
              <Link href="/legal/terms" className="font-medium text-ink-2 hover:text-brand">
                Terms of Service
              </Link>{" "}
              and{" "}
              <Link href="/legal/privacy" className="font-medium text-ink-2 hover:text-brand">
                Privacy Policy
              </Link>
              .
            </p>
          </form>
          <p className="mt-7 text-center text-[0.875rem] text-ink-2">
            Already have an account?{" "}
            <Link href="/login" className="font-medium text-accent hover:underline">
              Log in
            </Link>
          </p>
          <p className="mt-10 flex items-center justify-center gap-1.5 text-[0.75rem] text-ink-3">
            <Lock className="h-3 w-3" strokeWidth={2} />
            Encrypted in transit · your documents stay private
          </p>
        </div>
      </PageTransition>
    </div>
  );
}
