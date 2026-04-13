export interface WorkflowRun {
  id: string;
  workflow_type: string;
  feature_id: string;
  product_id: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'blocked';
  current_stage: string;
  temporal_run_id: string | null;
  created_at: string;
  updated_at: string;
}

export interface WorkflowStep {
  id: string;
  workflow_run_id: string;
  stage_name: string;
  status: 'pending' | 'in_progress' | 'completed' | 'failed' | 'skipped';
  agent_type: string | null;
  agent_id: string | null;
  started_at: string | null;
  completed_at: string | null;
  error_message: string | null;
}

export interface Approval {
  id: string;
  workflow_run_id: string;
  stage_name: string;
  approval_type: 'checker' | 'reviewer' | 'approver';
  status: 'pending' | 'approved' | 'rejected';
  requested_at: string;
  resolved_at: string | null;
  resolved_by: string | null;
}

export interface AgentContribution {
  id: string;
  workflow_run_id: string;
  step_id: string;
  agent_type: string;
  agent_id: string;
  action: string;
  result: string;
  duration_ms: number;
  created_at: string;
}

export interface DashboardSummary {
  active: number;
  completed: number;
  failed: number;
  blocked: number;
  pending_approvals: number;
  recent_runs: WorkflowRun[];
}
