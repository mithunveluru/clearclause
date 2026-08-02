export type SeverityKey = "critical" | "high" | "medium" | "low";

/**
 * The one definition of the risk palette.
 *
 * `tailwind.config.ts` imports this to build the `risk-*` utilities, so a Tailwind class
 * and an inline `style` can no longer disagree — they did, across four separate copies of
 * these values. Inline styles are still needed wherever the severity is only known at
 * runtime, since Tailwind cannot build a class name from a variable.
 *
 * WCAG-checked. Each colour as text on its own tint:
 *   critical 7.49 · high 5.91 · medium 4.73 · low 4.79   (4.5 required)
 * and on both page backgrounds (canvas #fafbff, surface #ffffff): 4.85 or better.
 */
export const RISK: Record<SeverityKey, { label: string; color: string; tint: string }> = {
  critical: { label: "Critical", color: "#991b1b", tint: "#fef0f0" },
  high: { label: "High", color: "#b91c1c", tint: "#fef2f2" },
  medium: { label: "Medium", color: "#b45309", tint: "#fff7ed" },
  low: { label: "Low", color: "#15803d", tint: "#f0fdf4" },
};

/** The single accent. 6.29:1 on white. */
export const BRAND = "#4f46e5";

/** For categories that carry no risk signal. Same value as the `ink-3` token (5.4:1). */
export const NEUTRAL = "#5b6b80";

/** Score bands are the severity scale under other names — derived, not restated. */
const BAND_SEVERITY: Record<string, SeverityKey> = {
  Low: "low",
  Moderate: "medium",
  High: "high",
  Critical: "critical",
};

export function severityMeta(s: string) {
  return RISK[s as SeverityKey] ?? RISK.low;
}

export function bandMeta(b: string) {
  const key = b in BAND_SEVERITY ? b : "Low";
  return { ...RISK[BAND_SEVERITY[key]], tone: `${key} risk` };
}

/** Confidence rides the same scale, inverted: high confidence reads as low risk. */
export function confidenceColor(confidence: number): string {
  if (confidence >= 0.8) return RISK.low.color;
  if (confidence >= 0.6) return RISK.medium.color;
  return RISK.high.color;
}

export function issueLabel(issueType: string): string {
  return issueType
    .replace(/_/g, " ")
    .replace(/\b\w/g, (c) => c.toUpperCase());
}

export function docTypeLabel(t: string | null | undefined): string {
  if (!t || t === "unknown") return "Unclassified";
  return t.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}
