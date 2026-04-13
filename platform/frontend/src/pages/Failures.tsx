import React from 'react';
import { Link } from 'react-router-dom';
import { AlertTriangle, RotateCcw } from 'lucide-react';
import { useWorkflows, useRetryWorkflow } from '../hooks/useWorkflows';
import StatusBadge from '../components/StatusBadge';

export default function Failures() {
  const { data: runs, isLoading, error } = useWorkflows();
  const retry = useRetryWorkflow();

  const failed = (runs ?? []).filter((r) => r.status === 'failed');

  if (isLoading) return <p className="p-6 text-gray-500">Loading...</p>;
  if (error) return <p className="p-6 text-red-600">Error: {(error as Error).message}</p>;

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Failed Workflows</h1>

      {failed.length === 0 ? (
        <div className="bg-white rounded-lg shadow-sm border p-12 text-center text-gray-400">
          <AlertTriangle size={40} className="mx-auto mb-3 opacity-40" />
          No failed workflows
        </div>
      ) : (
        <div className="space-y-3">
          {failed.map((run) => (
            <div key={run.id} className="bg-white rounded-lg shadow-sm border p-4">
              <div className="flex items-start justify-between">
                <div>
                  <div className="flex items-center gap-3 mb-1">
                    <Link
                      to={`/workflows/${run.id}`}
                      className="text-blue-600 hover:underline font-mono text-sm font-bold"
                    >
                      {run.id.slice(0, 12)}
                    </Link>
                    <StatusBadge status={run.status} />
                  </div>
                  <p className="text-sm text-gray-600">
                    {run.workflow_type} &middot; Stage: <span className="font-medium">{run.current_stage}</span>
                  </p>
                  <p className="text-xs text-gray-400 mt-1">
                    Failed at {new Date(run.updated_at).toLocaleString()}
                  </p>
                </div>
                <button
                  onClick={() => retry.mutate(run.id)}
                  disabled={retry.isPending}
                  className="flex items-center gap-1.5 px-3 py-1.5 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
                >
                  <RotateCcw size={14} />
                  Retry
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
