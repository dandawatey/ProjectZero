/**
 * Authenticated API client — PRJ0-29.
 *
 * Token lifecycle:
 *  - AuthContext calls setTokenGetter() at mount to inject the getter + refresh fn.
 *  - Every request attaches Authorization: Bearer <token>.
 *  - On 401: call refreshAccessToken() once, retry with new token.
 *  - On second 401: redirect to /login.
 */

import type {
  DashboardSummary,
  WorkflowRun,
  WorkflowStep,
  Approval,
  AgentContribution,
} from '../types/workflow';
import type { Portfolio, ProjectMetrics } from '../types/cxo';

const BASE = '/api/v1';

// Injected by AuthContext — avoids circular import
let _getToken: (() => string | null) | null = null;
let _refreshToken: (() => Promise<string | null>) | null = null;

export function setTokenGetter(
  getter: () => string | null,
  refresher: () => Promise<string | null>,
) {
  _getToken = getter;
  _refreshToken = refresher;
}

function authHeaders(token: string | null): Record<string, string> {
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function request<T>(path: string, init: RequestInit = {}, retry = true): Promise<T> {
  const token = _getToken?.() ?? null;
  const r = await fetch(BASE + path, {
    credentials: 'include',
    ...init,
    headers: {
      'Content-Type': 'application/json',
      ...authHeaders(token),
      ...init.headers,
    },
  });

  if (r.status === 401 && retry && _refreshToken) {
    const newToken = await _refreshToken();
    if (!newToken) {
      window.location.href = '/login';
      throw new Error('Session expired');
    }
    return request<T>(path, init, false); // retry once with refreshed token
  }

  if (!r.ok) throw new Error(r.statusText);
  if (r.status === 204) return undefined as T;
  return r.json();
}

function get<T>(path: string) {
  return request<T>(path);
}

function post<T>(path: string, body?: unknown) {
  return request<T>(path, {
    method: 'POST',
    body: body ? JSON.stringify(body) : undefined,
  });
}

function patch<T>(path: string, body?: unknown) {
  return request<T>(path, {
    method: 'PATCH',
    body: body ? JSON.stringify(body) : undefined,
  });
}

export const api = {
  dashboard: () => get<DashboardSummary>('/dashboard/summary'),

  workflows: {
    list: () => get<WorkflowRun[]>('/workflows'),
    get: (id: string) => get<WorkflowRun>(`/workflows/${id}`),
    start: (data: Record<string, unknown>) => post<WorkflowRun>('/workflows/start', data),
    steps: (id: string) => get<WorkflowStep[]>(`/workflows/${id}/steps`),
    retry: (id: string) => post<WorkflowRun>(`/workflows/${id}/retry`),
  },

  approvals: {
    pending: () => get<Approval[]>('/approvals/pending'),
    resolve: (id: string, data: { action: string; comment?: string }) =>
      post<Approval>(`/approvals/${id}/resolve`, data),
  },

  agents: {
    contributions: (wfId: string) => get<AgentContribution[]>(`/agents/contributions/${wfId}`),
    all: () => get<AgentContribution[]>('/agents/contributions'),
  },

  artifacts: {
    list: (wfId?: string) =>
      get<Record<string, unknown>[]>(wfId ? `/artifacts?workflow_id=${wfId}` : '/artifacts'),
  },

  audit: {
    list: () => get<Record<string, unknown>[]>('/audit'),
  },

  cxo: {
    portfolio: () => get<Portfolio>('/cxo/portfolio'),
    project: (key: string) => get<ProjectMetrics>(`/cxo/projects/${key}`),
    refresh: (key: string) => post<ProjectMetrics>(`/cxo/projects/${key}/refresh`),
  },

  agentRegistry: {
    list: () => get<Record<string, unknown>[]>('/agents'),
    skills: () => get<Record<string, unknown>[]>('/agents/skills'),
    executions: (limit = 50) => get<Record<string, unknown>[]>(`/agents/executions?limit=${limit}`),
    patch: (agent_id: string, body: Record<string, unknown>) =>
      patch<Record<string, unknown>>(`/agents/${agent_id}`, body),
  },
};
