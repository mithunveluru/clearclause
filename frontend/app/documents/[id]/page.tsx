"use client";
import { AnimatePresence, m } from "framer-motion";
import { AlertTriangle, CheckCircle, Compass, FileText, Lock, RotateCcw, Search } from "lucide-react";
import { useParams, useRouter, useSearchParams } from "next/navigation";
import { useCallback, useEffect, useState } from "react";
import {
  documentFileUrl,
  getAiSummary,
  getClassification,
  getDocument,
  getExplorer,
  type AISummary,
  type Classification,
  type Doc,
  type ExplorerDoc,
} from "@/lib/api";
import { AISummaryPanel } from "@/components/AISummaryPanel";
import { AnalysisProgress } from "@/components/AnalysisProgress";
import { AppShell } from "@/components/AppShell";
import { DocTypeBadge } from "@/components/DocTypeBadge";
import DownloadReportButton from "@/components/DownloadReportButton";
import { type ReadingMode } from "@/components/explorer/ClauseCard";
import { ExplorerNav } from "@/components/explorer/ExplorerNav";
import { FinancialView } from "@/components/explorer/FinancialView";
import { GuidedWalkthrough } from "@/components/explorer/GuidedWalkthrough";
import { OverviewView } from "@/components/explorer/OverviewView";
import { QuestionsView } from "@/components/explorer/QuestionsView";
import { SearchView } from "@/components/explorer/SearchView";
import { SectionView } from "@/components/explorer/SectionView";
import { TimelineView } from "@/components/explorer/TimelineView";
import { viewTransition, easeSmooth } from "@/components/ui/motion";
import { searchExplorer } from "@/lib/search";
import { Button, ButtonLink } from "@/components/ui/Button";
import { Skeleton } from "@/components/ui/Skeleton";

// Q&A lags report_ready by the embed stage
const fullyReady = (d: Doc) =>
  d.status === "failed" || (d.status === "report_ready" && d.qa_ready);

// A bad scan reads as "no risks found"
const isLowConfidenceScan = (d: Doc) =>
  d.ocr_confidence !== null && d.ocr_confidence < 60;

