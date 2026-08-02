import type { ExplorerDoc } from "@/lib/api";

/**
 * Search across everything the explorer already holds.
 *
 * The whole `ExplorerDoc` is in memory once the page loads, so filtering it needs no
 * request, no index and no dependency — which is also why results are instant. Matching is
 * literal rather than semantic: every whitespace-separated token must appear somewhere in
 * the record, so "late fee" finds a clause mentioning both words in either order.
 */
export type HitKind =
  | "clause"
  | "timeline"
  | "financial"
  | "question"
  | "figure"
  | "strength"
  | "recommendation";

export type SearchHit = {
  kind: HitKind;
  /** Explorer section to open when the hit is chosen. */
  sectionId: string;
  title: string;
  snippet: string;
  /** Offsets into `snippet` for the highlight. */
  matchStart: number;
  matchLength: number;
};

export const KIND_LABEL: Record<HitKind, string> = {
  clause: "Clause",
  timeline: "Timeline",
  financial: "Financial",
  question: "Question",
  figure: "Key figure",
  strength: "In your favour",
  recommendation: "Recommendation",
};

const SNIPPET_PAD = 70;

function tokenize(query: string): string[] {
  return query.toLowerCase().split(/\s+/).filter(Boolean);
}

/** Earliest position of any token, but only if *every* token is present. */
function locate(text: string, tokens: string[]): { index: number; length: number } | null {
  const hay = text.toLowerCase();
  let index = -1;
  let length = 0;
  for (const t of tokens) {
    const i = hay.indexOf(t);
    if (i === -1) return null;
    if (index === -1 || i < index) {
      index = i;
      length = t.length;
    }
  }
  return { index, length };
}

/** A window around the match, so a long clause does not dump a paragraph into the list. */
function snippetAround(text: string, index: number, length: number) {
  const start = Math.max(0, index - SNIPPET_PAD);
  const end = Math.min(text.length, index + length + SNIPPET_PAD);
  const prefix = start > 0 ? "…" : "";
  const suffix = end < text.length ? "…" : "";
  return {
    snippet: prefix + text.slice(start, end) + suffix,
    matchStart: prefix.length + (index - start),
    matchLength: length,
  };
}

function hit(
  kind: HitKind,
  sectionId: string,
  title: string,
  fields: (string | null | undefined)[],
  tokens: string[]
): SearchHit | null {
  // Title carries section and entity labels for topic search
  const text = [title, ...fields].filter(Boolean).join(" · ");
  const found = locate(text, tokens);
  if (!found) return null;
  return { kind, sectionId, title, ...snippetAround(text, found.index, found.length) };
}

export function searchExplorer(explorer: ExplorerDoc, query: string): SearchHit[] {
  const tokens = tokenize(query);
  if (!tokens.length) return [];

  const hits: (SearchHit | null)[] = [];

  for (const section of explorer.sections) {
    for (const c of section.clauses) {
      hits.push(
        hit("clause", section.id, section.label, [
          c.plain_english,
          c.why_it_matters,
          c.action_text,
          c.original_text,
          c.issue_type.replace(/_/g, " "),
        ], tokens)
      );
    }
  }

  for (const e of explorer.timeline) {
    hits.push(hit("timeline", "timeline", e.label, [e.value, e.description], tokens));
  }

  const fin = explorer.financial_impact;
  for (const [items, group] of [
    [fin.upfront_costs, "Upfront cost"],
    [fin.recurring_costs, "Recurring cost"],
    [fin.penalties, "Penalty"],
  ] as const) {
    for (const item of items) {
      hits.push(hit("financial", "financial", `${group} · ${item.label}`, [item.value], tokens));
    }
  }
  for (const r of fin.hidden_risks) {
    hits.push(hit("financial", "financial", "Hidden risk", [r], tokens));
  }

  for (const q of explorer.suggested_questions) {
    hits.push(hit("question", "questions", "Suggested question", [q.question], tokens));
  }
  for (const h of explorer.entity_highlights) {
    hits.push(hit("figure", "overview", h.label, [h.value], tokens));
  }
  for (const s of explorer.strengths) {
    hits.push(hit("strength", "strengths", "In your favour", [s], tokens));
  }
  for (const r of explorer.recommendations) {
    hits.push(hit("recommendation", "overview", "Recommended action", [r], tokens));
  }

  return hits.filter((h): h is SearchHit => h !== null);
}
