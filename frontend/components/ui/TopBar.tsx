import type { ReactNode } from "react";
import { Container } from "@/components/ui/Surface";
import { Logo } from "@/components/ui/Logo";

export function TopBar({ right }: { right?: ReactNode }) {
  return (
    <header className="sticky top-0 z-40 border-b border-line/70 bg-canvas/80 backdrop-blur-xl">
      <Container className="flex h-16 items-center justify-between">
        <Logo />
        <div className="flex items-center gap-2">{right}</div>
      </Container>
    </header>
  );
}
