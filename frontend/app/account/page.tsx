"use client";
import { Download, Trash2 } from "lucide-react";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { deleteAccount, exportAccount, logout } from "@/lib/api";
import { Button, ButtonLink } from "@/components/ui/Button";
import { Container, Surface } from "@/components/ui/Surface";
import { TopBar } from "@/components/ui/TopBar";

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
    <div className="min-h-screen">
      <TopBar
        right={
          <>
            <ButtonLink variant="ghost" href="/dashboard">
              Workspace
            </ButtonLink>
            <Button
              variant="ghost"
              onClick={async () => {
                await logout();
                router.push("/login");
              }}
            >
              Log out
            </Button>
          </>
        }
      />

      <Container className="py-12">
        <h1 className="t-headline">Your account</h1>
        <p className="t-body mt-2 max-w-prose text-[0.9375rem]">
          Your documents are deleted automatically 7 days after upload. These controls cover
          everything else.
        </p>

        {err && <p className="mt-6 text-sm text-risk-high">{err}</p>}

        <Surface className="mt-8 p-6">
          <h2 className="text-[1.0625rem] font-medium tracking-tight">Download your data</h2>
          <p className="t-body mt-2 max-w-prose text-[0.9375rem]">
            A JSON file containing your account details and every document we still hold,
            with its findings, entities and scores.
          </p>
          <Button variant="secondary" className="mt-5" disabled={exporting} onClick={download}>
            <Download className="h-4 w-4" strokeWidth={2} />
            {exporting ? "Preparing…" : "Download export"}
          </Button>
        </Surface>

        <Surface className="mt-6 border-risk-high/30 p-6">
          <h2 className="text-[1.0625rem] font-medium tracking-tight">Delete your account</h2>
          <p className="t-body mt-2 max-w-prose text-[0.9375rem]">
            This removes your account, every document you have uploaded, and every report
            generated from them. It cannot be undone. Download your data first if you want a
            copy.
          </p>

          {confirming ? (
            <form onSubmit={erase} className="mt-5 flex max-w-sm flex-col gap-3">
              <label className="text-[0.875rem] text-ink-2" htmlFor="confirm-password">
                Enter your password to confirm
              </label>
              <input
                id="confirm-password"
                className="field"
                type="password"
                required
                autoComplete="current-password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
              <div className="flex gap-2">
                <Button disabled={deleting}>
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
          ) : (
            <Button variant="secondary" className="mt-5" onClick={() => setConfirming(true)}>
              <Trash2 className="h-4 w-4" strokeWidth={2} />
              Delete account
            </Button>
          )}
        </Surface>
      </Container>
    </div>
  );
}
