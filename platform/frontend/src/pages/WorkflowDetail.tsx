import React from 'react';
import { useParams, Link } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import { useWorkflow, useWorkflowSteps, useAgentContributions, useArtifacts } from '../hooks/useWorkflows';
import StatusBadge from '../components/StatusBadge';
import StagePipeline from '../components/StagePipeline';

export default function WorkflowDetail() {
  const { id } = useParams<{ id: string }>();
  const { data: wf, isLoading: wfLoading } = useWorkflow(id!);
  const { data: steps } = useWorkflowSteps(id!);
  const { data: contributions } = useAgentContributions(id);
  const { data: artifacts } = useArtifacts(id);

  if (wfLoading) return <p className="p-6 text-gray-500">Loading...</p>;
  if (!wf) return <p className="p-6 text-red-600">Workflow not found</p>;

  return (
    <div>
      <Link to="/workflows" className="inline-flex items-center gap-1 text-sm text-gray-500 hover:text-gray-700 mb-4">
        <ArrowLeft size={16} /> Back to workflows
      </Link>

      <div className="bg-white rounded-lg shadow-sm border p-5 mb-6">
        <div className="flex items-start justify-between mb-4">
          <div>
            <h1 className="text-xl font-bold font-mono">{wf.id.slice(0, 12)}...</h1>
            <p className="text-sm text-gray-500 mt-1">{wf.workflow_type}</p>
          </div>
          <StatusBadge status={wf.status} />
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          <div>
            <span className="text-gray-500">Product</span>
            <p className="font-mono text-xs">{wf.product_id}</p>
          </div>
          <div>
            <span className="text-gray-500">Feature</span>
            <p className="font-mono text-xs">{wf.feature_id}</p>
          </div>
          <div>
            <span className="text-gray-500">Current Stage</span>
            <p>{wf.current_stage}</p>
          </div>
          <div>
            <span className="text-gray-500">Temporal Run</span>
            <p className="font-mono text-xs">{wf.temporal_run_id ?? 'N/A'}</p>
          </div>
        </div>
      </div>

      {steps && steps.length > 0 && (
        <div className="bg-white rounded-lg shadow-sm border p-5 mb-6">
          <h2 className="font-semibold mb-2">Pipeline</h2>
          <StagePipeline steps={steps} />
        </div>
      )}

      {steps && steps.length > 0 && (
        <div className="bg-white rounded-lg shadow-sm border mb-6">
          <div className="px-4 py-3 border-b"><h2 className="font-semibold">Steps</h2></div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-gray-50 text-left text-gray-600">
                <tr>
                  <th className="px-4 py-2">Stage</th>
                  <th className="px-4 py-2">Status</th>
                  <th className="px-4 py-2">Agent</th>
                  <th className="px-4 py-2">Started</th>
                  <th className="px-4 py-2">Completed</th>
                  <th className="px-4 py-2">Error</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {steps.map((s) => (
                  <tr key={s.id} className="hover:bg-gray-50">
                    <td className="px-4 py-2">{s.stage_name}</td>
                    <td className="px-4 py-2"><StatusBadge status={s.status} /></td>
                    <td className="px-4 py-2 text-xs">{s.agent_type ?? '-'}</td>
                    <td className="px-4 py-2 text-xs text-gray-500">{s.started_at ? new Date(s.started_at).toLocaleString() : '-'}</td>
                    <td className="px-4 py-2 text-xs text-gray-500">{s.completed_at ? new Date(s.completed_at).toLocaleString() : '-'}</td>
                    <td className="px-4 py-2 text-xs text-red-600 max-w-[200px] truncate">{s.error_message ?? '-'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {contributions && contributions.length > 0 && (
        <div className="bg-white rounded-lg shadow-sm border mb-6">
          <div className="px-4 py-3 border-b"><h2 className="font-semibold">Agent Contributions</h2></div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-gray-50 text-left text-gray-600">
                <tr>
                  <th className="px-4 py-2">Agent</th>
                  <th className="px-4 py-2">Action</th>
                  <th className="px-4 py-2">Result</th>
                  <th className="px-4 py-2">Duration</th>
                  <th className="px-4 py-2">Time</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {contributions.map((c) => (
                  <tr key={c.id} className="hover:bg-gray-50">
                    <td className="px-4 py-2 text-xs">{c.agent_type} / {c.agent_id.slice(0, 8)}</td>
                    <td className="px-4 py-2">{c.action}</td>
                    <td className="px-4 py-2 max-w-[200px] truncate text-gray-600">{c.result}</td>
                    <td className="px-4 py-2 text-xs">{(c.duration_ms / 1000).toFixed(1)}s</td>
                    <td className="px-4 py-2 text-xs text-gray-500">{new Date(c.created_at).toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {artifacts && artifacts.length > 0 && (
        <div className="bg-white rounded-lg shadow-sm border">
          <div className="px-4 py-3 border-b"><h2 className="font-semibold">Artifacts</h2></div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-gray-50 text-left text-gray-600">
                <tr>
                  <th className="px-4 py-2">Name</th>
                  <th className="px-4 py-2">Type</th>
                  <th className="px-4 py-2">Size</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {artifacts.map((a, i) => (
                  <tr key={i} className="hover:bg-gray-50">
                    <td className="px-4 py-2">{String(a.name ?? a.id ?? i)}</td>
                    <td className="px-4 py-2 text-xs">{String(a.type ?? '-')}</td>
                    <td className="px-4 py-2 text-xs text-gray-500">{String(a.size ?? '-')}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
