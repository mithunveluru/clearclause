import Link from "next/link";

/** A page with a folded corner and one highlighted line: the product in a glyph. */
export function Mark({ className = "h-6 w-6" }: { className?: string }) {
  return (
    <svg viewBox="0 0 24 24" className={className} aria-hidden fill="none">
      <path d="M5 3.5h9.5L19 8v12.5H5z" className="fill-brand" />
      <path d="M14.5 3.5V8H19" className="fill-brand-accent" />
      <rect x="8" y="11" width="8" height="1.6" rx=".8" className="fill-white/55" />
      <rect x="8" y="14.4" width="8" height="1.6" rx=".8" className="fill-ochre" />
      <rect x="8" y="17.8" width="5" height="1.6" rx=".8" className="fill-white/55" />
    </svg>
  );
}

export function Logo({ href = "/" }: { href?: string }) {
  return (
    <Link
      href={href}
      className="group inline-flex items-center gap-2 rounded-md text-ink focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-brand/25"
    >
      <Mark className="h-6 w-6 transition-transform duration-200 ease-smooth group-hover:-translate-y-px" />
      <span className="text-[1rem] font-semibold tracking-[-0.015em]">
        Clear<span className="text-ink-2">Clause</span>
      </span>
    </Link>
  );
}
