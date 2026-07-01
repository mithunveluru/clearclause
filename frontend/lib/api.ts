const BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

export type Doc = {
  id: number;
  original_filename: string;
  source_type: string;
  doc_type: string | null;
  classified_type: string | null;
  document_family: string | null;
  status: string;
  qa_ready: boolean;
  ai_summary_ready: boolean;
  created_at: string;
};

export type Finding = {
  id: number;
  clause_id: number | null;
  issue_type: string;
  severity: string;
  confidence: number;
  explanation: string;
  impact: string | null;
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

export type Entity = {
  entity_type: string;
  entity_value: string;
  confidence: number;
  page_number: number | null;
  source_text: string | null;
};

export type Analysis = {
  analyzer_type: string;
  status: string;
  result: {
    analyzer: string;
    family?: string;
    headline_metric?: { name: string; value: number; band: string } | null;
    summary?: string | null;
    strengths?: string[];
    recommendations?: string[];
  } | null;
};

export type AISummary = { content: string; model: string | null; created_at: string };

export type Citation = { page: number | null; section: string | null; snippet: string };
export type QAAnswer = { answer: string; citations: Citation[]; confidence_note: string };

export type ExplorerClause = {
  clause_id: number | null;
  finding_id: number | null;
  original_text: string | null;
  plain_english: string;
  why_it_matters: string | null;
  action_text: string;
  issue_type: string;
  risk_level: string;
  confidence: number;
  page_number: number | null;
};

export type ExplorerSection = {
  id: string;
  label: string;
  icon: string;
  risk_level: string;
  item_count: number;
  clauses: ExplorerClause[];
  summary: string;
};

export type TimelineEvent = {
  label: string;
  value: string;
  entity_type: string;
  event_type: string;
  description: string;
};

export type SuggestedQuestion = {
  question: string;
  category: string;
  finding_id: number | null;
};

export type WalkthroughStep = {
  step: number;
  title: string;
  description: string;
  section_id: string;
  insight: string;
};

export type FinancialImpact = {
  upfront_costs: { label: string; value: string }[];
  recurring_costs: { label: string; value: string }[];
  penalties: { label: string; value: string }[];
  hidden_risks: string[];
  total_note: string | null;
};

export type ExplorerDoc = {
  doc_id: number;
  doc_type: string | null;
  document_family: string | null;
  risk_score: number | null;
  risk_band: string | null;
  sections: ExplorerSection[];
  financial_impact: FinancialImpact;
  timeline: TimelineEvent[];
  suggested_questions: SuggestedQuestion[];
  walkthrough: WalkthroughStep[];
  entity_highlights: { label: string; value: string; type: string }[];
  analysis_summary: string | null;
  strengths: string[];
  recommendations: string[];
};

// Deduplicate concurrent refreshes
let _refreshing: Promise<boolean> | null = null;

async function _tryRefresh(): Promise<boolean> {
  try {
    const res = await fetch(`${BASE}/api/v1/auth/refresh`, {
      method: "POST",
      credentials: "include",
    });
    return res.ok;
  } catch {
    return false;
  }
}

async function req(path: string, opts: RequestInit = {}, _retried = false): Promise<Response> {
  const res = await fetch(`${BASE}${path}`, {
    ...opts,
    credentials: "include",
    headers: opts.headers as HeadersInit | undefined,
  });

  // Retry once after silent refresh; skip auth endpoints to avoid loops
  if (res.status === 401 && !_retried && !path.includes("/api/v1/auth/")) {
    if (!_refreshing) _refreshing = _tryRefresh().finally(() => { _refreshing = null; });
    const ok = await _refreshing;
    if (ok) return req(path, opts, true);
    if (typeof window !== "undefined") window.location.href = "/login";
    throw new Error("Session expired");
  }

  if (!res.ok) {
    let detail: unknown = res.statusText;
    try { detail = (await res.json()).detail; } catch { /* keep statusText */ }
    throw new Error(typeof detail === "string" ? detail : "Request failed");
  }
  return res;
}

export async function register(email: string, password: string): Promise<void> {
  const res = await fetch(`${BASE}/api/v1/auth/register`, {
    method: "POST",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  if (!res.ok) {
    let detail: unknown = res.statusText;
    try { detail = (await res.json()).detail; } catch { /* keep statusText */ }
    throw new Error(typeof detail === "string" ? detail : "Registration failed");
  }
}

export async function login(email: string, password: string): Promise<void> {
  const res = await fetch(`${BASE}/api/v1/auth/login`, {
    method: "POST",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  if (!res.ok) {
    let detail: unknown = res.statusText;
    try { detail = (await res.json()).detail; } catch { /* keep statusText */ }
    throw new Error(typeof detail === "string" ? detail : "Invalid email or password");
  }
  // server sets httpOnly cookies
}

export async function logout(): Promise<void> {
  await fetch(`${BASE}/api/v1/auth/logout`, { method: "POST", credentials: "include" });
}

export async function checkAuth(): Promise<boolean> {
  try {
    const res = await fetch(`${BASE}/api/v1/me`, { credentials: "include" });
    return res.ok;
  } catch {
    return false;
  }
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

export async function getFindings(id: number): Promise<Finding[]> {
  try {
    return await (await req(`/api/v1/documents/${id}/findings`)).json();
  } catch {
    return [];
  }
}

export async function getScore(id: number): Promise<Score | null> {
  try {
    return await (await req(`/api/v1/documents/${id}/score`)).json();
  } catch {
    return null;
  }
}

export const fetchReportBlob = async (id: number): Promise<Blob> =>
  (await req(`/api/v1/documents/${id}/report`)).blob();

export async function getEntities(id: number): Promise<Entity[]> {
  try {
    return await (await req(`/api/v1/documents/${id}/entities`)).json();
  } catch {
    return [];
  }
}

export async function getAnalysis(id: number): Promise<Analysis | null> {
  try {
    return await (await req(`/api/v1/documents/${id}/analysis`)).json();
  } catch {
    return null;
  }
}

export async function getAiSummary(id: number): Promise<AISummary | null> {
  try {
    return await (await req(`/api/v1/documents/${id}/ai-summary`)).json();
  } catch {
    return null;
  }
}

export async function askQuestion(id: number, question: string): Promise<QAAnswer> {
  const res = await req(`/api/v1/documents/${id}/qa`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });
  return res.json();
}

export async function getExplorer(id: number): Promise<ExplorerDoc | null> {
  try {
    return await (await req(`/api/v1/documents/${id}/explorer`)).json();
  } catch {
    return null;
  }
}
