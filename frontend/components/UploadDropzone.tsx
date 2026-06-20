"use client";
import { motion } from "framer-motion";
import { FileUp, Loader2 } from "lucide-react";
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
      <motion.div
        onClick={() => !busy && input.current?.click()}
        onDragOver={(e) => {
          e.preventDefault();
          setDrag(true);
        }}
        onDragLeave={() => setDrag(false)}
        onDrop={(e) => {
          e.preventDefault();
          setDrag(false);
          handle(e.dataTransfer.files[0]);
        }}
        animate={{ scale: drag ? 1.008 : 1 }}
        transition={{ duration: 0.2, ease: [0.22, 1, 0.36, 1] }}
        className={`group relative cursor-pointer overflow-hidden rounded-3xl border border-dashed px-8 py-14 text-center transition-colors duration-200 ${
          drag ? "border-accent bg-accent/[0.025]" : "border-line-strong bg-surface hover:border-ink-3"
        }`}
      >
        <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-canvas text-ink transition-colors duration-200 group-hover:bg-ink group-hover:text-white">
          {busy ? (
            <Loader2 className="h-[22px] w-[22px] animate-spin" strokeWidth={1.75} />
          ) : (
            <FileUp className="h-[22px] w-[22px]" strokeWidth={1.75} />
          )}
        </div>
        <p className="mt-5 text-[1.0625rem] font-medium tracking-tight text-ink">
          {busy ? "Uploading…" : "Drop a document, or click to browse"}
        </p>
        <p className="mt-1.5 t-caption">PDF, PNG or JPG · up to 10&nbsp;MB</p>
        <input
          ref={input}
          type="file"
          accept=".pdf,.png,.jpg,.jpeg"
          className="hidden"
          onChange={(e) => handle(e.target.files?.[0])}
        />
      </motion.div>
      {err && <p className="mt-3 text-sm text-risk-high">{err}</p>}
    </div>
  );
}
