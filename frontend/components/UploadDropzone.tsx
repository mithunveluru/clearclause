"use client";
import { AnimatePresence, m } from "framer-motion";
import { FileText, FileUp, X } from "lucide-react";
import { useRef, useState } from "react";
import { uploadDocument, type Doc } from "@/lib/api";
import { Button } from "@/components/ui/Button";
import { Notice } from "@/components/ui/Form";
import { easeSmooth } from "@/components/ui/motion";
import { ACCEPTED_EXTS as EXTS, MAX_UPLOAD_MB as MAX_MB, validateFile } from "@/lib/upload";

function fmtSize(b: number) {
  return b < 1024 * 1024 ? `${Math.max(1, Math.round(b / 1024))} KB` : `${(b / 1024 / 1024).toFixed(1)} MB`;
}

export default function UploadDropzone({ onUploaded }: { onUploaded: (doc: Doc) => void }) {
  const input = useRef<HTMLInputElement>(null);
  const [file, setFile] = useState<File | null>(null);
  const [busy, setBusy] = useState(false);
  const [drag, setDrag] = useState(false);
  const [err, setErr] = useState("");

  function pick(f: File | undefined) {
    if (!f || busy) return;
    const problem = validateFile(f);
    setErr(problem);
    setFile(problem ? null : f);
    if (input.current) input.current.value = "";
  }

  async function submit() {
    if (!file || busy) return; // guards double submission
    setErr("");
    setBusy(true);
    try {
      onUploaded(await uploadDocument(file));
    } catch (e) {
      const msg = (e as Error).message;
      setErr(msg === "Failed to fetch" ? "The upload didn't reach the server. Check your connection and try again." : msg);
      setBusy(false);
    }
  }

  return (
    <div>
      <AnimatePresence mode="wait" initial={false}>
        {file ? (
          <m.div
            key="file"
            initial={{ opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -4 }}
            transition={{ duration: 0.2, ease: easeSmooth }}
            className="rounded-xl border border-line-strong bg-surface p-4 sm:p-5"
          >
            <div className="flex items-center gap-3">
              <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-brand-soft text-brand">
                <FileText className="h-5 w-5" strokeWidth={1.75} aria-hidden />
              </span>
              <div className="min-w-0 flex-1">
                <p className="truncate text-[0.9375rem] font-medium">{file.name}</p>
                <p className="text-[0.8125rem] tabular-nums text-ink-3">{fmtSize(file.size)}</p>
              </div>
              {!busy && (
                <button
                  onClick={() => setFile(null)}
                  aria-label={`Remove ${file.name}`}
                  className="flex h-9 w-9 items-center justify-center rounded-md text-ink-3 hover:bg-sunken hover:text-ink focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand/30"
                >
                  <X className="h-4 w-4" strokeWidth={1.75} />
                </button>
              )}
            </div>
            {busy && (
              // fetch can't report upload progress, so this is honestly indeterminate
              <div className="mt-4 h-1 overflow-hidden rounded-full bg-sunken" role="progressbar" aria-label="Uploading" aria-busy="true">
                <div className="h-full w-full animate-shimmer bg-[linear-gradient(90deg,transparent_0%,theme(colors.brand.DEFAULT)_50%,transparent_100%)] bg-[length:200%_100%]" />
              </div>
            )}
            <div className="mt-4 flex flex-col-reverse gap-2 sm:flex-row sm:items-center sm:justify-between">
              <p className="text-[0.8125rem] text-ink-3" aria-live="polite">
                {busy ? "Uploading… analysis starts as soon as it arrives." : "Ready to upload."}
              </p>
              <Button onClick={submit} disabled={busy}>
                {busy ? "Uploading…" : "Analyze document"}
              </Button>
            </div>
          </m.div>
        ) : (
          <m.label
            key="drop"
            initial={{ opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -4 }}
            transition={{ duration: 0.2, ease: easeSmooth }}
            onDragOver={(e) => { e.preventDefault(); setDrag(true); }}
            onDragLeave={() => setDrag(false)}
            onDrop={(e) => { e.preventDefault(); setDrag(false); pick(e.dataTransfer.files[0]); }}
            className={`group flex cursor-pointer flex-col items-center rounded-xl border border-dashed px-6 py-10 text-center transition-colors duration-150 focus-within:border-brand focus-within:ring-4 focus-within:ring-brand/[0.12] ${
              drag ? "border-brand bg-brand-soft" : "border-line-strong bg-surface hover:border-brand/50 hover:bg-brand-soft/40"
            }`}
          >
            <span className={`flex h-11 w-11 items-center justify-center rounded-lg transition-colors duration-150 ${drag ? "bg-brand text-white" : "bg-brand-soft text-brand"}`}>
              <FileUp className="h-5 w-5" strokeWidth={1.75} aria-hidden />
            </span>
            <span className="mt-4 text-[0.9375rem] font-medium">
              {drag ? "Release to add this file" : <>Drop a document here, or <span className="text-brand underline-offset-2 group-hover:underline">choose a file</span></>}
            </span>
            <span className="mt-1 text-[0.8125rem] text-ink-3">PDF, PNG or JPG · up to {MAX_MB} MB</span>
            <input
              ref={input}
              type="file"
              accept={EXTS.join(",")}
              className="sr-only"
              onChange={(e) => pick(e.target.files?.[0])}
            />
          </m.label>
        )}
      </AnimatePresence>
      {err && <div className="mt-3"><Notice>{err}</Notice></div>}
    </div>
  );
}
