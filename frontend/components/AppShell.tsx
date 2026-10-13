"use client";
import { AnimatePresence, m } from "framer-motion";
import { ChevronRight, FileStack, LogOut, Menu, UserRound, X } from "lucide-react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState, type ReactNode } from "react";
import { logout } from "@/lib/api";
import { Logo } from "@/components/ui/Logo";
import { easeSmooth } from "@/components/ui/motion";

const NAV = [
  { href: "/dashboard", label: "Documents", icon: FileStack, match: ["/dashboard", "/documents"] },
  { href: "/account", label: "Account", icon: UserRound, match: ["/account"] },
];

function useSignOut() {
  const router = useRouter();
  return async () => {
    await logout();
    router.push("/login");
  };
}

function NavLinks({ onNavigate }: { onNavigate?: () => void }) {
  const path = usePathname();
  return (
    <ul className="space-y-0.5">
      {NAV.map(({ href, label, icon: Icon, match }) => {
        const on = match.some((p) => path.startsWith(p));
        return (
          <li key={href} className="relative">
            {on && (
              <m.span
                layoutId="nav-active"
                transition={{ duration: 0.22, ease: easeSmooth }}
                className="absolute inset-0 rounded-md bg-sunken"
                aria-hidden
              />
            )}
            <Link
              href={href}
              onClick={onNavigate}
              aria-current={on ? "page" : undefined}
              className={`relative flex h-9 items-center gap-2.5 rounded-md px-2.5 text-[0.875rem] font-medium transition-colors duration-150 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand/30 ${
                on ? "text-ink" : "text-ink-2 hover:text-ink"
              }`}
            >
              <Icon className={`h-4 w-4 ${on ? "text-brand" : ""}`} strokeWidth={1.75} aria-hidden />
              {label}
            </Link>
          </li>
        );
      })}
    </ul>
  );
}

function SignOutButton() {
  const signOut = useSignOut();
  return (
    <button
      onClick={signOut}
      className="flex h-9 w-full items-center gap-2.5 rounded-md px-2.5 text-[0.875rem] font-medium text-ink-2 transition-colors hover:text-ink focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand/30"
    >
      <LogOut className="h-4 w-4" strokeWidth={1.75} aria-hidden />
      Sign out
    </button>
  );
}

export type Crumb = { label: string; href?: string };

/**
 * The signed-in frame. `focus` drops the sidebar for the document workspace, which
 * carries its own section navigation and needs the width.
 */
export function AppShell({
  children,
  crumbs,
  actions,
  focus = false,
}: {
  children: ReactNode;
  crumbs?: Crumb[];
  actions?: ReactNode;
  focus?: boolean;
}) {
  const [drawer, setDrawer] = useState(false);
  const path = usePathname();

  useEffect(() => setDrawer(false), [path]);
  useEffect(() => {
    if (!drawer) return;
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && setDrawer(false);
    window.addEventListener("keydown", onKey);
    document.body.style.overflow = "hidden";
    return () => {
      window.removeEventListener("keydown", onKey);
      document.body.style.overflow = "";
    };
  }, [drawer]);

  return (
    <div className="min-h-screen bg-canvas">
      <a href="#main" className="sr-only focus:not-sr-only focus:fixed focus:left-3 focus:top-3 focus:z-[60] focus:rounded-md focus:bg-surface focus:px-3 focus:py-2 focus:shadow-raised">
        Skip to content
      </a>

      {!focus && (
        <aside className="fixed inset-y-0 left-0 z-30 hidden w-60 flex-col border-r border-line bg-canvas lg:flex">
          <div className="flex h-14 items-center px-5">
            <Logo href="/dashboard" />
          </div>
          <nav aria-label="Workspace" className="flex-1 px-3 pt-4">
            <NavLinks />
          </nav>
          <div className="border-t border-line p-3">
            <SignOutButton />
          </div>
        </aside>
      )}

      <div className={focus ? "" : "lg:pl-60"}>
        <header className="sticky top-0 z-20 flex h-14 items-center gap-3 border-b border-line bg-canvas/90 px-4 backdrop-blur-md sm:px-6">
          <button
            className={`-ml-2 flex h-10 w-10 items-center justify-center rounded-md text-ink ${focus ? "" : "lg:hidden"}`}
            aria-label="Open navigation"
            aria-expanded={drawer}
            onClick={() => setDrawer(true)}
          >
            <Menu className="h-5 w-5" strokeWidth={1.75} />
          </button>
          {focus && <span className="hidden sm:block"><Logo href="/dashboard" /></span>}
          {crumbs && crumbs.length > 0 && (
            <nav aria-label="Breadcrumb" className="min-w-0 flex-1">
              <ol className="flex min-w-0 items-center gap-1.5 text-[0.875rem]">
                {focus && <ChevronRight className="hidden h-3.5 w-3.5 shrink-0 text-ink-3 sm:block" aria-hidden />}
                {crumbs.map((c, i) => {
                  const last = i === crumbs.length - 1;
                  return (
                    <li key={i} className={`flex items-center gap-1.5 ${last ? "min-w-0" : "shrink-0"}`}>
                      {c.href && !last ? (
                        <Link href={c.href} className="text-ink-2 hover:text-ink">{c.label}</Link>
                      ) : (
                        <span aria-current={last ? "page" : undefined} className="truncate font-medium text-ink">{c.label}</span>
                      )}
                      {!last && <ChevronRight className="h-3.5 w-3.5 shrink-0 text-ink-3" aria-hidden />}
                    </li>
                  );
                })}
              </ol>
            </nav>
          )}
          {actions && <div className="ml-auto flex shrink-0 items-center gap-2">{actions}</div>}
        </header>

        <main id="main">{children}</main>
      </div>

      <AnimatePresence>
        {drawer && (
          <div className="fixed inset-0 z-50" role="dialog" aria-modal="true" aria-label="Navigation">
            <m.div
              className="absolute inset-0 bg-ink/25"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.2 }}
              onClick={() => setDrawer(false)}
            />
            <m.div
              className="absolute inset-y-0 left-0 flex w-72 max-w-[85vw] flex-col bg-canvas shadow-lift"
              initial={{ x: "-100%" }}
              animate={{ x: 0 }}
              exit={{ x: "-100%" }}
              transition={{ duration: 0.26, ease: easeSmooth }}
            >
              <div className="flex h-14 items-center justify-between px-5">
                <Logo href="/dashboard" />
                <button
                  autoFocus
                  onClick={() => setDrawer(false)}
                  aria-label="Close navigation"
                  className="-mr-2 flex h-10 w-10 items-center justify-center rounded-md text-ink"
                >
                  <X className="h-5 w-5" strokeWidth={1.75} />
                </button>
              </div>
              <nav aria-label="Workspace" className="flex-1 px-3 pt-4">
                <NavLinks onNavigate={() => setDrawer(false)} />
              </nav>
              <div className="border-t border-line p-3">
                <SignOutButton />
              </div>
            </m.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
}

/** Title block at the top of a workspace page. */
export function PageHeader({ title, description, actions }: { title: string; description?: ReactNode; actions?: ReactNode }) {
  return (
    <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
      <div className="min-w-0">
        <h1 className="text-[1.5rem] font-semibold tracking-tight">{title}</h1>
        {description && <p className="mt-1 max-w-prose text-[0.9375rem] text-ink-2">{description}</p>}
      </div>
      {actions && <div className="flex shrink-0 gap-2">{actions}</div>}
    </div>
  );
}
