"use client";
import { m } from "framer-motion";
import { ChevronRight, FileSearch, Trash2 } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useCallback, useEffect, useState } from "react";
import { deleteDocument, DOCUMENTS_PAGE_SIZE, listDocuments, logout, type Doc } from "@/lib/api";
import { DocTypeBadge } from "@/components/DocTypeBadge";
import UploadDropzone from "@/components/UploadDropzone";
import { Button } from "@/components/ui/Button";
import { staggerContainer, staggerItem, easeSmooth } from "@/components/ui/motion";
import { DocRowSkeleton } from "@/components/ui/Skeleton";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { Container, Surface } from "@/components/ui/Surface";
import { TopBar } from "@/components/ui/TopBar";

function fmtDate(iso: string) {
  return new Date(iso).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

export default function Dashboard() {
  const router = useRouter();
  const [docs, setDocs] = useState<Doc[]>([]);
  const [loading, setLoading] = useState(true);
  const [confirmDelete, setConfirmDelete] = useState<number | null>(null);
  const [deleting, setDeleting] = useState(false);
  // A full page back means there may be more
  const [hasMore, setHasMore] = useState(false);
  const [loadingMore, setLoadingMore] = useState(false);

  useEffect(() => { document.title = "Workspace — ClearClause"; }, []);

  const refresh = useCallback(() => {
    listDocuments()
      .then((page) => {
        setDocs(page);
        setHasMore(page.length === DOCUMENTS_PAGE_SIZE);
      })
      .catch(() => router.push("/login"))
      .finally(() => setLoading(false));
  }, [router]);

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

  useEffect(() => { refresh(); }, [refresh]);

  async function handleDelete(id: number) {
    setDeleting(true);
    try {
      await deleteDocument(id);
      setDocs((prev) => prev.filter((d) => d.id !== id));
    } catch { /* keep list intact on failure */ }
    finally {
      setDeleting(false);
      setConfirmDelete(null);
    }
  }

  return (
    <>
      <TopBar
        right={
          <Button
            variant="ghost"
            onClick={async () => {
              await logout();
              router.push("/login");
            }}
          >
            Log out
          </Button>
        }
      />

      <Container className="py-14">
        <div className="mx-auto max-w-2xl">
          <m.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.55, ease: easeSmooth }}
          >
            <p className="eyebrow">Workspace</p>
            <h1 className="t-headline mt-2">Review a document</h1>
            <p className="t-body mt-2.5">
              Upload a loan or subscription agreement to check it for hidden risk.
            </p>

            <div className="mt-9">
              <UploadDropzone onUploaded={(doc) => router.push(`/documents/${doc.id}`)} />
            </div>
          </m.div>

          <div className="mt-16">
            <div className="mb-5 flex items-baseline justify-between">
              <h2 className="t-section">Recent analyses</h2>
              {docs.length > 0 && (
                <span className="t-caption">
                  {docs.length} document{docs.length === 1 ? "" : "s"}
                </span>
              )}
            </div>

            {loading ? (
              <Surface className="divide-y divide-line overflow-hidden">
                {[0, 1, 2].map((i) => <DocRowSkeleton key={i} />)}
              </Surface>
            ) : docs.length === 0 ? (
              <Surface className="flex flex-col items-center px-6 py-16 text-center">
                <span className="flex h-12 w-12 items-center justify-center rounded-2xl bg-brand/[0.07] text-brand">
                  <FileSearch className="h-5 w-5" strokeWidth={1.75} />
                </span>
                <p className="mt-5 text-[0.9375rem] font-medium text-ink">No documents yet</p>
                <p className="t-caption mt-1.5 max-w-xs">
                  Upload your first agreement above and ClearClause will flag the risky clauses.
                </p>
              </Surface>
            ) : (
              <Surface className="divide-y divide-line overflow-hidden">
                <m.div variants={staggerContainer} initial="initial" animate="animate">
                  {docs.map((d) => (
                    <m.div key={d.id} variants={staggerItem} className="group relative">
                      {confirmDelete === d.id ? (
                        <div className="flex items-center justify-between gap-4 px-6 py-[18px]">
                          <p className="text-[0.9375rem] text-ink">
                            Delete <span className="font-medium">{d.original_filename}</span>?
                          </p>
                          <div className="flex shrink-0 gap-2">
                            <button
                              onClick={() => setConfirmDelete(null)}
                              className="rounded-lg border border-line px-3 py-1.5 text-[0.8125rem] font-medium text-ink-2 hover:bg-canvas"
                            >
                              Cancel
                            </button>
                            <button
                              onClick={() => handleDelete(d.id)}
                              disabled={deleting}
                              className="rounded-lg bg-risk-high px-3 py-1.5 text-[0.8125rem] font-semibold text-white disabled:opacity-50 hover:opacity-90"
                            >
                              {deleting ? "Deleting…" : "Delete"}
                            </button>
                          </div>
                        </div>
                      ) : (
                        <Link
                          href={`/documents/${d.id}`}
                          className="flex items-center gap-4 px-6 py-[18px] transition-colors hover:bg-brand/[0.025] focus-visible:bg-brand/[0.04] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-brand/30"
                        >
                          <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-brand/[0.06] text-brand">
                            <FileSearch className="h-4 w-4" strokeWidth={1.75} />
                          </span>
                          <div className="min-w-0 flex-1">
                            <p className="truncate text-[0.9375rem] font-medium text-ink">
                              {d.original_filename}
                            </p>
                            <div className="mt-1 flex items-center gap-2">
                              <p className="t-caption">{fmtDate(d.created_at)}</p>
                              {d.classified_type && <DocTypeBadge type={d.classified_type} />}
                            </div>
                          </div>
                          <StatusBadge status={d.status} />
                          <ChevronRight
                            className="h-4 w-4 text-ink-3 transition-transform duration-200 group-hover:translate-x-0.5 group-hover:text-brand"
                            strokeWidth={1.75}
                          />
                        </Link>
                      )}
                      {confirmDelete !== d.id && (
                        <button
                          onClick={(e) => { e.preventDefault(); setConfirmDelete(d.id); }}
                          aria-label={`Delete ${d.original_filename}`}
                          className="absolute right-12 top-1/2 -translate-y-1/2 rounded-lg p-1.5 text-ink-3 opacity-0 transition hover:bg-canvas hover:text-risk-high group-hover:opacity-100 focus-visible:opacity-100"
                        >
                          <Trash2 className="h-4 w-4" strokeWidth={1.75} />
                        </button>
                      )}
                    </m.div>
                  ))}
                </m.div>
              </Surface>
            )}

            {hasMore && (
              <div className="mt-5 flex justify-center">
                <Button variant="secondary" onClick={loadMore} disabled={loadingMore}>
                  {loadingMore ? "Loading…" : "Load older documents"}
                </Button>
              </div>
            )}
          </div>
        </div>
      </Container>
    </>
  );
}
