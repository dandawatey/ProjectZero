import React from 'react';
import { Link } from 'react-router-dom';
import { usePendingApprovals, useResolveApproval } from '../hooks/useWorkflows';
import StatusBadge from '../components/StatusBadge';

export default function Approvals() {
  const { data: approvals, isLoading, error } = usePendingApprovals();
  const resolve = useResolveApproval();

  function handleResolve(id: string, action: 'approved' | 'rejected') {
    if (!confirm(`Are you sure you want to ${action === 'approved' ? 'approve' : 'reject'} this?`)) return;
    resolve.mutate({ id, data: { action } });
  }

  if (isLoading) return <p className="p-6 text-gray-500">Loading approvals...</p>;
  if (error) return <p className="p-6 text-red-600">Error: {(error as Error).message}</p>;

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Pending Approvals</h1>

      {(!approvals || approvals.length === 0) ? (
        <div className="bg-white rounded-lg shadow-sm border p-8 text-center text-gray-400">
          No pending approvals
        </div>
      ) : (
        <div className="space-y-3">
          {approvals.map((a) => (
            <div key={a.id} className="bg-white rounded-lg shadow-sm border p-4 flex items-center justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-1">
                  <StatusBadge status={a.approval_type} />
                  <span className="text-sm font-medium">{a.stage_name}</span>
                </div>
                <p className="text-xs text-gray-500">
                  Workflow{' '}
                  <Link to={`/workflows/${a.workflow_run_id}`} className="text-blue-600 hover:underline font-mono">
                    {a.workflow_run_id.slice(0, 8)}
                  </Link>
                  {' '}&middot; Requested {new Date(a.requested_at).toLocaleString()}
                </p>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => handleResolve(a.id, 'approved')}
                  disabled={resolve.isPending}
                  className="px-3 py-1.5 text-sm bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50"
                >
                  Approve
                </button>
                <button
                  onClick={() => handleResolve(a.id, 'rejected')}
                  disabled={resolve.isPending}
                  className="px-3 py-1.5 text-sm bg-red-600 text-white rounded hover:bg-red-700 disabled:opacity-50"
                >
                  Reject
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
