"use client";
import { m } from "framer-motion";
import { ChevronRight, FileText, RotateCcw, Search, Trash2 } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useCallback, useEffect, useMemo, useState } from "react";
import { deleteDocument, DOCUMENTS_PAGE_SIZE, listDocuments, type Doc } from "@/lib/api";
import { AppShell, PageHeader } from "@/components/AppShell";
import UploadDropzone from "@/components/UploadDropzone";
import { Button, ButtonLink } from "@/components/ui/Button";
import { Notice } from "@/components/ui/Form";
import { easeSmooth, staggerContainer, staggerItem } from "@/components/ui/motion";
import { DocRowSkeleton } from "@/components/ui/Skeleton";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { docTypeLabel } from "@/lib/ui";

const FILTERS = [
  ["all", "All"],
  ["ready", "Reviewed"],
  ["active", "In progress"],
  ["failed", "Failed"],
] as const;
type Filter = (typeof FILTERS)[number][0];

const bucket = (s: string): Filter => (s === "report_ready" ? "ready" : s === "failed" ? "failed" : "active");

function fmtDate(iso: string) {
  return new Date(iso).toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" });
}

export default function Dashboard() {
  const router = useRouter();
  const [docs, setDocs] = useState<Doc[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadErr, setLoadErr] = useState("");
  const [confirmDelete, setConfirmDelete] = useState<number | null>(null);
  const [deleting, setDeleting] = useState(false);
  const [deleteErr, setDeleteErr] = useState("");
  // A full page back means there may be more
  const [hasMore, setHasMore] = useState(false);
  const [loadingMore, setLoadingMore] = useState(false);
  const [query, setQuery] = useState("");
  const [filter, setFilter] = useState<Filter>("all");

  useEffect(() => { document.title = "Documents — ClearClause"; }, []);

  // 401s are handled (refresh, then /login) inside api.ts; anything else is shown here
  const refresh = useCallback(() => {
    setLoading(true);
    setLoadErr("");
    listDocuments()
      .then((page) => {
        setDocs(page);
        setHasMore(page.length === DOCUMENTS_PAGE_SIZE);
      })
      .catch((e) => setLoadErr((e as Error).message))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => { refresh(); }, [refresh]);

  // Keep in-flight rows honest without a reload. Only the first page is re-read, so
  // older pages loaded via "Load older" are merged rather than replaced.
  const anyActive = docs.some((d) => bucket(d.status) === "active");
  useEffect(() => {
    if (!anyActive) return;
    const id = setInterval(() => {
      listDocuments()
        .then((page) => {
          const fresh = new Map(page.map((d) => [d.id, d]));
          setDocs((prev) => prev.map((d) => fresh.get(d.id) ?? d));
        })
        .catch(() => {});
    }, 5000);
    return () => clearInterval(id);
  }, [anyActive]);

  async function loadMore() {
    setLoadingMore(true);
    try {
      const page = await listDocuments(docs.length);
      setDocs((prev) => [...prev, ...page]);
      setHasMore(page.length === DOCUMENTS_PAGE_SIZE);
    } catch {
      // Leave the list intact; the button stays available
    } finally {
      setLoadingMore(false);
    }
  }

  async function handleDelete(id: number) {
    setDeleting(true);
    setDeleteErr("");
    try {
      await deleteDocument(id);
      setDocs((prev) => prev.filter((d) => d.id !== id));
      setConfirmDelete(null);
    } catch (e) {
      setDeleteErr((e as Error).message);
    } finally {
      setDeleting(false);
    }
  }

  // ponytail: filters what's loaded, not the server; add a ?q= param when users pass one page
  const shown = useMemo(() => {
    const q = query.trim().toLowerCase();
    return docs.filter(
      (d) =>
        (filter === "all" || bucket(d.status) === filter) &&
        (!q || d.original_filename.toLowerCase().includes(q) || docTypeLabel(d.classified_type).toLowerCase().includes(q)),
    );
  }, [docs, query, filter]);

  const counts = useMemo(() => {
    const c: Record<Filter, number> = { all: docs.length, ready: 0, active: 0, failed: 0 };
    docs.forEach((d) => c[bucket(d.status)]++);
    return c;
  }, [docs]);

  const empty = !loading && !loadErr && docs.length === 0;

  return (
    <AppShell crumbs={[{ label: "Documents" }]}>
      <m.div
        initial={{ opacity: 0, y: 6 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.25, ease: easeSmooth }}
        className="mx-auto max-w-4xl px-4 py-8 sm:px-6 sm:py-10"
      >
        <PageHeader
          title="Documents"
          description="Add a loan, subscription, credit card, rental, sale agreement or patta document to review it."
        />

        <section aria-labelledby="upload-h" className="mt-8">
          <h2 id="upload-h" className="sr-only">Analyze a document</h2>
          <UploadDropzone onUploaded={(doc) => router.push(`/documents/${doc.id}`)} />
          <p className="mt-2.5 text-[0.75rem] text-ink-3">
            Files are deleted automatically seven days after upload.{" "}
            <Link href="/legal/privacy" className="underline-offset-2 hover:text-ink hover:underline">How documents are handled</Link>
          </p>
        </section>

        <section aria-labelledby="library-h" className="mt-12">
          <div className="flex items-baseline justify-between">
            <h2 id="library-h" className="text-[1rem] font-semibold tracking-tight">Your documents</h2>
            {docs.length > 0 && (
              <span className="text-[0.8125rem] tabular-nums text-ink-3">
                {docs.length}{hasMore ? "+" : ""} document{docs.length === 1 ? "" : "s"}
              </span>
            )}
          </div>

          {docs.length > 0 && (
            <div className="mt-4 flex flex-col gap-3 sm:flex-row sm:items-center">
              <div className="relative flex-1">
                <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-ink-3" strokeWidth={1.75} aria-hidden />
                <input
                  type="search"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="Filter by name or type"
                  aria-label="Filter documents by name or type"
                  className="field h-10 pl-9 text-[0.875rem]"
                />
              </div>
              <div role="group" aria-label="Filter by status" className="flex gap-1 overflow-x-auto rounded-lg border border-line bg-sunken/60 p-1">
                {FILTERS.map(([id, label]) => (
                  <button
                    key={id}
                    onClick={() => setFilter(id)}
                    aria-pressed={filter === id}
                    className={`shrink-0 rounded-md px-2.5 py-1.5 text-[0.8125rem] font-medium transition-colors duration-150 ${
                      filter === id ? "bg-surface text-ink shadow-xs" : "text-ink-2 hover:text-ink"
                    }`}
                  >
                    {label} <span className="tabular-nums text-ink-3">{counts[id]}</span>
                  </button>
                ))}
              </div>
            </div>
          )}

          <div className="mt-4">
            {loading ? (
              <div className="divide-y divide-line overflow-hidden rounded-xl border border-line bg-surface" aria-busy="true" aria-label="Loading documents">
                {[0, 1, 2].map((i) => <DocRowSkeleton key={i} />)}
              </div>
            ) : loadErr ? (
              <div className="rounded-xl border border-line bg-surface px-6 py-10 text-center">
                <p className="text-[0.9375rem] font-medium">Your documents couldn&rsquo;t be loaded</p>
                <p className="mt-1 text-[0.8125rem] text-ink-3">{loadErr}</p>
                <Button variant="secondary" className="mt-5" onClick={refresh}>
                  <RotateCcw className="h-4 w-4" strokeWidth={1.75} aria-hidden /> Try again
                </Button>
              </div>
            ) : empty ? (
              <div className="rounded-xl border border-line bg-surface px-6 py-14 text-center">
                <svg viewBox="0 0 64 48" className="mx-auto h-12 w-16" aria-hidden fill="none">
                  <rect x="10" y="4" width="34" height="40" rx="3" className="fill-sunken stroke-line-strong" />
                  <rect x="20" y="8" width="34" height="40" rx="3" className="fill-surface stroke-line-strong" />
                  <rect x="26" y="18" width="20" height="2" rx="1" className="fill-line-strong" />
                  <rect x="26" y="24" width="20" height="2" rx="1" className="fill-ochre" />
                  <rect x="26" y="30" width="13" height="2" rx="1" className="fill-line-strong" />
                </svg>
                <p className="mt-5 text-[0.9375rem] font-medium">No documents yet</p>
                <p className="mx-auto mt-1.5 max-w-sm text-[0.875rem] leading-relaxed text-ink-2">
                  Add your first document above. You&rsquo;ll see its type, the clauses worth
                  questioning, and the wording behind each one.
                </p>
                <ButtonLink href="/sample" variant="ghost" className="mt-4">See a sample analysis first</ButtonLink>
              </div>
            ) : shown.length === 0 ? (
              <div className="rounded-xl border border-line bg-surface px-6 py-10 text-center">
                <p className="text-[0.9375rem] font-medium">No documents match</p>
                <p className="mt-1 text-[0.8125rem] text-ink-3">
                  Try a different name, or{" "}
                  <button className="font-medium text-brand hover:underline" onClick={() => { setQuery(""); setFilter("all"); }}>
                    clear filters
                  </button>
                  .{hasMore && " Only loaded documents are filtered."}
                </p>
              </div>
            ) : (
              <m.ul
                variants={staggerContainer}
                initial="initial"
                animate="animate"
                className="divide-y divide-line overflow-hidden rounded-xl border border-line bg-surface"
              >
                {shown.map((d) => (
                  <m.li key={d.id} variants={staggerItem} className="group relative">
                    {confirmDelete === d.id ? (
                      <div className="flex flex-col gap-3 px-4 py-4 sm:flex-row sm:items-center sm:justify-between sm:px-5">
                        <div className="min-w-0">
                          <p className="text-[0.9375rem]">
                            Delete <span className="break-all font-medium">{d.original_filename}</span>?
                          </p>
                          <p className="text-[0.8125rem] text-ink-3">The file, its findings and its report are removed.</p>
                          {deleteErr && <p role="alert" className="mt-1 text-[0.8125rem] text-risk-high">{deleteErr}</p>}
                        </div>
                        <div className="flex shrink-0 gap-2">
                          <Button variant="ghost" autoFocus onClick={() => { setConfirmDelete(null); setDeleteErr(""); }}>Cancel</Button>
                          <Button variant="danger" onClick={() => handleDelete(d.id)} disabled={deleting}>
                            {deleting ? "Deleting…" : "Delete"}
                          </Button>
                        </div>
                      </div>
                    ) : (
                      <>
                        <Link
                          href={`/documents/${d.id}`}
                          className="flex items-center gap-3.5 py-3.5 pl-4 pr-24 transition-colors duration-150 hover:bg-sunken/50 focus-visible:bg-sunken/50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-brand/30 sm:pl-5"
                        >
                          <FileText className="h-[18px] w-[18px] shrink-0 text-ink-3" strokeWidth={1.5} aria-hidden />
                          <div className="min-w-0 flex-1">
                            <p className="truncate text-[0.9375rem] font-medium" title={d.original_filename}>{d.original_filename}</p>
                            <p className="mt-0.5 flex flex-wrap items-center gap-x-2 text-[0.8125rem] text-ink-3">
                              <span>
                                {!d.classified_type && bucket(d.status) === "active" ? "Identifying type…" : docTypeLabel(d.classified_type)}
                              </span>
                              <span aria-hidden>·</span>
                              <time dateTime={d.created_at} className="tabular-nums">{fmtDate(d.created_at)}</time>
                            </p>
                          </div>
                          <StatusBadge status={d.status} />
                        </Link>
                        <div className="absolute right-3 top-1/2 flex -translate-y-1/2 items-center gap-1">
                          <button
                            onClick={() => setConfirmDelete(d.id)}
                            aria-label={`Delete ${d.original_filename}`}
                            className="flex h-9 w-9 items-center justify-center rounded-md text-ink-3 opacity-100 transition hover:bg-surface hover:text-risk-high focus-visible:opacity-100 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand/30 sm:opacity-0 sm:group-hover:opacity-100"
                          >
                            <Trash2 className="h-4 w-4" strokeWidth={1.75} />
                          </button>
                          <ChevronRight className="h-4 w-4 text-ink-3 transition-transform duration-150 group-hover:translate-x-0.5" strokeWidth={1.75} aria-hidden />
                        </div>
                      </>
                    )}
                  </m.li>
                ))}
              </m.ul>
            )}
          </div>

          {hasMore && !loadErr && (
            <div className="mt-5 flex justify-center">
              <Button variant="secondary" onClick={loadMore} disabled={loadingMore}>
                {loadingMore ? "Loading…" : "Load older documents"}
              </Button>
            </div>
          )}
          {!loading && docs.length > 0 && counts.failed > 0 && filter !== "failed" && (
            <div className="mt-4">
              <Notice>
                {counts.failed} document{counts.failed === 1 ? "" : "s"} couldn&rsquo;t be analyzed. Open one to try again.
              </Notice>
            </div>
          )}
        </section>
      </m.div>
    </AppShell>
  );
}
