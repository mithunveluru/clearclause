"use client";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { Suspense, useState } from "react";
import { resetPassword } from "@/lib/api";
import { Button } from "@/components/ui/Button";
import { AuthShell, Notice, PasswordField } from "@/components/ui/Form";

const MIN_LENGTH = 8;

const newLink = <Link href="/forgot-password" className="font-medium text-brand hover:underline">Request a new link</Link>;

function ResetForm() {
  const router = useRouter();
  const token = useSearchParams().get("token") ?? "";
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [confirmTouched, setConfirmTouched] = useState(false);
  const [err, setErr] = useState("");
  const [busy, setBusy] = useState(false);

  const mismatch = confirmTouched && confirm.length > 0 && confirm !== password;

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    if (password !== confirm) {
      setConfirmTouched(true);
      return;
    }
    setErr("");
    setBusy(true);
    try {
      await resetPassword(token, password);
      router.push("/login?reset=1");
    } catch (e) {
      setErr((e as Error).message);
      setBusy(false);
    }
  }

  if (!token) {
    return (
      <AuthShell title="This link is incomplete" subtitle="Open the link exactly as it appears in the email, or request a new one." footer={newLink}>
        {null}
      </AuthShell>
    );
  }

  return (
    <AuthShell
      title="Choose a new password"
      subtitle={`At least ${MIN_LENGTH} characters. A short phrase beats a short password.`}
      footer={newLink}
    >
      <form onSubmit={submit} className="flex flex-col gap-4">
        <PasswordField label="New password" required minLength={MIN_LENGTH} autoComplete="new-password" value={password} onChange={(e) => setPassword(e.target.value)} />
        <PasswordField
          label="Confirm new password"
          required
          minLength={MIN_LENGTH}
          autoComplete="new-password"
          value={confirm}
          onChange={(e) => setConfirm(e.target.value)}
          onBlur={() => setConfirmTouched(true)}
          error={mismatch ? "Those two passwords don't match." : undefined}
        />
        <Notice>{err}</Notice>
        <Button size="lg" disabled={busy} className="mt-1 w-full">
          {busy ? "Saving…" : "Set new password"}
        </Button>
      </form>
    </AuthShell>
  );
}

export default function ResetPasswordPage() {
  return (
    <Suspense fallback={null}>
      <ResetForm />
    </Suspense>
  );
}
