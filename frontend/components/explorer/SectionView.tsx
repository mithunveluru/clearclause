"use client";
import { m } from "framer-motion";
import type { ExplorerSection } from "@/lib/api";
import { ClauseCard, type ReadingMode } from "./ClauseCard";

export function SectionView({
  section,
  mode,
}: {
  section: ExplorerSection;
  mode: ReadingMode;
}) {
  return (
    <m.div
      key={section.id}
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, ease: [0.22, 1, 0.36, 1] }}
    >
      <div className="mb-6">
        <h2 className="text-[1.375rem] font-bold tracking-tight">{section.label}</h2>
        <p className="mt-1 t-body text-ink-2">{section.summary}</p>
        <p className="mt-1 t-caption">
          {section.item_count} {section.item_count === 1 ? "issue" : "issues"} detected
        </p>
      </div>

      <div className="space-y-4">
        {section.clauses.map((c, i) => (
          <ClauseCard key={c.finding_id ?? i} clause={c} mode={mode} index={i} />
        ))}
      </div>
    </m.div>
  );
}
