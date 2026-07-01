import Link from "next/link";
import type { ComponentProps, ReactNode } from "react";

type Variant = "primary" | "secondary" | "ghost";
type Size = "md" | "lg";

const base =
  "inline-flex items-center justify-center gap-2 rounded-[10px] font-medium tracking-tight transition-all duration-200 ease-smooth disabled:opacity-40 disabled:pointer-events-none focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-brand/25";

const variants: Record<Variant, string> = {
  primary:
    "bg-brand text-white shadow-xs hover:bg-brand-accent hover:shadow-brand hover:-translate-y-px active:translate-y-0 active:scale-[0.99]",
  secondary:
    "bg-surface text-ink border border-line-strong shadow-xs hover:border-brand/40 hover:text-brand active:scale-[0.99]",
  ghost: "text-ink-2 hover:text-brand hover:bg-brand/[0.06]",
};

const sizes: Record<Size, string> = {
  md: "h-10 px-[18px] text-[0.9375rem]",
  lg: "h-[52px] px-7 text-[1.0625rem]",
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
