const BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";
const TOKEN_KEY = "cc_token";

export type Doc = {
  id: number;
  original_filename: string;
  source_type: string;
  doc_type: string | null;
  status: string;
  created_at: string;
};

export type Finding = {
  id: number;
  clause_id: number | null;
  issue_type: string;
  severity: string;
  confidence: number;
  explanation: string;
  action_text: string;
  clause_text: string | null;
};

export type Score = {
  total_score: number;
  band: string;
  summary: string;
  breakdown: {
    fee_opacity: number;
    penalty: number;
    renewal: number;
    consent: number;
    cancellation: number;
  };
  cost: Record<string, number | null>;
};

export const getToken = () =>
  typeof window === "undefined" ? null : localStorage.getItem(TOKEN_KEY);
export const setToken = (t: string) => localStorage.setItem(TOKEN_KEY, t);
export const clearToken = () => localStorage.removeItem(TOKEN_KEY);

async function req(path: string, opts: RequestInit = {}, auth = true): Promise<Response> {
  const headers: Record<string, string> = { ...(opts.headers as Record<string, string>) };
  if (auth) {
    const t = getToken();
    if (t) headers["Authorization"] = `Bearer ${t}`;
  }
  const res = await fetch(`${BASE}${path}`, { ...opts, headers });
  if (!res.ok) {
    let detail: unknown = res.statusText;
    try {
      detail = (await res.json()).detail;
    } catch {
      /* keep statusText */
    }
    throw new Error(typeof detail === "string" ? detail : "Request failed");
  }
  return res;
}

const json = (path: string, body: unknown) =>
  req(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  }, false);

export const register = (email: string, password: string) =>
  json("/api/v1/auth/register", { email, password });

export async function login(email: string, password: string) {
  const res = await json("/api/v1/auth/login", { email, password });
  setToken((await res.json()).access_token);
}

export const listDocuments = async (): Promise<Doc[]> =>
  (await req("/api/v1/documents")).json();

export const getDocument = async (id: number): Promise<Doc> =>
  (await req(`/api/v1/documents/${id}`)).json();

export async function uploadDocument(file: File): Promise<Doc> {
  const fd = new FormData();
  fd.append("file", file);
  return (await req("/api/v1/documents/upload", { method: "POST", body: fd })).json();
}

export const deleteDocument = (id: number) =>
  req(`/api/v1/documents/${id}`, { method: "DELETE" });

export const analyzeDocument = async (id: number): Promise<{ status: string }> =>
  (await req(`/api/v1/documents/${id}/analyze`, { method: "POST" })).json();

export const getFindings = async (id: number): Promise<Finding[]> =>
  (await req(`/api/v1/documents/${id}/findings`)).json();

export async function getScore(id: number): Promise<Score | null> {
  try {
    return await (await req(`/api/v1/documents/${id}/score`)).json();
  } catch {
    return null; // not scored yet
  }
}

export const fetchReportBlob = async (id: number): Promise<Blob> =>
  (await req(`/api/v1/documents/${id}/report`)).blob();
