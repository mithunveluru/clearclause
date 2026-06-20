"use client";
import { fetchReportBlob } from "@/lib/api";

export default function DownloadReportButton({ docId }: { docId: number }) {
  async function open() {
    const blob = await fetchReportBlob(docId);
    const url = URL.createObjectURL(blob);
    window.open(url, "_blank");
    setTimeout(() => URL.revokeObjectURL(url), 60_000);
  }
  return (
    <button
      onClick={open}
      className="rounded-lg bg-gray-900 px-4 py-2 font-medium text-white hover:bg-gray-700"
    >
      Open report
    </button>
  );
}
