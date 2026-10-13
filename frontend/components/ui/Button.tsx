import Link from "next/link";
import type { ComponentProps, ReactNode } from "react";

type Variant = "primary" | "secondary" | "ghost" | "danger";
type Size = "md" | "lg";

const base =
  "inline-flex select-none items-center justify-center gap-2 rounded-lg font-medium tracking-tight transition-[background-color,border-color,color,box-shadow,transform] duration-150 ease-smooth active:scale-[0.985] disabled:opacity-40 disabled:pointer-events-none focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-brand/25";

const variants: Record<Variant, string> = {
  primary:
    "bg-brand text-white shadow-xs hover:bg-brand-accent hover:shadow-brand",
  secondary:
    "bg-surface text-ink border border-line-strong shadow-xs hover:border-ink/25 hover:bg-canvas",
  ghost: "text-ink-2 hover:text-ink hover:bg-sunken",
  danger: "bg-risk-high text-white shadow-xs hover:bg-risk-critical",
};

const sizes: Record<Size, string> = {
  md: "h-10 px-4 text-[0.875rem]",
  lg: "h-12 px-6 text-[0.9375rem]",
};

function cls(variant: Variant, size: Size, extra?: string) {
  return [base, variants[variant], sizes[size], extra].filter(Boolean).join(" ");
}

export function Button({
  variant = "primary",
  size = "md",
  className,
  children,
  ...props
}: { variant?: Variant; size?: Size; children: ReactNode } & ComponentProps<"button">) {
  return (
    <button className={cls(variant, size, className)} {...props}>
      {children}
    </button>
  );
}

export function ButtonLink({
  variant = "primary",
  size = "md",
  className,
  children,
  ...props
}: { variant?: Variant; size?: Size; children: ReactNode } & ComponentProps<typeof Link>) {
  return (
    <Link className={cls(variant, size, className)} {...props}>
      {children}
    </Link>
  );
}
