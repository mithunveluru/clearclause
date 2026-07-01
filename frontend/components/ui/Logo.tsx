import Link from "next/link";
import { ShieldCheck } from "lucide-react";

export function Logo({ href = "/" }: { href?: string }) {
  return (
    <Link href={href} className="group inline-flex items-center gap-2 text-ink">
      <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-brand text-white shadow-brand transition-transform duration-200 group-hover:-translate-y-px">
        <ShieldCheck className="h-4 w-4" strokeWidth={2} />
      </span>
      <span className="text-[1.0625rem] font-semibold tracking-tight">ClearClause</span>
    </Link>
  );
}
