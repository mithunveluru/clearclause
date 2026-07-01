import type { Entity } from "@/lib/api";
import { issueLabel } from "@/lib/ui";

export function EntitiesPanel({ entities }: { entities: Entity[] }) {
  if (entities.length === 0) return null;
  return (
    <div>
      <h3 className="t-section mb-5">Extracted details</h3>
      <dl className="divide-y divide-line">
        {entities.map((e, i) => (
          <div key={i} className="flex items-start justify-between gap-4 py-3">
            <dt className="text-[0.9375rem] text-ink-2">{issueLabel(e.entity_type)}</dt>
            <dd className="max-w-[60%] break-words text-right text-[0.9375rem] font-medium text-ink">
              {e.entity_value}
            </dd>
          </div>
        ))}
      </dl>
    </div>
  );
}
