"use client";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useCallback, useEffect, useState } from "react";
import ClauseDrawer from "@/components/ClauseDrawer";
import DownloadReportButton from "@/components/DownloadReportButton";
import FindingCard from "@/components/FindingCard";
import RiskBadge from "@/components/RiskBadge";
import Stepper from "@/components/Stepper";
import TrueCostCard from "@/components/TrueCostCard";
import {
  analyzeDocument,
  getDocument,
  getFindings,
  getScore,
  getToken,
  type Doc,
  type Finding,
  type Score,
} from "@/lib/api";

export default function DocumentDetail() {
  const router = useRouter();
  const { id } = useParams<{ id: string }>();
  const docId = Number(id);

  const [doc, setDoc] = useState<Doc | null>(null);
  const [findings, setFindings] = useState<Finding[]>([]);
  const [score, setScore] = useState<Score | null>(null);
  const [drawer, setDrawer] = useState<Finding | null>(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [err, setErr] = useState("");

  const load = useCallback(async () => {
    const d = await getDocument(docId);
    setDoc(d);
    if (d.status === "report_ready") {
      setScore(await getScore(docId));
      setFindings(await getFindings(docId));
    }
  }, [docId]);

  useEffect(() => {
    if (!getToken()) {
      router.push("/login");
      return;
    }
    load().catch(() => router.push("/dashboard"));
  }, [router, load]);

  async function runAnalyze() {
    setErr("");
    setAnalyzing(true);
    try {
      await analyzeDocument(docId); // enqueues, returns immediately
      for (let i = 0; i < 60; i++) {
        await new Promise((r) => setTimeout(r, 2000));
        const d = await getDocument(docId);
        setDoc(d);
        if (d.status === "report_ready") {
          setScore(await getScore(docId));
          setFindings(await getFindings(docId));
          return;
        }
        if (d.status === "failed") {
          setErr("Analysis failed. Please try again.");
          return;
        }
      }
      setErr("Analysis is taking longer than expected. Refresh to check again.");
    } catch (e) {
      setErr((e as Error).message);
    } finally {
      setAnalyzing(false);
    }
  }

  if (!doc) return <main className="p-12 text-gray-500">Loading…</main>;
  const ready = doc.status === "report_ready";

  return (
    <main className="mx-auto max-w-3xl px-6 py-12">
      <Link href="/dashboard" className="text-sm text-blue-600">
        ← Back
      </Link>
      <h1 className="mt-2 text-2xl font-bold">{doc.original_filename}</h1>

      <div className="my-6">
        <Stepper status={doc.status} />
      </div>

      {!ready && (
        <div className="rounded-xl border bg-white p-6">
          <p className="mb-4 text-gray-600">
            This document hasn’t been analyzed yet.
          </p>
          <button
            onClick={runAnalyze}
            disabled={analyzing}
            className="rounded-lg bg-blue-600 px-5 py-2.5 font-medium text-white hover:bg-blue-700 disabled:opacity-50"
          >
            {analyzing ? "Analyzing… (this can take a few seconds)" : "Analyze document"}
          </button>
          {err && <p className="mt-3 text-sm text-red-600">{err}</p>}
        </div>
      )}

      {ready && score && (
        <>
          <div className="flex flex-wrap items-center justify-between gap-4 rounded-xl border bg-white p-5">
            <div>
              <RiskBadge total={score.total_score} band={score.band} />
              <p className="mt-2 max-w-md text-gray-700">{score.summary}</p>
            </div>
            <DownloadReportButton docId={docId} />
          </div>

          <div className="mt-6">
            <TrueCostCard cost={score.cost} />
          </div>

          <h2 className="mb-3 mt-8 text-lg font-semibold">
            Findings ({findings.length})
          </h2>
          <div className="flex flex-col gap-3">
            {findings.map((f) => (
              <FindingCard key={f.id} f={f} onOpen={setDrawer} />
            ))}
          </div>
        </>
      )}

      <ClauseDrawer finding={drawer} onClose={() => setDrawer(null)} />
    </main>
  );
}
