"use client";
import { motion } from "framer-motion";
import { ChevronRight, FileSearch } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useCallback, useEffect, useState } from "react";
import { clearToken, getToken, listDocuments, type Doc } from "@/lib/api";
import UploadDropzone from "@/components/UploadDropzone";
import { Button } from "@/components/ui/Button";
import { Container, Surface } from "@/components/ui/Surface";
import { TopBar } from "@/components/ui/TopBar";

function statusMeta(status: string): { label: string; color: string; tint: string } {
  if (status === "report_ready") return { label: "Reviewed", color: "#1a7f5a", tint: "#e9f5ef" };
  if (status === "failed") return { label: "Failed", color: "#c0362c", tint: "#fdeceb" };
  return { label: "Analyzing", color: "#b2670a", tint: "#fbf2e6" };
}

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

  const refresh = useCallback(() => {
    listDocuments()
      .then(setDocs)
      .catch(() => router.push("/login"))
      .finally(() => setLoading(false));
  }, [router]);

  useEffect(() => {
    if (!getToken()) {
      router.push("/login");
      return;
    }
    refresh();
  }, [router, refresh]);

  return (
    <>
      <TopBar
        right={
          <Button
            variant="ghost"
            onClick={() => {
              clearToken();
              router.push("/login");
            }}
          >
            Log out
          </Button>
        }
      />

      <Container className="py-14">
        <div className="mx-auto max-w-2xl">
          <p className="eyebrow">Workspace</p>
          <h1 className="t-headline mt-2">Review a document</h1>
          <p className="t-body mt-2.5">Upload a loan or subscription agreement to check it for hidden risk.</p>

          <div className="mt-9">
            <UploadDropzone onUploaded={(doc) => router.push(`/documents/${doc.id}`)} />
          </div>

          <div className="mt-16">
            <div className="mb-5 flex items-baseline justify-between">
              <h2 className="t-section">Recent analyses</h2>
              {docs.length > 0 && (
                <span className="t-caption">{docs.length} document{docs.length === 1 ? "" : "s"}</span>
              )}
            </div>

            {loading ? (
              <p className="t-body">Loading…</p>
            ) : docs.length === 0 ? (
              <Surface className="flex flex-col items-center px-6 py-16 text-center">
                <span className="flex h-12 w-12 items-center justify-center rounded-2xl bg-canvas text-ink-3">
                  <FileSearch className="h-5 w-5" strokeWidth={1.75} />
                </span>
                <p className="mt-5 text-[0.9375rem] font-medium text-ink">No documents yet</p>
                <p className="t-caption mt-1.5 max-w-xs">
                  Upload your first agreement above and ClearClause will flag the risky clauses.
                </p>
              </Surface>
            ) : (
              <Surface className="divide-y divide-line overflow-hidden">
                {docs.map((d, i) => {
                  const s = statusMeta(d.status);
                  return (
                    <motion.div
                      key={d.id}
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      transition={{ delay: Math.min(i * 0.03, 0.3) }}
                    >
                      <Link
                        href={`/documents/${d.id}`}
                        className="group flex items-center gap-4 px-6 py-[18px] transition-colors hover:bg-canvas"
                      >
                        <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-canvas text-ink-3">
                          <FileSearch className="h-4 w-4" strokeWidth={1.75} />
                        </span>
                        <div className="min-w-0 flex-1">
                          <p className="truncate text-[0.9375rem] font-medium text-ink">
                            {d.original_filename}
                          </p>
                          <p className="t-caption mt-0.5">{fmtDate(d.created_at)}</p>
                        </div>
                        <span
                          className="inline-flex items-center gap-1.5 rounded-md px-2.5 py-1 text-[0.75rem] font-medium"
                          style={{ color: s.color, backgroundColor: s.tint }}
                        >
                          <span className="h-1.5 w-1.5 rounded-full" style={{ backgroundColor: s.color }} />
                          {s.label}
                        </span>
                        <ChevronRight
                          className="h-4 w-4 text-ink-3 transition-transform duration-200 group-hover:translate-x-0.5"
                          strokeWidth={1.75}
                        />
                      </Link>
                    </motion.div>
                  );
                })}
              </Surface>
            )}
          </div>
        </div>
      </Container>
    </>
  );
}
