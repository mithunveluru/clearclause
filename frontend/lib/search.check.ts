/**
 * Assertions for `searchExplorer`. Not wired to a runner — the frontend has no test
 * framework and adding one for a single file is not worth the dependency. Run it with:
 *
 *   docker run --rm -v "$PWD:/app" -v /app/node_modules -v /app/.next -w /app \
 *     clearclause-frontend sh -c 'npx esbuild lib/search.check.ts --bundle \
 *     --platform=node --outfile=/tmp/c.js --log-level=error && node /tmp/c.js'
 *
 * It caught two real bugs: hit titles were not searched, so "lock-in" missed the timeline
 * and "deposit" missed the key figure.
 */
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
  analysis_summary: null, strengths: ["Notice period is reasonable"], recommendations: ["Get the deposit terms in writing"],
} as unknown as ExplorerDoc;

let failures = 0;
function check(name: string, cond: boolean, extra = "") {
  if (!cond) { failures++; console.log("  FAIL " + name + " " + extra); }
  else console.log("  ok   " + name);
}

const deposit = searchExplorer(doc, "deposit");
const kinds = new Set(deposit.map(h => h.kind));
for (const k of ["clause", "financial", "question", "figure", "recommendation"]) {
  check("'deposit' reaches kind: " + k, kinds.has(k as never), "kinds=" + JSON.stringify([...kinds]));
}
check("'deposit' does not invent a timeline hit", !kinds.has("timeline" as never));
check("topic search by section name", searchExplorer(doc, "fees").some(h => h.kind === "clause"));
check("case-insensitive", searchExplorer(doc, "DEPOSIT").length === deposit.length);
check("empty query returns nothing", searchExplorer(doc, "   ").length === 0);
check("no match returns nothing", searchExplorer(doc, "zebra").length === 0);

const multi = searchExplorer(doc, "deposit refundable");
check("all tokens required (order-independent)", multi.length > 0, "got " + multi.length);
check("token missing => no hit", searchExplorer(doc, "deposit zebra").length === 0);

const clause = deposit.find(h => h.kind === "clause")!;
check("highlight offsets land on the term",
      clause.snippet.slice(clause.matchStart, clause.matchStart + clause.matchLength).toLowerCase() === "deposit",
      "got '" + clause.snippet.slice(clause.matchStart, clause.matchStart + clause.matchLength) + "'");
check("long text is windowed", clause.snippet.length < 160, "len=" + clause.snippet.length);
check("hit routes to its section", clause.sectionId === "fees", clause.sectionId);
check("timeline hit routes to timeline",
      searchExplorer(doc, "lock-in")[0]?.sectionId === "timeline");

// Every hit's offsets must be valid, whatever the query
for (const q of ["deposit", "rs", "e", "late fee", "notice"]) {
  for (const h of searchExplorer(doc, q)) {
    const ok = h.matchStart >= 0 && h.matchStart + h.matchLength <= h.snippet.length;
    if (!ok) { failures++; console.log("  FAIL offsets q=" + q + " " + JSON.stringify(h)); }
  }
}
check("offsets always inside the snippet", true);

console.log(failures === 0 ? "\nALL PASSED" : "\n" + failures + " FAILED");
process.exit(failures === 0 ? 0 : 1);
