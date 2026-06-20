export default function Home() {
  return (
    <main className="mx-auto flex max-w-2xl flex-col gap-6 px-6 py-20">
      <h1 className="text-4xl font-bold tracking-tight">ClearClause</h1>
      <p className="text-lg text-gray-600">
        Upload a loan agreement or subscription terms and see hidden fees,
        penalty clauses, and auto-renew traps in plain English.
      </p>
      <p className="text-sm text-gray-400">
        Upload flow lands in Phase 3. Backend health:{" "}
        <code>{process.env.NEXT_PUBLIC_API_BASE_URL}/health</code>
      </p>
    </main>
  );
}
