"use client";
import { motion } from "framer-motion";
import { AlertTriangle, ArrowLeft, Lock } from "lucide-react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useCallback, useEffect, useState } from "react";
import {
  getDocument,
  getFindings,
  getScore,
  getToken,
  type Doc,
  type Finding,
  type Score,
} from "@/lib/api";
import { AnalysisProgress } from "@/components/AnalysisProgress";
import { CategoryBreakdown } from "@/components/CategoryBreakdown";
import { ClauseInspectionPanel } from "@/components/ClauseInspectionPanel";
import { CostBreakdown } from "@/components/CostBreakdown";
import DownloadReportButton from "@/components/DownloadReportButton";
import { FindingsTimeline } from "@/components/FindingsTimeline";
import { RiskMeter } from "@/components/RiskMeter";
import { Container, Surface } from "@/components/ui/Surface";
import { TopBar } from "@/components/ui/TopBar";
import { bandMeta } from "@/lib/ui";

const TERMINAL = new Set(["report_ready", "failed"]);

export default function DocumentDetail() {
  const router = useRouter();
  const { id } = useParams<{ id: string }>();
  const docId = Number(id);

  const [doc, setDoc] = useState<Doc | null>(null);
  const [findings, setFindings] = useState<Finding[]>([]);
  const [score, setScore] = useState<Score | null>(null);
  const [inspect, setInspect] = useState<Finding | null>(null);

  const loadResults = useCallback(async () => {
    setScore(await getScore(docId));
    setFindings(await getFindings(docId));
  }, [docId]);

  // Initial load
  useEffect(() => {
    if (!getToken()) {
      router.push("/login");
      return;
    }
    getDocument(docId)
      .then(async (d) => {
        setDoc(d);
        if (d.status === "report_ready") await loadResults();
      })
      .catch(() => router.push("/dashboard"));
  }, [router, docId, loadResults]);

  // Auto-poll while processing (analysis was enqueued automatically on upload)
  useEffect(() => {
    if (!doc || TERMINAL.has(doc.status)) return;
    const id = setInterval(async () => {
      const d = await getDocument(docId);
      setDoc(d);
      if (d.status === "report_ready") await loadResults();
    }, 2500);
    return () => clearInterval(id);
  }, [doc, docId, loadResults]);

  if (!doc) {
    return (
      <>
        <TopBar />
        <Container className="py-24 text-center">
          <p className="t-body">Loading…</p>
        </Container>
      </>
    );
  }

  const ready = doc.status === "report_ready";
  const highRisk = score && (score.band === "High" || score.band === "Critical");

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

      <Container className="py-12">
        <p className="eyebrow">Document review</p>
        <h1 className="t-headline mt-2.5 break-words">{doc.original_filename}</h1>

        {!ready && (
          <Surface className="mt-10 max-w-xl px-8 py-9">
            <h2 className="t-section mb-1">Analyzing your document</h2>
            <p className="t-caption mb-7">
              This usually takes a few seconds. You don’t need to do anything.
            </p>
            <AnalysisProgress status={doc.status} />
            <p className="mt-8 flex items-center gap-1.5 text-[0.75rem] text-ink-3">
              <Lock className="h-3 w-3" strokeWidth={2} />
              Processed privately · only the extracted text is analyzed
            </p>
          </Surface>
        )}

        {ready && score && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
          >
            {highRisk && (
              <div
                className="mt-8 flex items-center gap-3 rounded-xl border px-4 py-3.5 text-[0.9375rem] font-medium"
                style={{
                  color: bandMeta(score.band).color,
                  backgroundColor: bandMeta(score.band).tint,
                  borderColor: `${bandMeta(score.band).color}26`,
                }}
              >
                <AlertTriangle className="h-[18px] w-[18px] shrink-0" strokeWidth={2} />
                High-risk terms detected — review these carefully before you agree.
              </div>
            )}

            <Surface className="mt-8 flex flex-col gap-8 px-8 py-8 md:flex-row md:items-center md:justify-between">
              <div className="max-w-md">
                <RiskMeter total={score.total_score} band={score.band} />
                <p className="t-body mt-5 text-[1rem]">{score.summary}</p>
              </div>
              <DownloadReportButton docId={docId} />
            </Surface>

            <div className="mt-8 grid grid-cols-1 gap-8 lg:grid-cols-[1fr_320px]">
              <Surface className="px-8 py-8">
                <h2 className="t-section mb-1">Findings</h2>
                <p className="t-caption mb-7">
                  {findings.length} issue{findings.length === 1 ? "" : "s"} found across the agreement
                </p>
                <FindingsTimeline findings={findings} onInspect={setInspect} />
              </Surface>

              <div className="space-y-8">
                <Surface className="px-7 py-7">
                  <h3 className="t-section mb-6">True cost</h3>
                  <CostBreakdown cost={score.cost} />
                </Surface>
                <Surface className="px-7 py-7">
                  <h3 className="t-section mb-6">Risk by category</h3>
                  <CategoryBreakdown breakdown={score.breakdown} />
                </Surface>
              </div>
            </div>
          </motion.div>
        )}
      </Container>

      <ClauseInspectionPanel finding={inspect} onClose={() => setInspect(null)} />
    </>
  );
}
