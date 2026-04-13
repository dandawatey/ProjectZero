import { useQuery } from '@tanstack/react-query';

const fetchSummary = (hours: number) => 
  fetch(`/api/v1/activities/summary?hours=${hours}`).then(r => r.json());

const fetchActivities = (hours: number) =>
  fetch(`/api/v1/activities/?hours=${hours}&limit=100`).then(r => r.json());

function StatCard({ label, value, color }: { label: string; value: number | string; color: string }) {
  return (
    <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
      <p className="text-gray-400 text-sm">{label}</p>
      <p className={`text-2xl font-bold ${color}`}>{value}</p>
    </div>
  );
}

function CategoryBar({ categories }: { categories: Record<string, number> }) {
  const total = Object.values(categories).reduce((a, b) => a + b, 0);
  if (total === 0) return <p className="text-gray-500 text-sm">No activity</p>;
  const colors: Record<string, string> = {
    workflow: 'bg-blue-500', approval: 'bg-yellow-500', command: 'bg-purple-500',
    navigation: 'bg-gray-500', integration: 'bg-green-500', agent: 'bg-cyan-500',
  };
  return (
    <div className="space-y-2">
      <div className="flex h-4 rounded overflow-hidden">
        {Object.entries(categories).map(([cat, count]) => (
          <div key={cat} className={`${colors[cat] || 'bg-gray-600'}`} style={{ width: `${(count / total) * 100}%` }} />
        ))}
      </div>
      <div className="flex flex-wrap gap-3 text-xs">
        {Object.entries(categories).map(([cat, count]) => (
          <span key={cat} className="flex items-center gap-1">
            <span className={`h-2 w-2 rounded-full ${colors[cat] || 'bg-gray-600'}`} />
            <span className="text-gray-400">{cat}: {count}</span>
          </span>
        ))}
      </div>
    </div>
  );
}

export default function ActivityMonitor() {
  const { data: summary } = useQuery({ queryKey: ['activity-summary'], queryFn: () => fetchSummary(24), refetchInterval: 10000 });
  const { data: activities } = useQuery({ queryKey: ['activity-list'], queryFn: () => fetchActivities(24), refetchInterval: 10000 });

  return (
    <div>
      <h1 className="text-2xl font-bold text-white mb-6">Activity Monitor</h1>

      {/* Summary cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <StatCard label="Total Activities (24h)" value={summary?.total_activities ?? 0} color="text-white" />
        <StatCard label="Active Users" value={summary?.active_users ?? 0} color="text-blue-400" />
        <StatCard label="Successful" value={summary?.by_status?.success ?? 0} color="text-green-400" />
        <StatCard label="Failed" value={summary?.by_status?.failed ?? 0} color="text-red-400" />
      </div>

      {/* Category breakdown */}
      <div className="bg-gray-800 rounded-lg p-4 border border-gray-700 mb-6">
        <h3 className="text-sm font-medium text-gray-400 mb-3">Activity by Category</h3>
        <CategoryBar categories={summary?.by_category ?? {}} />
      </div>

      {/* Top actions */}
      {summary?.top_actions?.length > 0 && (
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700 mb-6">
          <h3 className="text-sm font-medium text-gray-400 mb-3">Top Actions</h3>
          <div className="space-y-1">
            {summary.top_actions.map((a: any) => (
              <div key={a.action} className="flex justify-between text-sm">
                <span className="text-gray-300 font-mono">{a.action}</span>
                <span className="text-gray-400">{a.count}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* System events */}
      {summary?.recent_system_events?.length > 0 && (
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700 mb-6">
          <h3 className="text-sm font-medium text-gray-400 mb-3">System Events</h3>
          <div className="space-y-2">
            {summary.recent_system_events.map((e: any, i: number) => (
              <div key={i} className={`text-sm px-3 py-2 rounded ${
                e.severity === 'error' ? 'bg-red-900/30 text-red-300' :
                e.severity === 'warning' ? 'bg-yellow-900/30 text-yellow-300' :
                'bg-gray-700/50 text-gray-300'
              }`}>
                <span className="font-mono text-xs text-gray-500">{e.source}</span>
                <span className="mx-2">|</span>
                {e.message}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Activity feed */}
      <div className="bg-gray-800 rounded-lg border border-gray-700">
        <div className="px-4 py-3 border-b border-gray-700">
          <h3 className="text-white font-medium">Recent Activity</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left">
            <thead className="text-gray-400 border-b border-gray-700">
              <tr>
                <th className="px-4 py-2">Time</th>
                <th className="px-4 py-2">User</th>
                <th className="px-4 py-2">Action</th>
                <th className="px-4 py-2">Category</th>
                <th className="px-4 py-2">Status</th>
                <th className="px-4 py-2">Duration</th>
              </tr>
            </thead>
            <tbody>
              {activities?.map((a: any) => (
                <tr key={a.id} className="border-b border-gray-700/50 hover:bg-gray-700/30">
                  <td className="px-4 py-2 text-gray-400 text-xs">{new Date(a.created_at).toLocaleTimeString()}</td>
                  <td className="px-4 py-2 text-gray-300">{a.user_id}</td>
                  <td className="px-4 py-2 font-mono text-xs text-blue-400">{a.action}</td>
                  <td className="px-4 py-2">
                    <span className="px-2 py-0.5 rounded text-xs bg-gray-700 text-gray-300">{a.category}</span>
                  </td>
                  <td className="px-4 py-2">
                    <span className={`text-xs ${a.status === 'success' ? 'text-green-400' : 'text-red-400'}`}>{a.status}</span>
                  </td>
                  <td className="px-4 py-2 text-gray-400 text-xs">{a.duration_ms ? `${a.duration_ms}ms` : '-'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
