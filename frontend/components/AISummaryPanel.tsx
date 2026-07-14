import type { AISummary } from "@/lib/api";
import { Surface } from "@/components/ui/Surface";

// The only two constructs the model emits
function Bold({ text }: { text: string }) {
  return (
    <>
      {text.split(/(\*\*[^*]+\*\*)/g).map((part, i) =>
        part.startsWith("**") && part.endsWith("**") ? (
          <strong key={i} className="font-semibold text-ink">
            {part.slice(2, -2)}
          </strong>
        ) : (
          <span key={i}>{part}</span>
        ),
      )}
    </>
  );
}

export function AISummaryPanel({ summary }: { summary: AISummary }) {
  const lines = summary.content
    .split("\n")
    .map((l) => l.trim())
    .filter(Boolean);

  return (
    <Surface className="mt-8 px-8 py-6">
      <div className="mb-4 flex items-baseline gap-2">
        <h3 className="t-section">Summary</h3>
        <span className="t-caption">grounded in the findings below</span>
      </div>

      <div className="space-y-2 text-[0.9375rem] leading-relaxed text-ink-2">
        {lines.map((line, i) => {
          const bullet = line.match(/^[*-]\s+(.*)$/);
          if (bullet) {
            return (
              <p key={i} className="flex gap-2 pl-1">
                <span aria-hidden className="text-ink-3">
                  •
                </span>
                <span>
                  <Bold text={bullet[1]} />
                </span>
              </p>
            );
          }
          return (
            <p key={i}>
              <Bold text={line} />
            </p>
          );
        })}
      </div>
    </Surface>
  );
}
