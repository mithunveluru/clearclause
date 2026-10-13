"use client";
import { Download, Trash2 } from "lucide-react";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { deleteAccount, exportAccount } from "@/lib/api";
import { AppShell, PageHeader } from "@/components/AppShell";
import { Button } from "@/components/ui/Button";
import { Notice, PasswordField } from "@/components/ui/Form";

export default function AccountPage() {
  const router = useRouter();
  const [exporting, setExporting] = useState(false);
  const [confirming, setConfirming] = useState(false);
  const [password, setPassword] = useState("");
  const [deleting, setDeleting] = useState(false);
  const [err, setErr] = useState("");

  useEffect(() => { document.title = "Account — ClearClause"; }, []);

  async function download() {
    setErr("");
    setExporting(true);
    try {
      const data = await exportAccount();
      // Built in the browser: the export is already in memory, and routing it
      // back through a server would be a second copy of the same private data
      const url = URL.createObjectURL(
        new Blob([JSON.stringify(data, null, 2)], { type: "application/json" }),
      );
      const link = document.createElement("a");
      link.href = url;
      link.download = `clearclause-export-${new Date().toISOString().slice(0, 10)}.json`;
      link.click();
      URL.revokeObjectURL(url);
    } catch (e) {
      setErr((e as Error).message);
    } finally {
      setExporting(false);
    }
  }

  async function erase(e: React.FormEvent) {
    e.preventDefault();
    setErr("");
    setDeleting(true);
    try {
      await deleteAccount(password);
      router.push("/");
    } catch (e) {
      setErr((e as Error).message);
      setDeleting(false);
    }
  }

  return (
    <AppShell crumbs={[{ label: "Account" }]}>
      <div className="mx-auto max-w-3xl px-4 py-8 sm:px-6 sm:py-10">
        <PageHeader
          title="Account"
          description="Documents are deleted automatically seven days after upload. These controls cover everything else."
        />

        {err && <div className="mt-6"><Notice>{err}</Notice></div>}

        <div className="mt-8 divide-y divide-line rounded-xl border border-line bg-surface">
          <section className="grid gap-4 p-5 sm:grid-cols-[1fr_auto] sm:items-start sm:p-6">
            <div>
              <h2 className="text-[0.9375rem] font-semibold tracking-tight">Download your data</h2>
              <p className="mt-1 max-w-prose text-[0.875rem] leading-relaxed text-ink-2">
                A JSON file containing your account details and every document we still hold,
                with its findings, entities and scores.
              </p>
            </div>
            <Button variant="secondary" disabled={exporting} onClick={download}>
              <Download className="h-4 w-4" strokeWidth={1.75} aria-hidden />
              {exporting ? "Preparing…" : "Download export"}
            </Button>
          </section>

          <section className="p-5 sm:p-6">
            <div className="grid gap-4 sm:grid-cols-[1fr_auto] sm:items-start">
              <div>
                <h2 className="text-[0.9375rem] font-semibold tracking-tight text-risk-high">Delete your account</h2>
                <p className="mt-1 max-w-prose text-[0.875rem] leading-relaxed text-ink-2">
                  Removes your account, every document you have uploaded, and every report
                  generated from them. This cannot be undone. Download your data first if you
                  want a copy.
                </p>
              </div>
              {!confirming && (
                <Button variant="secondary" onClick={() => setConfirming(true)}>
                  <Trash2 className="h-4 w-4" strokeWidth={1.75} aria-hidden />
                  Delete account
                </Button>
              )}
            </div>

            {confirming && (
              <form onSubmit={erase} className="mt-5 max-w-sm space-y-3 rounded-lg border border-risk-high/25 bg-risk-high-tint/50 p-4">
                <PasswordField
                  label="Enter your password to confirm"
                  required
                  autoFocus
                  autoComplete="current-password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
                <div className="flex gap-2">
                  <Button variant="danger" disabled={deleting}>
                    {deleting ? "Deleting…" : "Delete everything"}
                  </Button>
                  <Button
                    type="button"
                    variant="ghost"
                    disabled={deleting}
                    onClick={() => { setConfirming(false); setPassword(""); setErr(""); }}
                  >
                    Cancel
                  </Button>
                </div>
              </form>
            )}
          </section>
        </div>
      </div>
    </AppShell>
  );
}
