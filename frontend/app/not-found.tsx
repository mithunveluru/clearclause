import Link from "next/link";
import { Mark } from "@/components/ui/Logo";
import { ButtonLink } from "@/components/ui/Button";

export default function NotFound() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center bg-canvas px-6 text-center">
      <Mark className="h-9 w-9" />
      <p className="mt-6 font-serif text-[1rem] tabular-nums text-ochre">404</p>
      <h1 className="t-display-2 mt-2">This page isn&rsquo;t in the file.</h1>
      <p className="mt-3 max-w-sm text-[0.9375rem] leading-relaxed text-ink-2">
        The link may be mistyped, or the document may have been deleted.
      </p>
      <div className="mt-8 flex flex-col gap-2 sm:flex-row">
        <ButtonLink href="/dashboard">Go to documents</ButtonLink>
        <ButtonLink href="/" variant="ghost">Home</ButtonLink>
      </div>
      <Link href="/legal/contact" className="mt-10 text-[0.8125rem] text-ink-3 hover:text-ink">Report a broken link</Link>
    </main>
  );
}
