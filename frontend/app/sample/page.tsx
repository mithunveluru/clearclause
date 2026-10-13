"use client";
import { AnimatePresence } from "framer-motion";
import { CheckCircle, HelpCircle } from "lucide-react";
import { useState } from "react";
import { SAMPLE } from "@/lib/sample";
import { type ReadingMode } from "@/components/explorer/ClauseCard";
import { ExplorerNav } from "@/components/explorer/ExplorerNav";
import { FinancialView } from "@/components/explorer/FinancialView";
import { GuidedWalkthrough } from "@/components/explorer/GuidedWalkthrough";
import { OverviewView } from "@/components/explorer/OverviewView";
import { SearchView } from "@/components/explorer/SearchView";
import { SectionView } from "@/components/explorer/SectionView";
import { TimelineView } from "@/components/explorer/TimelineView";
import { ButtonLink } from "@/components/ui/Button";
import { searchExplorer } from "@/lib/search";
import { SiteHeader } from "@/components/SiteChrome";

export default function SamplePage() {
  const [active, setActive] = useState("overview");
  const [mode, setMode] = useState<ReadingMode>("consumer");
  const [walkthrough, setWalkthrough] = useState(false);
  const [query, setQuery] = useState("");

  return (
    <>
      <SiteHeader />
      <div>
        <div className="flex min-h-[calc(100vh-64px)]">
          <aside className="hidden w-64 shrink-0 border-r border-line bg-canvas lg:block xl:w-72">
            <div className="sticky top-16 max-h-[calc(100vh-64px)] overflow-y-auto px-4">
              <ExplorerNav
                explorer={SAMPLE}
                active={active}
                onSelect={setActive}
                mode={mode}
                onMode={setMode}
                onWalkthrough={() => setWalkthrough(true)}
                query={query}
                onQuery={setQuery}
              />
            </div>
          </aside>

          <main className="min-w-0 flex-1">
            <div className="sticky top-16 z-20 border-b border-line bg-surface/95 backdrop-blur-md">
              <div className="flex items-center justify-between gap-4 px-6 py-3.5">
                <div className="min-w-0">
                  {/* Same fix as the real explorer: without an h1 the views started at h2 */}
                  <h1 className="truncate text-[0.9375rem] font-semibold leading-snug">
                    Personal Loan Agreement.pdf
                  </h1>
                  <p className="t-caption">Sample document · findings shown for illustration</p>
                </div>
                <ButtonLink href="/register" variant="primary" className="shrink-0">
                  Analyze your own
                </ButtonLink>
              </div>

              <nav
                aria-label="Document sections"
                className="lg:hidden flex gap-1.5 overflow-x-auto px-4 pb-2.5 scrollbar-none"
              >
                {[
                  { id: "overview", label: "Overview" },
                  { id: "financial", label: "Financial" },
                  { id: "timeline", label: "Timeline" },
                  { id: "questions", label: "Questions" },
                  ...SAMPLE.sections.map((s) => ({ id: s.id, label: s.label })),
                ].map(({ id, label }) => (
                  <button
                    key={id}
                    onClick={() => setActive(id)}
                    className={`shrink-0 rounded-lg px-3 py-1.5 text-[0.8125rem] font-medium transition whitespace-nowrap ${
                      active === id ? "bg-ink text-white" : "bg-sunken text-ink-2 hover:text-ink"
                    }`}
                  >
                    {label}
                  </button>
                ))}
              </nav>
            </div>

            <div className="mx-auto max-w-3xl px-6 py-10">
              <AnimatePresence mode="wait">
                {query.trim() ? (
                  <SearchView
                    key="search"
                    query={query.trim()}
                    hits={searchExplorer(SAMPLE, query)}
                    onSelect={(sectionId) => {
                      setQuery("");
                      setActive(sectionId);
                    }}
                  />
                ) : (
                  <SamplePane key={active} active={active} mode={mode} onSection={setActive} />
                )}
              </AnimatePresence>
            </div>
          </main>
        </div>
      </div>

      <AnimatePresence>
        {walkthrough && (
          <GuidedWalkthrough
            steps={SAMPLE.walkthrough}
            onClose={() => setWalkthrough(false)}
            onGo={(sid) => {
              setActive(sid);
              setWalkthrough(false);
            }}
          />
        )}
      </AnimatePresence>
    </>
  );
}

function SamplePane({
  active,
  mode,
  onSection,
}: {
  active: string;
  mode: ReadingMode;
  onSection: (id: string) => void;
}) {
  if (active === "financial") return <FinancialView impact={SAMPLE.financial_impact} />;
  if (active === "timeline") return <TimelineView events={SAMPLE.timeline} />;
  if (active === "strengths") {
    return (
      <div>
        <h2 className="mb-4 text-[1.375rem] font-semibold tracking-tight">In your favour</h2>
        <ul className="space-y-3">
          {SAMPLE.strengths.map((s, i) => (
            <li
              key={i}
              className="flex items-start gap-3 rounded-xl border border-risk-low/20 bg-risk-low-tint px-4 py-3 text-[0.9375rem] leading-relaxed"
            >
              <CheckCircle className="mt-0.5 h-4 w-4 shrink-0 text-risk-low" strokeWidth={2} />
              {s}
            </li>
          ))}
        </ul>
      </div>
    );
  }
  if (active === "questions" || active === "qa") {
    // No live Q&A here; show the detected questions
    return (
      <div>
        <h2 className="mb-1 text-[1.375rem] font-semibold tracking-tight">Questions to Ask</h2>
        <p className="t-body mb-6 text-ink-2">
          Detected from this document. In a full analysis you can ask your own — every answer
          cites the page and clause it came from.
        </p>
        <div className="space-y-2">
          {SAMPLE.suggested_questions.map((q, i) => (
            <div
              key={i}
              className="flex items-start gap-3 rounded-xl border border-line bg-surface px-4 py-3.5"
            >
              <HelpCircle className="mt-0.5 h-4 w-4 shrink-0 text-brand" strokeWidth={1.75} />
              <span className="text-[0.9375rem] leading-relaxed">{q.question}</span>
            </div>
          ))}
        </div>
        <div className="mt-8">
          <ButtonLink href="/register" variant="secondary">
            Create an account to ask your own
          </ButtonLink>
        </div>
      </div>
    );
  }

  const section = SAMPLE.sections.find((s) => s.id === active);
  if (section) return <SectionView section={section} mode={mode} />;

  return <OverviewView explorer={SAMPLE} onSection={onSection} />;
}
