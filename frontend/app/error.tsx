"use client";
import { useEffect } from "react";
import { Mark } from "@/components/ui/Logo";
import { Button, ButtonLink } from "@/components/ui/Button";

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error(error);
  }, [error]);

  return (
    <main className="flex min-h-screen flex-col items-center justify-center bg-canvas px-6 text-center">
      <Mark className="h-9 w-9" />
      <h1 className="mt-6 text-[1.375rem] font-semibold tracking-tight">Something went wrong</h1>
      <p className="mt-2 max-w-sm text-[0.9375rem] leading-relaxed text-ink-2">
        An unexpected error stopped this page. Your documents are unaffected.
      </p>
      <div className="mt-7 flex gap-2">
        <Button onClick={reset}>Try again</Button>
        <ButtonLink href="/dashboard" variant="ghost">Go to documents</ButtonLink>
      </div>
    </main>
  );
}
