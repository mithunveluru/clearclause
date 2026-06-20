"use client";
import { FileText } from "lucide-react";
import { useState } from "react";
import { fetchReportBlob } from "@/lib/api";
import { Button } from "@/components/ui/Button";

export default function DownloadReportButton({ docId }: { docId: number }) {
  const [busy, setBusy] = useState(false);
  async function open() {
    setBusy(true);
    try {
      const blob = await fetchReportBlob(docId);
      const url = URL.createObjectURL(blob);
      window.open(url, "_blank");
      setTimeout(() => URL.revokeObjectURL(url), 60_000);
    } finally {
      setBusy(false);
    }
  }
  return (
    <Button variant="secondary" onClick={open} disabled={busy}>
      <FileText className="h-4 w-4" strokeWidth={1.75} />
      {busy ? "Preparing…" : "Download PDF report"}
    </Button>
  );
}
