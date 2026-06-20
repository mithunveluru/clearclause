import Link from "next/link";

export default function Home() {
  return (
    <main className="mx-auto flex max-w-2xl flex-col gap-6 px-6 py-24">
      <h1 className="text-5xl font-bold tracking-tight">ClearClause</h1>
      <p className="text-lg text-gray-600">
        Upload a loan agreement or subscription terms and see hidden fees,
        penalty clauses, and auto-renew traps in plain English — with a risk
        score and a downloadable report.
      </p>
      <div className="flex gap-3">
        <Link
          href="/dashboard"
          className="rounded-lg bg-blue-600 px-5 py-2.5 font-medium text-white hover:bg-blue-700"
        >
          Get started
        </Link>
        <Link
          href="/login"
          className="rounded-lg border px-5 py-2.5 font-medium hover:bg-gray-100"
        >
          Log in
        </Link>
      </div>
    </main>
  );
}
