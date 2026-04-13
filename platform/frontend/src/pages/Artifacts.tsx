import React, { useState } from 'react';
import { useArtifacts } from '../hooks/useWorkflows';
import { Package } from 'lucide-react';

export default function Artifacts() {
  const [workflowId, setWorkflowId] = useState('');
  const { data: artifacts, isLoading, error } = useArtifacts(workflowId || undefined);

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Artifacts</h1>

      <div className="mb-4">
        <input
          type="text"
          placeholder="Filter by workflow ID..."
          value={workflowId}
          onChange={(e) => setWorkflowId(e.target.value)}
          className="border rounded px-3 py-1.5 text-sm w-72"
        />
      </div>

      {isLoading && <p className="text-gray-500">Loading artifacts...</p>}
      {error && <p className="text-red-600">Error: {(error as Error).message}</p>}

      {artifacts && artifacts.length === 0 && (
        <div className="bg-white rounded-lg shadow-sm border p-12 text-center text-gray-400">
          <Package size={40} className="mx-auto mb-3 opacity-40" />
          No artifacts found
        </div>
      )}

      {artifacts && artifacts.length > 0 && (
        <div className="bg-white rounded-lg shadow-sm border overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 text-left text-gray-600">
              <tr>
                <th className="px-4 py-2">Name</th>
                <th className="px-4 py-2">Type</th>
                <th className="px-4 py-2">Workflow</th>
                <th className="px-4 py-2">Size</th>
                <th className="px-4 py-2">Created</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {artifacts.map((a, i) => (
                <tr key={i} className="hover:bg-gray-50">
                  <td className="px-4 py-2 font-medium">{String(a.name ?? a.id ?? '-')}</td>
                  <td className="px-4 py-2 text-xs">{String(a.type ?? '-')}</td>
                  <td className="px-4 py-2 font-mono text-xs">{String(a.workflow_id ?? a.workflow_run_id ?? '-')}</td>
                  <td className="px-4 py-2 text-xs text-gray-500">{String(a.size ?? '-')}</td>
                  <td className="px-4 py-2 text-xs text-gray-500">
                    {a.created_at ? new Date(String(a.created_at)).toLocaleString() : '-'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
