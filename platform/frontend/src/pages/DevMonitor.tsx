import { useQuery } from '@tanstack/react-query';

const api = {
  overview: () => fetch('/api/v1/dev/overview').then(r => r.json()),
  worktrees: () => fetch('/api/v1/dev/worktrees').then(r => r.json()),
  liveAgents: () => fetch('/api/v1/dev/agents/live').then(r => r.json()),
  stats: () => fetch('/api/v1/dev/stats').then(r => r.json()),
  tmuxOutput: (session: string) => fetch(`/api/v1/dev/tmux/${session}/output`).then(r => r.json()),
};

function StatCard({ label, value, color }: { label: string; value: string | number; color: string }) {
  return (
    <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
      <p className="text-gray-400 text-xs uppercase tracking-wide">{label}</p>
      <p className={`text-3xl font-bold mt-1 ${color}`}>{value}</p>
    </div>
  );
}

function LiveAgents() {
  const { data } = useQuery({ queryKey: ['live-agents'], queryFn: api.liveAgents, refetchInterval: 5000 });
  if (!data?.active_agents?.length) return (
    <div className="bg-gray-800 rounded-lg p-6 border border-gray-700 text-center text-gray-500">
      No agents active
    </div>
  );
  return (
    <div className="bg-gray-800 rounded-lg border border-gray-700">
      <div className="px-4 py-3 border-b border-gray-700 flex items-center gap-2">
        <span className="h-2 w-2 rounded-full bg-green-500 animate-pulse" />
        <h3 className="text-white font-medium">Live Agents ({data.count})</h3>
      </div>
      <div className="divide-y divide-gray-700/50">
        {data.active_agents.map((a: any, i: number) => (
          <div key={i} className="px-4 py-3 flex items-center justify-between">
            <div>
              <span className="text-blue-400 font-medium">{a.agent_type}</span>
              <span className="text-gray-500 mx-2">→</span>
              <span className="text-gray-300">{a.working_on}</span>
            </div>
            <span className="text-gray-500 text-xs font-mono">
              {Math.round(a.duration_seconds)}s
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

function Worktrees() {
  const { data } = useQuery({ queryKey: ['worktrees'], queryFn: api.worktrees, refetchInterval: 10000 });
  if (!data?.worktrees?.length) return null;
  return (
    <div className="bg-gray-800 rounded-lg border border-gray-700">
      <div className="px-4 py-3 border-b border-gray-700">
        <h3 className="text-white font-medium">Git Worktrees</h3>
      </div>
      <div className="divide-y divide-gray-700/50">
        {data.worktrees.map((wt: any, i: number) => (
          <div key={i} className="px-4 py-3">
            <div className="flex items-center justify-between">
              <div>
                <span className="font-mono text-sm text-cyan-400">{wt.branch}</span>
                <span className="text-gray-600 text-xs ml-2">{wt.path}</span>
              </div>
              <div className="flex items-center gap-2">
                {wt.tmux_active ? (
                  <span className="px-2 py-0.5 rounded text-xs bg-green-900 text-green-300">tmux active</span>
                ) : (
                  <span className="px-2 py-0.5 rounded text-xs bg-gray-700 text-gray-400">no session</span>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function ActiveWorkflows() {
  const { data } = useQuery({ queryKey: ['dev-overview'], queryFn: api.overview, refetchInterval: 5000 });
  if (!data?.active_workflows?.length) return null;
  return (
    <div className="bg-gray-800 rounded-lg border border-gray-700">
      <div className="px-4 py-3 border-b border-gray-700">
        <h3 className="text-white font-medium">Active Workflows</h3>
      </div>
      <table className="w-full text-sm">
        <thead className="text-gray-400 border-b border-gray-700">
          <tr>
            <th className="px-4 py-2 text-left">Feature</th>
            <th className="px-4 py-2 text-left">Type</th>
            <th className="px-4 py-2 text-left">Stage</th>
            <th className="px-4 py-2 text-left">Product</th>
          </tr>
        </thead>
        <tbody>
          {data.active_workflows.map((w: any) => (
            <tr key={w.id} className="border-b border-gray-700/50 hover:bg-gray-700/30">
              <td className="px-4 py-2 text-blue-400 font-mono text-xs">{w.feature_id}</td>
              <td className="px-4 py-2 text-gray-300">{w.type}</td>
              <td className="px-4 py-2">
                <span className="px-2 py-0.5 rounded text-xs bg-blue-900 text-blue-300">{w.stage}</span>
              </td>
              <td className="px-4 py-2 text-gray-400">{w.product_id}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function RecentContributions() {
  const { data } = useQuery({ queryKey: ['dev-overview'], queryFn: api.overview, refetchInterval: 5000 });
  if (!data?.recent_contributions?.length) return null;
  return (
    <div className="bg-gray-800 rounded-lg border border-gray-700">
      <div className="px-4 py-3 border-b border-gray-700">
        <h3 className="text-white font-medium">Recent Agent Work</h3>
      </div>
      <div className="divide-y divide-gray-700/50 max-h-96 overflow-y-auto">
        {data.recent_contributions.map((c: any, i: number) => (
          <div key={i} className="px-4 py-2 flex items-center justify-between">
            <div>
              <span className="text-cyan-400 text-sm">{c.agent_type}</span>
              <span className="text-gray-500 mx-2">|</span>
              <span className="text-gray-300 text-sm">{c.action}</span>
            </div>
            <div className="flex items-center gap-3">
              <span className={`text-xs ${c.result === 'success' ? 'text-green-400' : 'text-red-400'}`}>
                {c.result}
              </span>
              <span className="text-gray-500 text-xs">{c.duration_ms}ms</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default function DevMonitor() {
  const { data: stats } = useQuery({ queryKey: ['dev-stats'], queryFn: api.stats, refetchInterval: 30000 });

  return (
    <div>
      <div className="flex items-center gap-3 mb-6">
        <h1 className="text-2xl font-bold text-white">Developer Monitor</h1>
        <span className="h-2 w-2 rounded-full bg-green-500 animate-pulse" />
        <span className="text-gray-500 text-sm">Live</span>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <StatCard label="Workflows Today" value={stats?.workflows_completed_today ?? 0} color="text-green-400" />
        <StatCard label="Steps Today" value={stats?.steps_completed_today ?? 0} color="text-blue-400" />
        <StatCard label="Agent Actions (7d)" value={stats?.agent_contributions_this_week ?? 0} color="text-cyan-400" />
        <StatCard label="Avg Step Duration" value={`${stats?.avg_step_duration_ms ?? 0}ms`} color="text-yellow-400" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="space-y-6">
          <LiveAgents />
          <Worktrees />
        </div>
        <div className="space-y-6">
          <ActiveWorkflows />
          <RecentContributions />
        </div>
      </div>
    </div>
  );
}
