import { describe, expect, it } from "vitest";

import { searchExplorer } from "./search";
import type { ExplorerDoc } from "./api";

const doc = {
  doc_id: 1, doc_type: "loan", document_family: "consumer", risk_score: 68, risk_band: "High",
  sections: [{ id: "fees", label: "Fees and Charges", icon: "DollarSign", risk_level: "high",
    item_count: 1, summary: "", clauses: [{
      clause_id: 1, finding_id: 1,
      original_text: "A security deposit of Rs. 50,000 is payable and is non-refundable in the event of early termination by the tenant.",
      plain_english: "Your deposit is not returned if you leave early.",
      why_it_matters: "You could lose the entire deposit.", action_text: "Ask for it to be refundable.",
      issue_type: "hidden_fee", risk_level: "high", confidence: 0.9, page_number: 3 }] }],
  financial_impact: { upfront_costs: [{ label: "Security deposit", value: "Rs. 50,000" }],
    recurring_costs: [], penalties: [{ label: "Late fee", value: "Rs. 500" }],
    hidden_risks: ["Deposit may be withheld"], total_note: null },
  timeline: [{ label: "Lock-in Period", value: "11 months", entity_type: "lock_in_period",
    event_type: "period", description: "Cannot exit before this duration ends" }],
  suggested_questions: [{ question: "Is the deposit refundable?", category: "cost", finding_id: 1 }],
  walkthrough: [], entity_highlights: [{ label: "Deposit", value: "Rs. 50,000", type: "deposit_amount" }],
  analysis_summary: null, strengths: ["Notice period is reasonable"],
  recommendations: ["Get the deposit terms in writing"],
} as unknown as ExplorerDoc;

describe("searchExplorer", () => {
  it("reaches every kind of record a document holds", () => {
    const kinds = new Set(searchExplorer(doc, "deposit").map((h) => h.kind));
    for (const k of ["clause", "financial", "question", "figure", "recommendation"]) {
      expect(kinds, `missing ${k}`).toContain(k);
    }
    expect(kinds).not.toContain("timeline");
  });

  it("matches a topic by section name", () => {
    expect(searchExplorer(doc, "fees").some((h) => h.kind === "clause")).toBe(true);
  });

  it("matches the entity label, not only its value", () => {
    // Regression: titles were unsearched, so lock-in never found the timeline
    expect(searchExplorer(doc, "lock-in")[0]?.sectionId).toBe("timeline");
  });

  it("ignores case", () => {
    expect(searchExplorer(doc, "DEPOSIT").length).toBe(searchExplorer(doc, "deposit").length);
  });

  it("returns nothing for an empty or unmatched query", () => {
    expect(searchExplorer(doc, "   ")).toHaveLength(0);
    expect(searchExplorer(doc, "zebra")).toHaveLength(0);
  });

  it("requires every token regardless of order", () => {
    expect(searchExplorer(doc, "deposit refundable").length).toBeGreaterThan(0);
    expect(searchExplorer(doc, "refundable deposit").length).toBeGreaterThan(0);
    expect(searchExplorer(doc, "deposit zebra")).toHaveLength(0);
  });

  it("points the highlight at the matched term", () => {
    const hit = searchExplorer(doc, "deposit").find((h) => h.kind === "clause")!;
    const marked = hit.snippet.slice(hit.matchStart, hit.matchStart + hit.matchLength);
    expect(marked.toLowerCase()).toBe("deposit");
  });

  it("windows long text and keeps offsets inside the snippet", () => {
    for (const q of ["deposit", "rs", "e", "late fee", "notice"]) {
      for (const h of searchExplorer(doc, q)) {
        expect(h.snippet.length).toBeLessThan(180);
        expect(h.matchStart).toBeGreaterThanOrEqual(0);
        expect(h.matchStart + h.matchLength).toBeLessThanOrEqual(h.snippet.length);
      }
    }
  });

  it("routes a hit to the section that holds it", () => {
    const hit = searchExplorer(doc, "deposit").find((h) => h.kind === "clause")!;
    expect(hit.sectionId).toBe("fees");
  });
});
