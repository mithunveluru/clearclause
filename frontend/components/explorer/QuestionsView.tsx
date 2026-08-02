"use client";
import { AnimatePresence, m } from "framer-motion";
import { viewTransition } from "@/components/ui/motion";
import { HelpCircle, MessageSquare, Send } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { askQuestion, type Citation, type SuggestedQuestion } from "@/lib/api";
import { BRAND, NEUTRAL, RISK } from "@/lib/ui";

type Msg = { role: "user" | "assistant"; content: string; citations?: Citation[] };

// Brand indigo, not a one-off violet outside the palette
const CATEGORY_COLORS: Record<string, string> = {
  cost: RISK.medium.color,
  penalty: RISK.high.color,
  cancellation: BRAND,
  rights: RISK.low.color,
};

function citationLabel(c: Citation) {
  const p = [];
  if (c.section) p.push(c.section);
  if (c.page != null) p.push(`p${c.page}`);
  return p.join(" · ") || "Clause";
}

function ExpandableCitation({ c }: { c: Citation }) {
  const [open, setOpen] = useState(false);
  return (
    <span className="inline-flex flex-col items-start">
      <button
        onClick={() => setOpen((v) => !v)}
        aria-expanded={open}
        className="rounded-md border border-line px-2 py-0.5 text-[0.6875rem] font-medium text-ink-2 hover:border-brand/40 hover:text-brand transition"
      >
        {citationLabel(c)}
      </button>
      <AnimatePresence>
        {open && c.snippet && (
          <m.span
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.2 }}
            className="mt-1 block max-w-xs overflow-hidden rounded-md bg-canvas px-2.5 py-1.5 text-[0.75rem] italic leading-relaxed text-ink-2"
          >
            {c.snippet}
          </m.span>
        )}
      </AnimatePresence>
    </span>
  );
}

export function QuestionsView({
  docId,
  questions,
  qaReady,
}: {
  docId: number;
  questions: SuggestedQuestion[];
  qaReady: boolean;
}) {
  const [messages, setMessages] = useState<Msg[]>([]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }, [messages]);

  async function submit(question: string) {
    if (!question.trim() || busy || !qaReady) return;
    setMessages((prev) => [...prev, { role: "user", content: question }]);
    setInput("");
    setBusy(true);
    try {
      const a = await askQuestion(docId, question);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: a.answer, citations: a.citations },
      ]);
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "Sorry — couldn't answer that right now." },
      ]);
    } finally {
      setBusy(false);
    }
  }

  return (
    <m.div {...viewTransition}>
      <h2 className="mb-1 text-[1.375rem] font-semibold tracking-tight">Questions to Ask</h2>
      <p className="mb-6 t-body text-ink-2">
        Ask these before signing. Every answer is grounded in the document with citations.
      </p>

      {questions.length > 0 && (
        <div className="mb-8 space-y-2">
          <p className="t-caption mb-3 uppercase">Detected from this document</p>
          {questions.map((q, i) => {
            const color = CATEGORY_COLORS[q.category] ?? NEUTRAL;
            return (
              <m.button
                key={i}
                initial={{ opacity: 0, y: 6 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.04, duration: 0.3 }}
                onClick={() => qaReady && submit(q.question)}
                disabled={!qaReady}
                className="flex w-full items-start gap-3 rounded-xl border border-line bg-surface px-4 py-3.5 text-left transition hover:border-brand/30 hover:bg-brand/[0.02] disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <HelpCircle
                  className="mt-0.5 h-4 w-4 shrink-0"
                  style={{ color }}
                  strokeWidth={1.75}
                />
                <span className="text-[0.9375rem] leading-relaxed">{q.question}</span>
              </m.button>
            );
          })}
        </div>
      )}

      {qaReady ? (
        <>
          <div className="mb-1 flex items-center gap-2">
            <MessageSquare className="h-4 w-4 text-ink-3" strokeWidth={1.75} />
            <p className="t-section">Ask about this document</p>
          </div>
          <p className="t-caption mb-4">Answers cite the page and clause they came from.</p>

          {messages.length > 0 && (
            <div className="mb-4 space-y-3">
              {messages.map((msg, i) => (
                <m.div
                  key={i}
                  initial={{ opacity: 0, y: 6 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.25 }}
                  className={msg.role === "user" ? "text-right" : ""}
                >
                  <div
                    className={`inline-block max-w-[88%] rounded-2xl px-4 py-2.5 text-left text-[0.9375rem] leading-relaxed ${
                      msg.role === "user" ? "bg-brand text-white" : "bg-canvas text-ink"
                    }`}
                  >
                    {msg.content}
                  </div>
                  {msg.citations && msg.citations.length > 0 && (
                    <div className="mt-1.5 flex flex-wrap gap-1.5 justify-end">
                      {msg.citations.map((c, j) => (
                        <ExpandableCitation key={j} c={c} />
                      ))}
                    </div>
                  )}
                </m.div>
              ))}
              {busy && (
                <p className="text-[0.8125rem] font-medium text-brand animate-pulse">
                  Thinking…
                </p>
              )}
              <div ref={endRef} />
            </div>
          )}

          <form
            onSubmit={(e) => { e.preventDefault(); submit(input); }}
            className="flex gap-2"
          >
            <input
              className="field flex-1"
              aria-label="Ask a question about this document"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="e.g. Can I cancel this agreement early?"
            />
            <button
              type="submit"
              disabled={busy}
              aria-label="Send question"
              className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-brand text-white shadow-xs transition hover:bg-brand-accent disabled:opacity-40"
            >
              <Send className="h-4 w-4" strokeWidth={2} />
            </button>
          </form>
        </>
      ) : (
        <div className="flex items-center gap-3 rounded-xl border border-line bg-canvas px-4 py-4">
          <span className="h-2 w-2 shrink-0 animate-pulse rounded-full bg-brand" />
          <p className="t-body text-ink-3">
            Generating embeddings — Q&amp;A turns on automatically in a few seconds.
          </p>
        </div>
      )}
    </m.div>
  );
}
