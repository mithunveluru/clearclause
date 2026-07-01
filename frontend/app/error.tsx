"use client";
import { useEffect } from "react";
import { Button } from "@/components/ui/Button";
import { Container } from "@/components/ui/Surface";

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
    <Container className="py-24 text-center">
      <p className="eyebrow mb-3">Something went wrong</p>
      <p className="t-body text-ink-2 mb-6 max-w-sm mx-auto">
        An unexpected error occurred. Try refreshing the page.
      </p>
      <Button variant="secondary" onClick={reset}>Try again</Button>
    </Container>
  );
}
