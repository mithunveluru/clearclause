"use client";
import { AnimatePresence, m } from "framer-motion";
import { AlertTriangle, ArrowLeft, CheckCircle, Lock } from "lucide-react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useCallback, useEffect, useState } from "react";
import {
  getAiSummary,
  getDocument,
  getExplorer,
  type AISummary,
  type Doc,
  type ExplorerDoc,
} from "@/lib/api";
import { AISummaryPanel } from "@/components/AISummaryPanel";
import { AnalysisProgress } from "@/components/AnalysisProgress";
import { DocTypeBadge } from "@/components/DocTypeBadge";
import DownloadReportButton from "@/components/DownloadReportButton";
import { type ReadingMode } from "@/components/explorer/ClauseCard";
import { ExplorerNav } from "@/components/explorer/ExplorerNav";
import { FinancialView } from "@/components/explorer/FinancialView";
import { GuidedWalkthrough } from "@/components/explorer/GuidedWalkthrough";
import { OverviewView } from "@/components/explorer/OverviewView";
import { QuestionsView } from "@/components/explorer/QuestionsView";
import { SectionView } from "@/components/explorer/SectionView";
import { TimelineView } from "@/components/explorer/TimelineView";
import { Container, Surface } from "@/components/ui/Surface";
import { TopBar } from "@/components/ui/TopBar";

// Q&A lags report_ready by the embed stage
const fullyReady = (d: Doc) =>
  d.status === "failed" || (d.status === "report_ready" && d.qa_ready);

// A garbled scan yields few clauses, which reads as "nothing risky here". Say so
// instead. null means the text came from the PDF's own text layer — nothing to doubt.
const isLowConfidenceScan = (d: Doc) =>
  d.ocr_confidence !== null && d.ocr_confidence < 60;

export default function DocumentDetail() {
  const router = useRouter();
  const { id } = useParams<{ id: string }>();
  const docId = Number(id);

  const [doc, setDoc] = useState<Doc | null>(null);
  const [explorer, setExplorer] = useState<ExplorerDoc | null>(null);
  const [aiSummary, setAiSummary] = useState<AISummary | null>(null);
  const [active, setActive] = useState("overview");
  const [mode, setMode] = useState<ReadingMode>("consumer");
  const [walkthrough, setWalkthrough] = useState(false);

  const loadExplorer = useCallback(async () => {
    const e = await getExplorer(docId);
    if (e) setExplorer(e);
  }, [docId]);

  // Only produced when AI_MODE is summary_only or full; absent otherwise.
  useEffect(() => {
    if (doc?.ai_summary_ready && !aiSummary) getAiSummary(docId).then(setAiSummary).catch(() => {});
  }, [doc?.ai_summary_ready, aiSummary, docId]);

  useEffect(() => {
    document.title = doc
      ? `${doc.original_filename} — ClearClause`
      : "Document — ClearClause";
  }, [doc?.original_filename]);

  useEffect(() => {
    getDocument(docId).then(setDoc).catch(() => router.push("/dashboard"));
  }, [router, docId]);

  useEffect(() => {
    if (doc?.status === "report_ready" && !explorer) loadExplorer();
  }, [doc?.status, explorer, loadExplorer]);

  useEffect(() => {
    if (!doc || fullyReady(doc)) return;
    // Backoff: 2.5 → 3.5 → 5 → 7.5 → 10s cap
    const DELAYS = [2500, 3500, 5000, 7500, 10000];
    let tick = 0;
    let afterReport = 0;
    let id: ReturnType<typeof setTimeout>;
    const poll = async () => {
      const d = await getDocument(docId);
      setDoc(d);
      if (fullyReady(d)) return;
      // Stop if embeddings never arrive
      if (d.status === "report_ready" && ++afterReport > 12) return;
      id = setTimeout(poll, DELAYS[Math.min(tick++, DELAYS.length - 1)]);
    };
    id = setTimeout(poll, DELAYS[0]);
    return () => clearTimeout(id);
  }, [doc?.status, doc?.qa_ready, docId]);

  if (!doc) {
    return (
      <>
        <TopBar />
        <Container className="py-24 text-center"><p className="t-body">Loading…</p></Container>
      </>
    );
  }

  const ready = doc.status === "report_ready";

  return (
    <>
      <TopBar
        right={
          <Link
            href="/dashboard"
            className="inline-flex items-center gap-1.5 text-[0.875rem] font-medium text-ink-2 hover:text-ink"
          >
            <ArrowLeft className="h-4 w-4" strokeWidth={1.75} />
            Workspace
          </Link>
        }
      />

      {!ready && (
        <Container className="py-12">
          <div className="flex items-center gap-3">
            <p className="eyebrow">Document review</p>
            {doc.classified_type && <DocTypeBadge type={doc.classified_type} />}
          </div>
          <h1 className="t-headline mt-2.5 break-words">{doc.original_filename}</h1>
          <Surface className="mt-10 max-w-xl px-8 py-9">
            <h2 className="t-section mb-1">Analyzing your document</h2>
            <p className="t-caption mb-7">This usually takes a few seconds. You don&apos;t need to do anything.</p>
            <AnalysisProgress status={doc.status} />
            <p className="mt-8 flex items-center gap-1.5 text-[0.75rem] text-ink-3">
              <Lock className="h-3 w-3" strokeWidth={2} />
              Processed privately · only the extracted text is analyzed
            </p>
          </Surface>
        </Container>
      )}

      {ready && explorer && (
        <m.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.4, ease: [0.22, 1, 0.36, 1] }}
          className="flex min-h-[calc(100vh-56px)]"
        >
          <aside className="hidden w-64 shrink-0 border-r border-line bg-surface lg:block xl:w-72">
            <div className="sticky top-14 max-h-[calc(100vh-56px)] overflow-y-auto px-4">
              <ExplorerNav
                explorer={explorer}
                active={active}
                onSelect={setActive}
                mode={mode}
                onMode={setMode}
                onWalkthrough={() => setWalkthrough(true)}
              />
            </div>
          </aside>

          <main className="flex-1 min-w-0">
            <div className="sticky top-14 z-20 border-b border-line bg-surface/95 backdrop-blur-md">
              <div className="px-6 py-3.5 flex items-center justify-between gap-4">
                <div className="min-w-0">
                  <p className="truncate font-semibold text-[0.9375rem] leading-snug">
                    {doc.original_filename}
                  </p>
                  {doc.classified_type && (
                    <DocTypeBadge type={doc.classified_type} />
                  )}
                </div>
                <div className="shrink-0">
                  <DownloadReportButton docId={docId} />
                </div>
              </div>

              <MobileNav explorer={explorer} active={active} onSelect={setActive} />
            </div>

            <div className="mx-auto max-w-3xl px-6 py-10">
              {isLowConfidenceScan(doc) && (
                <div
                  role="status"
                  className="mb-8 flex items-start gap-3 rounded-xl border border-[#f59e0b]/30 bg-[#fffbeb] px-4 py-3"
                >
                  <AlertTriangle
                    className="mt-0.5 h-4 w-4 shrink-0 text-[#b45309]"
                    strokeWidth={2}
                    aria-hidden
                  />
                  <p className="text-[0.9375rem] leading-relaxed text-[#78350f]">
                    <span className="font-medium">This scan was hard to read.</span>{" "}
                    Some text may have been missed, so this review could be incomplete —
                    a clearer scan or the original PDF will give a more reliable result.
                  </p>
                </div>
              )}

              <AnimatePresence mode="wait">
                <ContentPane
                  key={active}
                  active={active}
                  explorer={explorer}
                  mode={mode}
                  docId={docId}
                  qaReady={!!doc.qa_ready}
                  aiSummary={active === "overview" ? aiSummary : null}
                  onSection={setActive}
                />
              </AnimatePresence>
            </div>
          </main>
        </m.div>
      )}

      {ready && !explorer && (
        <Container className="py-24 text-center">
          <p className="t-body text-ink-3">Building explorer…</p>
        </Container>
      )}

      <AnimatePresence>
        {walkthrough && explorer && (
          <GuidedWalkthrough
            steps={explorer.walkthrough}
            onClose={() => setWalkthrough(false)}
            onGo={(sid) => { setActive(sid); setWalkthrough(false); }}
          />
        )}
      </AnimatePresence>
    </>
  );
}

