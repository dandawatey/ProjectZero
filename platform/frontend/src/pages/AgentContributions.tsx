import React, { useState } from 'react';
import { useAgentContributions } from '../hooks/useWorkflows';

export default function AgentContributions() {
  const { data: contributions, isLoading, error } = useAgentContributions();
  const [agentFilter, setAgentFilter] = useState('all');

  if (isLoading) return <p className="p-6 text-gray-500">Loading agent contributions...</p>;
  if (error) return <p className="p-6 text-red-600">Error: {(error as Error).message}</p>;

  const agentTypes = ['all', ...new Set(contributions?.map((c) => c.agent_type) ?? [])];
  const filtered = (contributions ?? []).filter(
    (c) => agentFilter === 'all' || c.agent_type === agentFilter,
  );

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Agent Contributions</h1>

      <div className="mb-4">
        <select
          value={agentFilter}
          onChange={(e) => setAgentFilter(e.target.value)}
          className="border rounded px-3 py-1.5 text-sm bg-white"
        >
          {agentTypes.map((t) => (
            <option key={t} value={t}>{t === 'all' ? 'All agents' : t}</option>
          ))}
        </select>
      </div>

      <div className="bg-white rounded-lg shadow-sm border overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 text-left text-gray-600">
            <tr>
              <th className="px-4 py-2">Agent Type</th>
              <th className="px-4 py-2">Agent ID</th>
              <th className="px-4 py-2">Workflow</th>
              <th className="px-4 py-2">Action</th>
              <th className="px-4 py-2">Result</th>
              <th className="px-4 py-2">Duration</th>
              <th className="px-4 py-2">Time</th>
            </tr>
          </thead>
          <tbody className="divide-y">
            {filtered.map((c) => (
              <tr key={c.id} className="hover:bg-gray-50">
                <td className="px-4 py-2 font-medium">{c.agent_type}</td>
                <td className="px-4 py-2 font-mono text-xs">{c.agent_id.slice(0, 8)}</td>
                <td className="px-4 py-2 font-mono text-xs">{c.workflow_run_id.slice(0, 8)}</td>
                <td className="px-4 py-2">{c.action}</td>
                <td className="px-4 py-2 max-w-[250px] truncate text-gray-600">{c.result}</td>
                <td className="px-4 py-2 text-xs">{(c.duration_ms / 1000).toFixed(1)}s</td>
                <td className="px-4 py-2 text-xs text-gray-500">{new Date(c.created_at).toLocaleString()}</td>
              </tr>
            ))}
            {filtered.length === 0 && (
              <tr><td colSpan={7} className="px-4 py-8 text-center text-gray-400">No contributions found</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
