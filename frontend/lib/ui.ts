export type SeverityKey = "critical" | "high" | "medium" | "low";

export const SEVERITY: Record<SeverityKey, { label: string; color: string; tint: string }> = {
  critical: { label: "Critical", color: "#7c1d12", tint: "#fbeae8" },
  high: { label: "High", color: "#c0362c", tint: "#fdeceb" },
  medium: { label: "Medium", color: "#b2670a", tint: "#fbf2e6" },
  low: { label: "Low", color: "#1a7f5a", tint: "#e9f5ef" },
};

export const BAND: Record<string, { color: string; tint: string; tone: string }> = {
  Low: { color: "#1a7f5a", tint: "#e9f5ef", tone: "Low risk" },
  Moderate: { color: "#b2670a", tint: "#fbf2e6", tone: "Moderate risk" },
  High: { color: "#c0362c", tint: "#fdeceb", tone: "High risk" },
  Critical: { color: "#7c1d12", tint: "#fbeae8", tone: "Critical risk" },
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
