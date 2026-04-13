import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useWorkflows } from '../hooks/useWorkflows';
import StatusBadge from '../components/StatusBadge';

const STATUS_OPTIONS = ['all', 'pending', 'running', 'completed', 'failed', 'blocked'] as const;

export default function WorkflowRuns() {
  const { data: runs, isLoading, error } = useWorkflows();
  const [statusFilter, setStatusFilter] = useState('all');
  const [typeFilter, setTypeFilter] = useState('all');

  if (isLoading) return <p className="p-6 text-gray-500">Loading workflows...</p>;
  if (error) return <p className="p-6 text-red-600">Error: {(error as Error).message}</p>;

  const types = ['all', ...new Set(runs?.map((r) => r.workflow_type) ?? [])];
  const filtered = (runs ?? []).filter(
    (r) =>
      (statusFilter === 'all' || r.status === statusFilter) &&
      (typeFilter === 'all' || r.workflow_type === typeFilter),
  );

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Workflow Runs</h1>

      <div className="flex gap-3 mb-4">
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="border rounded px-3 py-1.5 text-sm bg-white"
        >
          {STATUS_OPTIONS.map((s) => (
            <option key={s} value={s}>{s === 'all' ? 'All statuses' : s}</option>
          ))}
        </select>
        <select
          value={typeFilter}
          onChange={(e) => setTypeFilter(e.target.value)}
          className="border rounded px-3 py-1.5 text-sm bg-white"
        >
          {types.map((t) => (
            <option key={t} value={t}>{t === 'all' ? 'All types' : t}</option>
          ))}
        </select>
      </div>

      <div className="bg-white rounded-lg shadow-sm border overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 text-left text-gray-600">
            <tr>
              <th className="px-4 py-2">ID</th>
              <th className="px-4 py-2">Type</th>
              <th className="px-4 py-2">Product</th>
              <th className="px-4 py-2">Feature</th>
              <th className="px-4 py-2">Status</th>
              <th className="px-4 py-2">Stage</th>
              <th className="px-4 py-2">Created</th>
            </tr>
          </thead>
          <tbody className="divide-y">
            {filtered.map((run) => (
              <tr key={run.id} className="hover:bg-gray-50">
                <td className="px-4 py-2">
                  <Link to={`/workflows/${run.id}`} className="text-blue-600 hover:underline font-mono text-xs">
                    {run.id.slice(0, 8)}
                  </Link>
                </td>
                <td className="px-4 py-2">{run.workflow_type}</td>
                <td className="px-4 py-2 font-mono text-xs">{run.product_id.slice(0, 8)}</td>
                <td className="px-4 py-2 font-mono text-xs">{run.feature_id.slice(0, 8)}</td>
                <td className="px-4 py-2"><StatusBadge status={run.status} /></td>
                <td className="px-4 py-2 text-gray-600">{run.current_stage}</td>
                <td className="px-4 py-2 text-gray-500 text-xs">{new Date(run.created_at).toLocaleString()}</td>
              </tr>
            ))}
            {filtered.length === 0 && (
              <tr><td colSpan={7} className="px-4 py-8 text-center text-gray-400">No workflows found</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
