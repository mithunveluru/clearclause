"use client";
import { m } from "framer-motion";
import { easeSmooth } from "@/components/ui/motion";
import type { ReactNode } from "react";

export function PageTransition({ children }: { children: ReactNode }) {
  return (
    <m.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, ease: easeSmooth }}
    >
      {children}
    </m.div>
  );
}
