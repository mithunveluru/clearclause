"use client";
import { useRef, useState } from "react";
import { uploadDocument } from "@/lib/api";

export default function UploadDropzone({ onUploaded }: { onUploaded: () => void }) {
  const input = useRef<HTMLInputElement>(null);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState("");

  async function handle(file: File | undefined) {
    if (!file) return;
    setErr("");
    setBusy(true);
    try {
      await uploadDocument(file);
      onUploaded();
    } catch (e) {
      setErr((e as Error).message);
    } finally {
      setBusy(false);
      if (input.current) input.current.value = "";
    }
  }

  return (
    <div>
      <div
        onClick={() => input.current?.click()}
        onDragOver={(e) => e.preventDefault()}
        onDrop={(e) => {
          e.preventDefault();
          handle(e.dataTransfer.files[0]);
        }}
        className="cursor-pointer rounded-xl border-2 border-dashed border-gray-300 bg-white p-10 text-center hover:border-blue-400"
      >
        <p className="font-medium">{busy ? "Uploading…" : "Drop a PDF or image here, or click to choose"}</p>
        <p className="mt-1 text-sm text-gray-500">PDF, PNG, JPG · up to 10 MB</p>
        <input
          ref={input}
          type="file"
          accept=".pdf,.png,.jpg,.jpeg"
          className="hidden"
          onChange={(e) => handle(e.target.files?.[0])}
        />
      </div>
      {err && <p className="mt-2 text-sm text-red-600">{err}</p>}
    </div>
  );
}
