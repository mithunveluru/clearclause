"use client";
import { Download } from "lucide-react";
import { useState } from "react";
import { fetchReportBlob } from "@/lib/api";
import { Button } from "@/components/ui/Button";

export default function DownloadReportButton({ docId }: { docId: number }) {
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState("");
  async function open() {
    setBusy(true);
    setErr("");
    try {
      const blob = await fetchReportBlob(docId);
      const url = URL.createObjectURL(blob);
      window.open(url, "_blank");
      setTimeout(() => URL.revokeObjectURL(url), 60_000);
    } catch (e) {
      setErr((e as Error).message || "The report couldn't be generated.");
    } finally {
      setBusy(false);
    }
  }
  return (
    <span className="relative inline-flex">
      <Button variant="secondary" onClick={open} disabled={busy} aria-describedby={err ? `report-err-${docId}` : undefined}>
        <Download className="h-4 w-4" strokeWidth={1.75} aria-hidden />
        <span className="hidden sm:inline">{busy ? "Preparing…" : "PDF report"}</span>
        <span className="sm:hidden">{busy ? "…" : "Report"}</span>
      </Button>
      {err && (
        <span
          id={`report-err-${docId}`}
          role="alert"
          className="absolute right-0 top-full z-30 mt-2 w-64 rounded-lg border border-risk-high/25 bg-surface px-3 py-2 text-[0.8125rem] text-risk-high shadow-raised"
        >
          Report failed: {err}. Try again in a moment.
        </span>
      )}
    </span>
  );
}
