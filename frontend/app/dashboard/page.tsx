"use client";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useCallback, useEffect, useState } from "react";
import UploadDropzone from "@/components/UploadDropzone";
import { clearToken, getToken, listDocuments, type Doc } from "@/lib/api";

const STATUS_LABEL: Record<string, string> = {
  uploaded: "Uploaded",
  ocr_processing: "Reading text…",
  ocr_done: "Read",
  analysis_processing: "Analyzing…",
  analysis_done: "Analyzed",
  report_ready: "Report ready",
  failed: "Failed",
};

export default function Dashboard() {
  const router = useRouter();
  const [docs, setDocs] = useState<Doc[]>([]);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(() => {
    listDocuments()
      .then(setDocs)
      .catch(() => router.push("/login"))
      .finally(() => setLoading(false));
  }, [router]);

  useEffect(() => {
    if (!getToken()) {
      router.push("/login");
      return;
    }
    refresh();
  }, [router, refresh]);

  return (
    <main className="mx-auto max-w-3xl px-6 py-12">
      <div className="mb-8 flex items-center justify-between">
        <h1 className="text-2xl font-bold">Your scans</h1>
        <button
          onClick={() => {
            clearToken();
            router.push("/login");
          }}
          className="text-sm text-gray-500 hover:text-gray-800"
        >
          Log out
        </button>
      </div>

      <UploadDropzone onUploaded={refresh} />

      <div className="mt-10 flex flex-col gap-2">
        {loading ? (
          <p className="text-gray-500">Loading…</p>
        ) : docs.length === 0 ? (
          <p className="text-gray-500">No scans yet. Upload a document to start.</p>
        ) : (
          docs.map((d) => (
            <Link
              key={d.id}
              href={`/documents/${d.id}`}
              className="flex items-center justify-between rounded-lg border bg-white px-4 py-3 hover:border-blue-400"
            >
              <span className="font-medium">{d.original_filename}</span>
              <span className="text-sm text-gray-500">
                {STATUS_LABEL[d.status] ?? d.status}
              </span>
            </Link>
          ))
        )}
      </div>
    </main>
  );
}
