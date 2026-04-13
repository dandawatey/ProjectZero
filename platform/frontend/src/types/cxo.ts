// CXO dashboard types — matches backend schemas/cxo.py

export interface VelocityPoint {
  sprint: string | null;
  committed: number;
  completed: number;
  end_date: string | null;
}

export interface BurndownPoint {
  date: string;
  remaining: number;
}

export interface Burndown {
  sprint: string | null;
  total: number;
  series: BurndownPoint[];
}

export interface AssigneeTickets {
  assignee: string;
  todo: number;
  in_progress: number;
}

export interface CycleTimePoint {
  key: string;
  days: number;
}

export interface IssueTypeCount {
  type: string;
  count: number;
}

export interface ThroughputPoint {
  date: string;
  done: number;
}

export interface ProjectSummary {
  key: string;
  total: number;
  done: number;
  in_progress: number;
  todo: number;
  completion_pct: number;
}

export interface ProjectMetrics {
  summary: ProjectSummary;
  velocity: VelocityPoint[];
  burndown: Burndown;
  assignees: AssigneeTickets[];
  cycle_time: CycleTimePoint[];
  issue_types: IssueTypeCount[];
  throughput: ThroughputPoint[];
  cached: boolean;
}

export interface Portfolio {
  projects: ProjectSummary[];
}
