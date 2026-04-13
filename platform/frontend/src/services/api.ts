import type {
  DashboardSummary,
  WorkflowRun,
  WorkflowStep,
  Approval,
  AgentContribution,
} from '../types/workflow';

const BASE = '/api/v1';

async function get<T>(path: string): Promise<T> {
  const r = await fetch(BASE + path);
  if (!r.ok) throw new Error(r.statusText);
  return r.json();
}

async function post<T>(path: string, body?: unknown): Promise<T> {
  const r = await fetch(BASE + path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!r.ok) throw new Error(r.statusText);
  return r.json();
}

export const api = {
  dashboard: () => get<DashboardSummary>('/dashboard/summary'),

  workflows: {
    list: () => get<WorkflowRun[]>('/workflows'),
    get: (id: string) => get<WorkflowRun>(`/workflows/${id}`),
    start: (data: Record<string, unknown>) =>
      post<WorkflowRun>('/workflows/start', data),
    steps: (id: string) => get<WorkflowStep[]>(`/workflows/${id}/steps`),
    retry: (id: string) => post<WorkflowRun>(`/workflows/${id}/retry`),
  },

  approvals: {
    pending: () => get<Approval[]>('/approvals/pending'),
    resolve: (id: string, data: { action: string; comment?: string }) =>
      post<Approval>(`/approvals/${id}/resolve`, data),
  },

  agents: {
    contributions: (wfId: string) =>
      get<AgentContribution[]>(`/agents/contributions/${wfId}`),
    all: () => get<AgentContribution[]>('/agents/contributions'),
  },

  artifacts: {
    list: (wfId?: string) =>
      get<Record<string, unknown>[]>(
        wfId ? `/artifacts?workflow_id=${wfId}` : '/artifacts',
      ),
  },

  audit: {
    list: () => get<Record<string, unknown>[]>('/audit'),
  },
};
