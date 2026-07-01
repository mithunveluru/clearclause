export type SeverityKey = "critical" | "high" | "medium" | "low";

export const SEVERITY: Record<SeverityKey, { label: string; color: string; tint: string }> = {
  critical: { label: "Critical", color: "#991b1b", tint: "#fef0f0" },
  high: { label: "High", color: "#dc2626", tint: "#fef2f2" },
  medium: { label: "Medium", color: "#d97706", tint: "#fff7ed" },
  low: { label: "Low", color: "#16a34a", tint: "#f0fdf4" },
};

export const BAND: Record<string, { color: string; tint: string; tone: string }> = {
  Low: { color: "#16a34a", tint: "#f0fdf4", tone: "Low risk" },
  Moderate: { color: "#d97706", tint: "#fff7ed", tone: "Moderate risk" },
  High: { color: "#dc2626", tint: "#fef2f2", tone: "High risk" },
  Critical: { color: "#991b1b", tint: "#fef0f0", tone: "Critical risk" },
};

export function severityMeta(s: string) {
  return SEVERITY[(s as SeverityKey)] ?? SEVERITY.low;
}

export function bandMeta(b: string) {
  return BAND[b] ?? BAND.Low;
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
