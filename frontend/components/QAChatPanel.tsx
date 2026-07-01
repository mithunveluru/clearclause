"use client";
import { m } from "framer-motion";
import { MessageSquare, Send } from "lucide-react";
import { useState } from "react";
import { askQuestion, type Citation } from "@/lib/api";
import { Surface } from "@/components/ui/Surface";

type Msg = { role: "user" | "assistant"; content: string; citations?: Citation[] };

function citationLabel(c: Citation): string {
  const parts = [];
  if (c.section) parts.push(c.section);
  if (c.page != null) parts.push(`p${c.page}`);
  return parts.join(" · ") || "Clause";
}

export function QAChatPanel({ docId }: { docId: number }) {
  const [messages, setMessages] = useState<Msg[]>([]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    const q = input.trim();
    if (!q || busy) return;
    setMessages((m) => [...m, { role: "user", content: q }]);
    setInput("");
    setBusy(true);
    try {
      const a = await askQuestion(docId, q);
      setMessages((m) => [...m, { role: "assistant", content: a.answer, citations: a.citations }]);
    } catch {
      setMessages((m) => [
        ...m,
        { role: "assistant", content: "Sorry — I couldn't answer that right now." },
      ]);
    } finally {
      setBusy(false);
    }
  }

  return (
    <Surface className="mt-8 px-8 py-7">
      <div className="mb-1 flex items-center gap-2">
        <MessageSquare className="h-4 w-4 text-ink-3" strokeWidth={1.75} />
        <h3 className="t-section">Ask about this document</h3>
      </div>
      <p className="t-caption mb-6">
        Answers are grounded only in this document, with citations.
      </p>

      <div className="space-y-3">
        {messages.map((m, i) => (
          <m.div
            key={i}
            initial={{ opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
            className={m.role === "user" ? "text-right" : ""}
          >
            <div
              className={`inline-block max-w-[85%] rounded-2xl px-4 py-2.5 text-left text-[0.9375rem] leading-relaxed ${
                m.role === "user" ? "bg-brand text-white" : "bg-canvas text-ink"
              }`}
            >
              {m.content}
            </div>
            {m.citations && m.citations.length > 0 && (
              <div className="mt-2 flex flex-wrap gap-1.5">
                {m.citations.map((c, j) => (
                  <span
                    key={j}
                    title={c.snippet}
                    className="rounded-md border border-line px-2 py-0.5 text-[0.6875rem] font-medium text-ink-2"
                  >
                    {citationLabel(c)}
                  </span>
                ))}
              </div>
            )}
          </m.div>
        ))}
        {busy && <p className="text-[0.8125rem] font-medium text-brand">Thinking…</p>}
      </div>

      <form onSubmit={submit} className="mt-6 flex gap-2">
        <input
          className="field flex-1"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="e.g. Can the landlord increase rent anytime?"
        />
        <button
          type="submit"
          disabled={busy}
          className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-brand text-white shadow-xs transition hover:bg-brand-accent hover:shadow-brand active:scale-[0.98] disabled:opacity-40"
        >
          <Send className="h-4 w-4" strokeWidth={2} />
        </button>
      </form>
    </Surface>
  );
}
