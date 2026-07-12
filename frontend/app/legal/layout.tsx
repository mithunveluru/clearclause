import Link from "next/link";
import { TopBar } from "@/components/ui/TopBar";
import { Container } from "@/components/ui/Surface";

export default function LegalLayout({ children }: { children: React.ReactNode }) {
  return (
    <>
      <div className="print:hidden">
        <TopBar
          right={
            <Link
              href="/dashboard"
              className="text-[0.875rem] font-medium text-ink-2 hover:text-ink"
            >
              Workspace
            </Link>
          }
        />
      </div>
      {children}
      <footer className="border-t border-line print:hidden">
        <Container className="flex flex-col items-center justify-between gap-3 py-8 sm:flex-row">
          <span className="t-caption">© {new Date().getFullYear()} ClearClause</span>
          <span className="t-caption">
            Informational analysis only — not legal or financial advice.
          </span>
        </Container>
      </footer>
    </>
  );
}
