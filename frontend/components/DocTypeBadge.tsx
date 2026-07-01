import { docTypeLabel } from "@/lib/ui";

export function DocTypeBadge({ type }: { type: string | null | undefined }) {
  return (
    <span className="inline-flex items-center rounded-md border border-brand/20 bg-brand/[0.04] px-2 py-0.5 text-[0.6875rem] font-medium uppercase tracking-[0.06em] text-brand">
      {docTypeLabel(type)}
    </span>
  );
}
