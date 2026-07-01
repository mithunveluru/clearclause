"use client";
import { AnimatePresence, m } from "framer-motion";
import { FileUp } from "lucide-react";
import { useRef, useState } from "react";
import { uploadDocument, type Doc } from "@/lib/api";

export default function UploadDropzone({ onUploaded }: { onUploaded: (doc: Doc) => void }) {
  const input = useRef<HTMLInputElement>(null);
  const [busy, setBusy] = useState(false);
  const [drag, setDrag] = useState(false);
  const [err, setErr] = useState("");

  async function handle(file: File | undefined) {
    if (!file) return;
    setErr("");
    setBusy(true);
    try {
      const doc = await uploadDocument(file);
      onUploaded(doc);
    } catch (e) {
      setErr((e as Error).message);
    } finally {
      setBusy(false);
      if (input.current) input.current.value = "";
    }
  }

  return (
    <div>
      <m.div
        onClick={() => !busy && input.current?.click()}
        onDragOver={(e) => { e.preventDefault(); setDrag(true); }}
        onDragLeave={() => setDrag(false)}
        onDrop={(e) => { e.preventDefault(); setDrag(false); handle(e.dataTransfer.files[0]); }}
        animate={{ scale: drag ? 1.014 : busy ? 1.004 : 1 }}
        transition={{ duration: 0.28, ease: [0.22, 1, 0.36, 1] }}
        className={`group relative cursor-pointer overflow-hidden rounded-3xl border px-8 py-16 text-center transition-colors duration-200 ${
          busy
            ? "cursor-wait border-brand/30 bg-brand/[0.025]"
            : drag
            ? "border-brand border-solid bg-brand/[0.05]"
            : "border-dashed border-line-strong bg-surface hover:border-brand/50 hover:bg-brand/[0.02]"
        }`}
      >
        {busy && (
          <div className="pointer-events-none absolute inset-0 animate-shimmer bg-[linear-gradient(105deg,transparent_40%,rgba(79,70,229,0.07)_50%,transparent_60%)] bg-[length:200%_100%]" />
        )}

        {busy && (
          <div className="absolute inset-x-0 bottom-0 h-[2px] overflow-hidden rounded-b-3xl">
            <div className="h-full w-full animate-shimmer bg-[linear-gradient(90deg,transparent_0%,#4f46e5_50%,transparent_100%)] bg-[length:200%_100%]" />
          </div>
        )}

        <div
          className={`relative mx-auto flex h-16 w-16 items-center justify-center rounded-2xl transition-all duration-300 ${
            drag
              ? "scale-110 bg-brand text-white shadow-brand"
              : busy
              ? "bg-brand/[0.10] text-brand"
              : "bg-brand/[0.07] text-brand group-hover:bg-brand group-hover:text-white group-hover:shadow-brand group-hover:scale-105"
          }`}
        >
          <AnimatePresence mode="wait">
            {busy ? (
              <m.span
                key="busy"
                initial={{ opacity: 0, scale: 0.7 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.7 }}
                transition={{ duration: 0.25, ease: [0.22, 1, 0.36, 1] }}
                className="flex h-5 w-5 items-center justify-center"
              >
                <span className="h-5 w-5 animate-pulse rounded-full border-2 border-brand/70" />
              </m.span>
            ) : (
              <m.span
                key="idle"
                initial={{ opacity: 0, scale: 0.7 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.7 }}
                transition={{ duration: 0.25, ease: [0.22, 1, 0.36, 1] }}
              >
                <FileUp className="h-6 w-6" strokeWidth={1.75} />
              </m.span>
            )}
          </AnimatePresence>
        </div>

        <AnimatePresence mode="wait">
          <m.div
            key={busy ? "busy" : drag ? "drag" : "idle"}
            initial={{ opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -4 }}
            transition={{ duration: 0.3, ease: [0.22, 1, 0.36, 1] }}
          >
            <p className="mt-5 text-[1.0625rem] font-medium tracking-tight text-ink">
              {busy
                ? "Uploading your document…"
                : drag
                ? "Release to analyze"
                : "Drop a document, or click to browse"}
            </p>
            <p className="mt-1.5 t-caption">
              {busy ? "Sit tight — analysis starts automatically" : "PDF, PNG or JPG · up to 10 MB"}
            </p>
          </m.div>
        </AnimatePresence>

        <input
          ref={input}
          type="file"
          accept=".pdf,.png,.jpg,.jpeg"
          className="hidden"
          onChange={(e) => handle(e.target.files?.[0])}
        />
      </m.div>
      <AnimatePresence>
        {err && (
          <m.p
            initial={{ opacity: 0, y: 4 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            className="mt-3 text-sm text-risk-high"
          >
            {err}
          </m.p>
        )}
      </AnimatePresence>
    </div>
  );
}
