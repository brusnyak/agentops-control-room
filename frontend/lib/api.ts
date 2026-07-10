const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8001";

export interface ContactRead {
  id: string;
  name: string;
  phone: string | null;
  email: string | null;
  meta: Record<string, unknown> | null;
  created_at: string;
}

export interface WorkflowTemplateRead {
  id: string;
  name: string;
  version: number;
  channel: "email" | "voice_simulated" | "sms_simulated";
  goal_prompt: string;
  eval_rubric: string;
  config: Record<string, unknown> | null;
  created_at: string;
}

export interface RegressionPoint {
  version: number;
  template_id: string;
  run_count: number;
  avg_rule_score: number | null;
  avg_llm_score: number | null;
  pass_rate: number | null;
}

export interface RegressionReport {
  name: string;
  points: RegressionPoint[];
}

export interface CampaignRead {
  id: string;
  workflow_template_id: string;
  name: string;
  status: string;
  created_at: string;
}

export interface MessageRead {
  id: string;
  direction: "outbound" | "inbound";
  provider: string;
  content: string;
  created_at: string;
}

export interface ToolCallRead {
  id: string;
  tool_name: string;
  input: Record<string, unknown> | null;
  output: Record<string, unknown> | null;
  success: boolean;
  created_at: string;
}

export interface RunRead {
  id: string;
  campaign_id: string;
  contact_id: string;
  channel: string;
  state: "pending" | "running" | "completed" | "failed";
  outcome: string | null;
  error_reason: string | null;
  latency_ms: number | null;
  created_at: string;
}

export interface RunDetailRead extends RunRead {
  messages: MessageRead[];
  tool_calls: ToolCallRead[];
}

export interface EvaluationRead {
  id: string;
  run_id: string;
  rule_score: number;
  llm_score: number | null;
  passed: boolean;
  failure_tags: string[] | null;
  notes: string | null;
  created_at: string;
}

export interface DashboardStats {
  campaign_id: string;
  total_runs: number;
  outcome_counts: Record<string, number>;
  failure_reasons: Record<string, number>;
  avg_latency_ms: number | null;
  completed: number;
  failed: number;
  pending: number;
}

export interface ObservabilityStats {
  total_calls: number;
  success_rate: number | null;
  total_prompt_tokens: number;
  total_completion_tokens: number;
  avg_latency_ms: number | null;
  avg_attempts: number | null;
  by_purpose: Record<string, number>;
}

export interface ExportResult {
  delivered: boolean;
  run_count: number;
  status_code: number | null;
  error: string | null;
}

export class ApiError extends Error {
  constructor(
    public status: number,
    public detail: string,
  ) {
    super(detail);
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...init?.headers },
  });
  if (!response.ok) {
    let detail = response.statusText;
    try {
      const body = await response.json();
      detail = body.detail ?? detail;
    } catch {
      // no JSON body
    }
    throw new ApiError(response.status, detail);
  }
  return response.json();
}

export const api = {
  contacts: {
    list: () => request<ContactRead[]>("/contacts"),
    get: (id: string) => request<ContactRead>(`/contacts/${id}`),
    create: (payload: { name: string; email?: string; phone?: string }) =>
      request<ContactRead>("/contacts", { method: "POST", body: JSON.stringify(payload) }),
  },
  workflowTemplates: {
    list: () => request<WorkflowTemplateRead[]>("/workflow-templates"),
    get: (id: string) => request<WorkflowTemplateRead>(`/workflow-templates/${id}`),
    create: (payload: {
      name: string;
      channel: string;
      goal_prompt: string;
      eval_rubric: string;
      version?: number;
    }) => request<WorkflowTemplateRead>("/workflow-templates", { method: "POST", body: JSON.stringify(payload) }),
    regression: (name: string) =>
      request<RegressionReport>(`/workflow-templates/regression?name=${encodeURIComponent(name)}`),
  },
  campaigns: {
    list: () => request<CampaignRead[]>("/campaigns"),
    get: (id: string) => request<CampaignRead>(`/campaigns/${id}`),
    create: (payload: { workflow_template_id: string; name: string }) =>
      request<CampaignRead>("/campaigns", { method: "POST", body: JSON.stringify(payload) }),
    export: (id: string, webhookUrl: string) =>
      request<ExportResult>(`/campaigns/${id}/export`, {
        method: "POST",
        body: JSON.stringify({ webhook_url: webhookUrl }),
      }),
  },
  runs: {
    list: (campaignId?: string) =>
      request<RunRead[]>(`/runs${campaignId ? `?campaign_id=${campaignId}` : ""}`),
    get: (id: string) => request<RunDetailRead>(`/runs/${id}`),
    create: (payload: { campaign_id: string; contact_id: string }) =>
      request<RunRead>("/runs", { method: "POST", body: JSON.stringify(payload) }),
  },
  evals: {
    create: (runId: string) => request<EvaluationRead>(`/evals/${runId}`, { method: "POST" }),
    list: (runId: string) => request<EvaluationRead[]>(`/evals/${runId}`),
  },
  dashboard: {
    get: (campaignId: string) => request<DashboardStats>(`/dashboard/${campaignId}`),
  },
  observability: {
    stats: () => request<ObservabilityStats>("/observability/stats"),
  },
};
