import type { ComponentProps, ReactNode } from "react";

export function Surface({
  className = "",
  children,
  ...props
}: { children: ReactNode } & ComponentProps<"div">) {
  return (
    <div
      className={`rounded-2xl border border-line bg-surface shadow-soft ${className}`}
      {...props}
    >
      {children}
    </div>
  );
}

export function Container({
  className = "",
  children,
}: {
  className?: string;
  children: ReactNode;
}) {
  return <div className={`mx-auto w-full max-w-content px-6 ${className}`}>{children}</div>;
}
