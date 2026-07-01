"use client";
import { AnimatePresence, m } from "framer-motion";
import { ArrowLeft, Lock } from "lucide-react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useCallback, useEffect, useState } from "react";
import {
  getDocument,
  getExplorer,
  type Doc,
  type ExplorerDoc,
} from "@/lib/api";
import { AnalysisProgress } from "@/components/AnalysisProgress";
import { DocTypeBadge } from "@/components/DocTypeBadge";
import DownloadReportButton from "@/components/DownloadReportButton";
import { ClauseCard, type ReadingMode } from "@/components/explorer/ClauseCard";
import { ExplorerNav } from "@/components/explorer/ExplorerNav";
import { FinancialView } from "@/components/explorer/FinancialView";
import { GuidedWalkthrough } from "@/components/explorer/GuidedWalkthrough";
import { OverviewView } from "@/components/explorer/OverviewView";
import { QuestionsView } from "@/components/explorer/QuestionsView";
import { SectionView } from "@/components/explorer/SectionView";
import { TimelineView } from "@/components/explorer/TimelineView";
import { Container, Surface } from "@/components/ui/Surface";
import { TopBar } from "@/components/ui/TopBar";

const TERMINAL = new Set(["report_ready", "failed"]);

export default function DocumentDetail() {
  const router = useRouter();
  const { id } = useParams<{ id: string }>();
  const docId = Number(id);

  const [doc, setDoc] = useState<Doc | null>(null);
  const [explorer, setExplorer] = useState<ExplorerDoc | null>(null);
  const [active, setActive] = useState("overview");
  const [mode, setMode] = useState<ReadingMode>("consumer");
  const [walkthrough, setWalkthrough] = useState(false);

  const loadExplorer = useCallback(async () => {
    const e = await getExplorer(docId);
    if (e) setExplorer(e);
  }, [docId]);

  useEffect(() => {
    document.title = doc
      ? `${doc.original_filename} — ClearClause`
      : "Document — ClearClause";
  }, [doc?.original_filename]);

  useEffect(() => {
    getDocument(docId)
      .then(async (d) => {
        setDoc(d);
        if (d.status === "report_ready") await loadExplorer();
      })
      .catch(() => router.push("/dashboard"));
  }, [router, docId, loadExplorer]);

  useEffect(() => {
    if (!doc || TERMINAL.has(doc.status)) return;
    // Backoff: 2.5 → 3.5 → 5 → 7.5 → 10s cap
    const DELAYS = [2500, 3500, 5000, 7500, 10000];
    let tick = 0;
    let id: ReturnType<typeof setTimeout>;
    const poll = async () => {
      const d = await getDocument(docId);
      setDoc(d);
      if (d.status === "report_ready") { await loadExplorer(); return; }
      if (!TERMINAL.has(d.status)) {
        id = setTimeout(poll, DELAYS[Math.min(tick++, DELAYS.length - 1)]);
      }
    };
    id = setTimeout(poll, DELAYS[0]);
    return () => clearTimeout(id);
  }, [doc?.status, docId, loadExplorer]);

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
            <p className="t-caption mb-7">This usually takes a few seconds. You don't need to do anything.</p>
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
              <AnimatePresence mode="wait">
                <ContentPane
                  key={active}
                  active={active}
                  explorer={explorer}
                  mode={mode}
                  docId={docId}
                  qaReady={!!doc.qa_ready}
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
  onSection,
}: {
  active: string;
  explorer: ExplorerDoc;
  mode: ReadingMode;
  docId: number;
  qaReady: boolean;
  onSection: (id: string) => void;
}) {
  if (active === "overview")  return <OverviewView explorer={explorer} onSection={onSection} />;
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
        <h2 className="mb-4 text-[1.375rem] font-bold tracking-tight">What's in Your Favour</h2>
        <ul className="space-y-3">
          {explorer.strengths.map((s, i) => (
            <li key={i} className="flex items-start gap-3 rounded-xl border border-[#16a34a]/20 bg-[#f0fdf4] px-4 py-3 text-[0.9375rem] leading-relaxed">
              <span className="mt-0.5 shrink-0 text-[#16a34a]">✓</span>
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