export default function DocumentDetail() {
  const router = useRouter();
  const { id } = useParams<{ id: string }>();
  const docId = Number(id);

  const [doc, setDoc] = useState<Doc | null>(null);
  const [explorer, setExplorer] = useState<ExplorerDoc | null>(null);
  const [aiSummary, setAiSummary] = useState<AISummary | null>(null);
  const [classification, setClassification] = useState<Classification | null>(null);
  const [loadErr, setLoadErr] = useState("");
  const [explorerFailed, setExplorerFailed] = useState(false);
  const [mode, setMode] = useState<ReadingMode>("consumer");
  const [walkthrough, setWalkthrough] = useState(false);
  // Transient, not a navigable location
  const [query, setQuery] = useState("");

  // Section in the URL keeps Back refresh and links working
  const params = useSearchParams();
  const active = params.get("section") || "overview";
  const setActive = useCallback(
    (id: string) => {
      const qs = id === "overview" ? "" : `?section=${encodeURIComponent(id)}`;
      router.push(`/documents/${docId}${qs}`, { scroll: false });
    },
    [router, docId]
  );

  const loadExplorer = useCallback(async () => {
    setExplorerFailed(false);
    const e = await getExplorer(docId);
    if (e) setExplorer(e);
    else setExplorerFailed(true);
  }, [docId]);

  // Only produced when AI_MODE is summary_only or full
  useEffect(() => {
    if (doc?.ai_summary_ready && !aiSummary) getAiSummary(docId).then(setAiSummary).catch(() => {});
  }, [doc?.ai_summary_ready, aiSummary, docId]);

  useEffect(() => {
    document.title = doc
      ? `${doc.original_filename} — ClearClause`
      : "Document — ClearClause";
  }, [doc?.original_filename]);

  useEffect(() => {
    getDocument(docId).then(setDoc).catch((e) => setLoadErr((e as Error).message));
  }, [docId]);

  useEffect(() => {
    if (doc?.status === "report_ready" && !explorer) loadExplorer();
  }, [doc?.status, explorer, loadExplorer]);

  // Weak classifier signal is surfaced, not presented as fact
  useEffect(() => {
    if (doc?.classified_type && !classification) getClassification(docId).then(setClassification);
  }, [doc?.classified_type, classification, docId]);

  useEffect(() => {
    if (!doc || fullyReady(doc)) return;
    // Backoff, capped at 10s
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

  const crumbs = [{ label: "Documents", href: "/dashboard" }, { label: doc?.original_filename ?? "Document" }];

  if (!doc) {
    return (
      <AppShell focus crumbs={crumbs}>
        {loadErr ? (
          <div className="mx-auto max-w-md px-6 py-24 text-center">
            <h1 className="text-[1.25rem] font-semibold tracking-tight">This document isn&rsquo;t available</h1>
            <p className="mt-2 text-[0.9375rem] text-ink-2">
              It may have been deleted, or removed after the seven-day retention period. ({loadErr})
            </p>
            <ButtonLink href="/dashboard" variant="secondary" className="mt-6">Back to documents</ButtonLink>
          </div>
        ) : (
          <div className="mx-auto max-w-3xl space-y-4 px-6 py-12" aria-busy="true" aria-label="Loading document">
            <Skeleton className="h-4 w-24" />
            <Skeleton className="h-7 w-2/3" />
            <Skeleton className="mt-8 h-40 w-full" />
          </div>
        )}
      </AppShell>
    );
  }

  const ready = doc.status === "report_ready";
  const uncertainType = classification && classification.routing_action !== "auto";
  const typeBadge = doc.classified_type && (
    <span className="inline-flex flex-wrap items-center gap-2">
      <DocTypeBadge type={doc.classified_type} />
      {uncertainType && (
        <span className="text-[0.75rem] text-ink-3" title="The document's wording only weakly matched this type">
          Type identified with low confidence
        </span>
      )}
    </span>
  );

  return (
    <AppShell
      focus
      crumbs={crumbs}
      actions={
        ready && (
          <>
            <a
              href={documentFileUrl(docId)}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex h-10 items-center gap-2 rounded-lg px-3 text-[0.875rem] font-medium text-ink-2 transition hover:bg-sunken hover:text-ink focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-brand/25"
            >
              <FileText className="h-4 w-4" strokeWidth={1.75} aria-hidden />
              <span className="hidden sm:inline">Original</span>
              <span className="sr-only"> document (opens in a new tab)</span>
            </a>
            <DownloadReportButton docId={docId} />
          </>
        )
      }
    >
      {!ready && (
        <div className="mx-auto max-w-2xl px-4 py-10 sm:px-6 sm:py-14">
          <p className="eyebrow">Document review</p>
          <h1 className="mt-2 break-words text-[1.5rem] font-semibold tracking-tight">{doc.original_filename}</h1>
          {typeBadge && <div className="mt-3">{typeBadge}</div>}
          <div className="mt-8 rounded-xl border border-line bg-surface px-6 py-7 sm:px-8">
            <h2 className="text-[1rem] font-semibold tracking-tight" aria-live="polite">
              {doc.status === "failed" ? "Analysis stopped" : "Analyzing your document"}
            </h2>
            <p className="mb-7 mt-1 text-[0.875rem] text-ink-3">
              {doc.status === "failed"
                ? "Nothing was saved from this run."
                : "This page updates as each step finishes. You can leave and come back."}
            </p>
            <AnalysisProgress
              docId={docId}
              status={doc.status}
              onRetried={() => setDoc((d) => (d ? { ...d, status: "uploaded" } : d))}
            />
            <p className="mt-8 flex items-center gap-1.5 text-[0.75rem] text-ink-3">
              <Lock className="h-3 w-3" strokeWidth={2} aria-hidden />
              Only the extracted text is analyzed · deleted after seven days
            </p>
          </div>
        </div>
      )}

      {ready && explorer && (
        <m.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.4, ease: easeSmooth }}
          className="flex min-h-[calc(100vh-56px)]"
        >
          <aside className="hidden w-64 shrink-0 border-r border-line bg-canvas lg:block xl:w-72">
            <div className="sticky top-14 max-h-[calc(100vh-56px)] overflow-y-auto px-4">
              <ExplorerNav
                explorer={explorer}
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

          <div className="min-w-0 flex-1">
            <div className="border-b border-line bg-surface">
              <div className="mx-auto max-w-3xl px-4 pb-4 pt-6 sm:px-6">
                {/* The document's own title. Without it the loaded explorer had no h1 and
                    every view opened at h2, so heading navigation started mid-hierarchy. */}
                <h1 className="break-words text-[1.25rem] font-semibold leading-snug tracking-tight">
                  {doc.original_filename}
                </h1>
                {typeBadge && <div className="mt-2">{typeBadge}</div>}
              </div>
            </div>

            <MobileNav
                explorer={explorer}
                active={active}
                onSelect={setActive}
                mode={mode}
                onMode={setMode}
                onWalkthrough={() => setWalkthrough(true)}
                query={query}
                onQuery={setQuery}
              />

            <div className="mx-auto max-w-3xl px-4 py-8 sm:px-6 sm:py-10">
              {isLowConfidenceScan(doc) && (
                <div
                  role="status"
                  className="mb-8 flex items-start gap-3 rounded-xl border border-risk-moderate/30 bg-risk-moderate-tint px-4 py-3"
                >
                  <AlertTriangle
                    className="mt-0.5 h-4 w-4 shrink-0 text-risk-moderate"
                    strokeWidth={2}
                    aria-hidden
                  />
                  <p className="text-[0.9375rem] leading-relaxed text-ink">
                    <span className="font-medium">This scan was hard to read.</span>{" "}
                    Some text may have been missed, so this review could be incomplete —
                    a clearer scan or the original PDF will give a more reliable result.
                  </p>
                </div>
              )}

              <AnimatePresence mode="wait">
                {query.trim() ? (
                  <SearchView
                    key="search"
                    query={query.trim()}
                    hits={searchExplorer(explorer, query)}
                    onSelect={(sectionId) => {
                      setQuery("");
                      setActive(sectionId);
                    }}
                  />
                ) : (
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
                )}
              </AnimatePresence>
            </div>
          </div>
        </m.div>
      )}

      {ready && !explorer && (
        <div className="mx-auto max-w-md px-6 py-24 text-center">
          {explorerFailed ? (
            <>
              <p className="text-[0.9375rem] font-medium">The findings couldn&rsquo;t be loaded</p>
              <p className="mt-1 text-[0.875rem] text-ink-2">The analysis finished, but loading its results failed.</p>
              <Button variant="secondary" className="mt-5" onClick={loadExplorer}>
                <RotateCcw className="h-4 w-4" strokeWidth={1.75} aria-hidden /> Try again
              </Button>
            </>
          ) : (
            <p className="text-[0.9375rem] text-ink-3" role="status">Loading findings…</p>
          )}
        </div>
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
    </AppShell>
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
      <m.div {...viewTransition}>
        <h2 className="mb-4 text-[1.375rem] font-semibold tracking-tight">In your favour</h2>
        <ul className="space-y-3">
          {explorer.strengths.map((s, i) => (
            <li key={i} className="flex items-start gap-3 rounded-xl border border-risk-low/20 bg-risk-low-tint px-4 py-3 text-[0.9375rem] leading-relaxed">
              <CheckCircle className="mt-0.5 h-4 w-4 shrink-0 text-risk-low" strokeWidth={2} />
              {s}
            </li>
          ))}
        </ul>
      </m.div>
    );
  }

  const section = explorer.sections.find((s) => s.id === active);
  if (section) return <SectionView section={section} mode={mode} docId={docId} />;

  return <OverviewView explorer={explorer} onSection={onSection} />;
}

const READING_MODES: ReadingMode[] = ["consumer", "professional", "negotiation", "financial"];

function MobileNav({
  explorer,
  active,
  onSelect,
  mode,
  onMode,
  onWalkthrough,
  query,
  onQuery,
}: {
  explorer: ExplorerDoc;
  active: string;
  onSelect: (id: string) => void;
  mode: ReadingMode;
  onMode: (m: ReadingMode) => void;
  onWalkthrough: () => void;
  query: string;
  onQuery: (q: string) => void;
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
    <div className="sticky top-14 z-10 border-b border-line bg-canvas/95 px-4 py-2.5 backdrop-blur-md lg:hidden">
      <div className="relative mb-2">
        <Search
          className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-ink-3"
          strokeWidth={1.75}
          aria-hidden
        />
        <input
          type="search"
          value={query}
          onChange={(e) => onQuery(e.target.value)}
          placeholder="Search this document"
          aria-label="Search this document"
          className="field h-10 pl-9 text-[0.875rem]"
        />
      </div>
      <div className="flex items-center gap-2">
      <nav
        aria-label="Document sections"
        className="flex min-w-0 flex-1 gap-1.5 overflow-x-auto scrollbar-none"
      >
        {items.map(({ id, label }) => (
          <button
            key={id}
            onClick={() => onSelect(id)}
            className={`shrink-0 rounded-lg px-3 py-1.5 text-[0.8125rem] font-medium transition whitespace-nowrap ${
              active === id
                ? "bg-ink text-white"
                : "bg-sunken text-ink-2 hover:text-ink"
            }`}
          >
            {label}
          </button>
        ))}
      </nav>
      <select
        aria-label="Reading mode"
        value={mode}
        onChange={(e) => onMode(e.target.value as ReadingMode)}
        className="h-8 shrink-0 rounded-lg border border-line bg-surface px-1.5 text-[0.8125rem] font-medium text-ink-2 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand/30"
      >
        {READING_MODES.map((id) => (
          <option key={id} value={id}>
            {id.charAt(0).toUpperCase() + id.slice(1)}
          </option>
        ))}
      </select>
      {explorer.walkthrough.length > 0 && (
        <button
          onClick={onWalkthrough}
          aria-label="Guided walkthrough"
          className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg border border-brand/20 bg-brand/5 text-brand transition hover:bg-brand/10"
        >
          <Compass className="h-4 w-4" strokeWidth={1.75} />
        </button>
      )}
      </div>
    </div>
  );
}
