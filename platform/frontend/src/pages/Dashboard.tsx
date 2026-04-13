import React from 'react';
import { Link } from 'react-router-dom';
import { Activity, CheckCircle, XCircle, ShieldAlert, Clock } from 'lucide-react';
import { useDashboard } from '../hooks/useWorkflows';
import StatusBadge from '../components/StatusBadge';

export default function Dashboard() {
  const { data, isLoading, error } = useDashboard();

  if (isLoading) return <Skeleton />;
  if (error) return <p className="text-red-600 p-6">Failed to load dashboard: {(error as Error).message}</p>;
  if (!data) return null;

  const cards = [
    { label: 'Active', value: data.active, icon: Activity, color: 'text-blue-600 bg-blue-50' },
    { label: 'Completed', value: data.completed, icon: CheckCircle, color: 'text-green-600 bg-green-50' },
    { label: 'Failed', value: data.failed, icon: XCircle, color: 'text-red-600 bg-red-50' },
    { label: 'Blocked', value: data.blocked, icon: ShieldAlert, color: 'text-yellow-600 bg-yellow-50' },
    { label: 'Pending Approvals', value: data.pending_approvals, icon: Clock, color: 'text-purple-600 bg-purple-50' },
  ];

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Dashboard</h1>

      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4 mb-8">
        {cards.map((c) => (
          <div key={c.label} className="bg-white rounded-lg shadow-sm border p-4">
            <div className="flex items-center gap-3">
              <div className={`p-2 rounded-lg ${c.color}`}>
                <c.icon size={20} />
              </div>
              <div>
                <p className="text-2xl font-bold">{c.value}</p>
                <p className="text-xs text-gray-500">{c.label}</p>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="bg-white rounded-lg shadow-sm border">
        <div className="px-4 py-3 border-b">
          <h2 className="font-semibold">Recent Workflow Runs</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 text-left text-gray-600">
              <tr>
                <th className="px-4 py-2">ID</th>
                <th className="px-4 py-2">Type</th>
                <th className="px-4 py-2">Feature</th>
                <th className="px-4 py-2">Status</th>
                <th className="px-4 py-2">Stage</th>
                <th className="px-4 py-2">Updated</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {data.recent_runs.map((run) => (
                <tr key={run.id} className="hover:bg-gray-50">
                  <td className="px-4 py-2">
                    <Link to={`/workflows/${run.id}`} className="text-blue-600 hover:underline font-mono text-xs">
                      {run.id.slice(0, 8)}
                    </Link>
                  </td>
                  <td className="px-4 py-2">{run.workflow_type}</td>
                  <td className="px-4 py-2 font-mono text-xs">{run.feature_id.slice(0, 8)}</td>
                  <td className="px-4 py-2"><StatusBadge status={run.status} /></td>
                  <td className="px-4 py-2 text-gray-600">{run.current_stage}</td>
                  <td className="px-4 py-2 text-gray-500 text-xs">{new Date(run.updated_at).toLocaleString()}</td>
                </tr>
              ))}
              {data.recent_runs.length === 0 && (
                <tr><td colSpan={6} className="px-4 py-8 text-center text-gray-400">No recent runs</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

function Skeleton() {
  return (
    <div className="animate-pulse space-y-4">
      <div className="h-8 bg-gray-200 rounded w-40" />
      <div className="grid grid-cols-5 gap-4">
        {Array.from({ length: 5 }).map((_, i) => (
          <div key={i} className="h-20 bg-gray-200 rounded-lg" />
        ))}
      </div>
      <div className="h-64 bg-gray-200 rounded-lg" />
    </div>
  );
}
