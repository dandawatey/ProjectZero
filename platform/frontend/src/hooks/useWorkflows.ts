import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../services/api';

export function useDashboard() {
  return useQuery({
    queryKey: ['dashboard'],
    queryFn: api.dashboard,
  });
}

export function useWorkflows() {
  return useQuery({
    queryKey: ['workflows'],
    queryFn: api.workflows.list,
  });
}

export function useWorkflow(id: string) {
  return useQuery({
    queryKey: ['workflow', id],
    queryFn: () => api.workflows.get(id),
    enabled: !!id,
  });
}

export function useWorkflowSteps(id: string) {
  return useQuery({
    queryKey: ['workflow-steps', id],
    queryFn: () => api.workflows.steps(id),
    enabled: !!id,
  });
}

export function useStartWorkflow() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: api.workflows.start,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['workflows'] });
      qc.invalidateQueries({ queryKey: ['dashboard'] });
    },
  });
}

export function useRetryWorkflow() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: api.workflows.retry,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['workflows'] });
      qc.invalidateQueries({ queryKey: ['dashboard'] });
    },
  });
}

export function usePendingApprovals() {
  return useQuery({
    queryKey: ['approvals-pending'],
    queryFn: api.approvals.pending,
  });
}

export function useResolveApproval() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: { action: string; comment?: string } }) =>
      api.approvals.resolve(id, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['approvals-pending'] });
      qc.invalidateQueries({ queryKey: ['dashboard'] });
    },
  });
}

export function useAgentContributions(wfId?: string) {
  return useQuery({
    queryKey: ['agent-contributions', wfId],
    queryFn: () => (wfId ? api.agents.contributions(wfId) : api.agents.all()),
  });
}

export function useArtifacts(wfId?: string) {
  return useQuery({
    queryKey: ['artifacts', wfId],
    queryFn: () => api.artifacts.list(wfId),
  });
}

export function useAuditLog() {
  return useQuery({
    queryKey: ['audit'],
    queryFn: api.audit.list,
  });
}
