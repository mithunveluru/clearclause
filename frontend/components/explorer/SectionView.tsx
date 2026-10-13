"use client";
import { m } from "framer-motion";
import { viewTransition } from "@/components/ui/motion";
import type { ExplorerSection } from "@/lib/api";
import { ClauseCard, type ReadingMode } from "./ClauseCard";

export function SectionView({
  section,
  mode,
  docId,
}: {
  section: ExplorerSection;
  mode: ReadingMode;
  /** Omitted by the sample explorer, which has no stored file to link to. */
  docId?: number;
}) {
  return (
    <m.div key={section.id} {...viewTransition}>
      <div className="mb-6">
        <h2 className="text-[1.375rem] font-semibold tracking-tight">{section.label}</h2>
        <p className="mt-1 t-body text-ink-2">{section.summary}</p>
        <p className="mt-1 t-caption">
          {section.item_count} {section.item_count === 1 ? "issue" : "issues"} detected
        </p>
      </div>

      <div className="space-y-4">
        {section.clauses.map((c, i) => (
          <ClauseCard key={c.finding_id ?? i} clause={c} mode={mode} index={i} docId={docId} />
        ))}
      </div>
    </m.div>
  );
}