function ContentPane({
  active,
  explorer,
  mode,
  docId,
  qaReady,
  aiSummary,
  onSection,
}: {
  active: string;
  explorer: ExplorerDoc;
  mode: ReadingMode;
  docId: number;
  qaReady: boolean;
  aiSummary: AISummary | null;
  onSection: (id: string) => void;
}) {
  if (active === "overview") {
    return (
      <>
        <OverviewView explorer={explorer} onSection={onSection} />
        {aiSummary && <AISummaryPanel summary={aiSummary} />}
      </>
    );
  }
  if (active === "financial") return <FinancialView impact={explorer.financial_impact} />;
  if (active === "timeline")  return <TimelineView events={explorer.timeline} />;
  if (active === "questions" || active === "qa") {
    return (
      <QuestionsView
        docId={docId}
        questions={explorer.suggested_questions}
        qaReady={qaReady}
      />
    );
  }
  if (active === "strengths") {
    return (
      <m.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.3 }}>
        <h2 className="mb-4 text-[1.375rem] font-bold tracking-tight">What&apos;s in Your Favour</h2>
        <ul className="space-y-3">
          {explorer.strengths.map((s, i) => (
            <li key={i} className="flex items-start gap-3 rounded-xl border border-[#15803d]/20 bg-[#f0fdf4] px-4 py-3 text-[0.9375rem] leading-relaxed">
              <CheckCircle className="mt-0.5 h-4 w-4 shrink-0 text-[#15803d]" strokeWidth={2} />
              {s}
            </li>
          ))}
        </ul>
      </m.div>
    );
  }

  const section = explorer.sections.find((s) => s.id === active);
  if (section) return <SectionView section={section} mode={mode} />;

  return <OverviewView explorer={explorer} onSection={onSection} />;
}

function MobileNav({
  explorer,
  active,
  onSelect,
}: {
  explorer: ExplorerDoc;
  active: string;
  onSelect: (id: string) => void;
}) {
  const items = [
    { id: "overview",  label: "Overview" },
    { id: "financial", label: "Financial" },
    { id: "questions", label: "Questions" },
    ...(explorer.timeline?.length ? [{ id: "timeline", label: "Timeline" }] : []),
    ...(explorer.strengths?.length ? [{ id: "strengths", label: "Strengths" }] : []),
    ...explorer.sections.map((s) => ({ id: s.id, label: s.label })),
  ];

  return (
    <nav
      aria-label="Document sections"
      className="lg:hidden flex gap-1.5 overflow-x-auto px-4 pb-2.5 scrollbar-none"
    >
      {items.map(({ id, label }) => (
        <button
          key={id}
          onClick={() => onSelect(id)}
          className={`shrink-0 rounded-lg px-3 py-1.5 text-[0.8125rem] font-medium transition whitespace-nowrap ${
            active === id
              ? "bg-brand text-white"
              : "bg-canvas text-ink-2 hover:text-ink"
          }`}
        >
          {label}
        </button>
      ))}
    </nav>
  );
}
