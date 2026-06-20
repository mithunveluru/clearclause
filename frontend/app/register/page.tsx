"use client";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { login, register } from "@/lib/api";

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
    <main className="mx-auto max-w-sm px-6 py-24">
      <h1 className="mb-6 text-2xl font-bold">Create account</h1>
      <form onSubmit={submit} className="flex flex-col gap-3">
        <input
          type="email" required placeholder="Email" value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="rounded-lg border px-3 py-2"
        />
        <input
          type="password" required minLength={8} placeholder="Password (min 8 chars)"
          value={password} onChange={(e) => setPassword(e.target.value)}
          className="rounded-lg border px-3 py-2"
        />
        {err && <p className="text-sm text-red-600">{err}</p>}
        <button
          disabled={busy}
          className="rounded-lg bg-blue-600 px-4 py-2 font-medium text-white hover:bg-blue-700 disabled:opacity-50"
        >
          {busy ? "…" : "Register"}
        </button>
      </form>
      <p className="mt-4 text-sm text-gray-600">
        Have an account?{" "}
        <Link href="/login" className="text-blue-600 underline">
          Log in
        </Link>
      </p>
    </main>
  );
}
