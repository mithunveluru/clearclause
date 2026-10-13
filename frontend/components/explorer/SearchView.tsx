"use client";
import { m } from "framer-motion";
import { SearchX } from "lucide-react";
import { viewTransition } from "@/components/ui/motion";
import { KIND_LABEL, type SearchHit } from "@/lib/search";

/** Renders the snippet with the matched span marked. Built from offsets rather than a
 *  regex replace, so a query containing regex characters cannot break the output. */
function Highlighted({ hit }: { hit: SearchHit }) {
  const { snippet, matchStart, matchLength } = hit;
  return (
    <>
      {snippet.slice(0, matchStart)}
      <mark className="rounded-[3px] bg-ochre-soft px-0.5 shadow-[inset_0_-1px_0_theme(colors.ochre.DEFAULT)] text-ink">
        {snippet.slice(matchStart, matchStart + matchLength)}
      </mark>
      {snippet.slice(matchStart + matchLength)}
    </>
  );
}

export function SearchView({
  query,
  hits,
  onSelect,
}: {
  query: string;
  hits: SearchHit[];
  onSelect: (sectionId: string) => void;
}) {
  return (
    <m.div {...viewTransition}>
      <h2 className="mb-1 text-[1.375rem] font-semibold tracking-tight">
        {hits.length} {hits.length === 1 ? "result" : "results"}
      </h2>
      <p className="mb-6 t-body text-ink-2">
        Matching “{query}” across this document&apos;s clauses, figures, dates, and questions.
      </p>

      {hits.length === 0 ? (
        <div className="flex flex-col items-center rounded-xl border border-line bg-surface px-6 py-14 text-center">
          <span className="flex h-11 w-11 items-center justify-center rounded-xl bg-brand/[0.07] text-brand">
            <SearchX className="h-5 w-5" strokeWidth={1.75} />
          </span>
          <p className="mt-4 text-[0.9375rem] font-medium text-ink">Nothing matched that</p>
          <p className="t-caption mt-1.5 max-w-xs">
            Only this document is searched — if the wording never appears in it, there is
            nothing to find.
          </p>
        </div>
      ) : (
        <ul className="space-y-2">
          {hits.map((h, i) => (
            <li key={i}>
              <button
                onClick={() => onSelect(h.sectionId)}
                className="w-full rounded-xl border border-line bg-surface px-4 py-3.5 text-left transition hover:border-brand/30 hover:bg-brand/[0.02] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand/30"
              >
                <span className="flex items-baseline gap-2">
                  <span className="text-[0.6875rem] font-semibold uppercase tracking-[0.08em] text-ink-3">
                    {KIND_LABEL[h.kind]}
                  </span>
                  <span className="truncate text-[0.9375rem] font-semibold">{h.title}</span>
                </span>
                <span className="mt-1 block text-[0.875rem] leading-relaxed text-ink-2">
                  <Highlighted hit={h} />
                </span>
              </button>
            </li>
          ))}
        </ul>
      )}
    </m.div>
  );
}
