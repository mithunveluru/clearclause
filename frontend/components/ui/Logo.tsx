import Link from "next/link";
import { ShieldCheck } from "lucide-react";

export function Logo({ href = "/" }: { href?: string }) {
  return (
    <Link href={href} className="inline-flex items-center gap-2 text-ink">
      <ShieldCheck className="h-5 w-5" strokeWidth={1.75} />
      <span className="text-[1.0625rem] font-semibold tracking-tight">ClearClause</span>
    </Link>
  );
}
