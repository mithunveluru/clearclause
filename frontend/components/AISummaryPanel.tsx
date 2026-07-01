import { Sparkles } from "lucide-react";
import type { AISummary } from "@/lib/api";
import { Surface } from "@/components/ui/Surface";

export function AISummaryPanel({ summary }: { summary: AISummary }) {
  return (
    <Surface className="mt-8 px-8 py-6">
      <div className="mb-3 flex items-center gap-2">
        <Sparkles className="h-4 w-4 text-brand" strokeWidth={1.75} />
        <h3 className="t-section">AI summary</h3>
        <span className="t-caption">· grounded in the findings below</span>
      </div>
      <p className="text-[0.9375rem] leading-relaxed text-ink-2">{summary.content}</p>
    </Surface>
  );
}
