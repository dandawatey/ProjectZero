import { useQuery } from '@tanstack/react-query';
import { StatusBadge } from '../components/StatusBadge';

const api = {
  running: () => fetch('/api/v1/temporal/running').then(r => r.json()),
  completed: () => fetch('/api/v1/temporal/completed').then(r => r.json()),
  failed: () => fetch('/api/v1/temporal/failed').then(r => r.json()),
  workers: () => fetch('/api/v1/temporal/workers').then(r => r.json()),
  workflow: (id: string) => fetch(`/api/v1/temporal/workflow/${id}`).then(r => r.json()),
};

function WorkerStatus() {
  const { data } = useQuery({ queryKey: ['temporal-workers'], queryFn: api.workers, refetchInterval: 10000 });
  if (!data) return null;
  return (
    <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
      <h3 className="text-sm font-medium text-gray-400 mb-2">Temporal Connection</h3>
      <div className="flex items-center gap-3">
        <span className={`h-3 w-3 rounded-full ${data.status === 'connected' ? 'bg-green-500' : 'bg-red-500'}`} />
        <span className="text-white">{data.status === 'connected' ? 'Connected' : 'Disconnected'}</span>
        <span className="text-gray-400 text-sm">| {data.host} | Queue: {data.task_queue}</span>
      </div>
    </div>
  );
}

function WorkflowTable({ title, queryKey, queryFn, statusColor }: {
  title: string; queryKey: string; queryFn: () => Promise<any>; statusColor: string;
}) {
  const { data, isLoading } = useQuery({ queryKey: [queryKey], queryFn, refetchInterval: 5000 });
  return (
    <div className="bg-gray-800 rounded-lg border border-gray-700">
      <div className="px-4 py-3 border-b border-gray-700 flex items-center justify-between">
        <h3 className="text-white font-medium">{title}</h3>
        <span className={`px-2 py-0.5 rounded text-xs font-medium ${statusColor}`}>
          {data?.count ?? 0}
        </span>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-sm text-left">
          <thead className="text-gray-400 border-b border-gray-700">
            <tr>
              <th className="px-4 py-2">Workflow ID</th>
              <th className="px-4 py-2">Type</th>
              <th className="px-4 py-2">Status</th>
              <th className="px-4 py-2">Started</th>
              <th className="px-4 py-2">Actions</th>
            </tr>
          </thead>
          <tbody>
            {isLoading && <tr><td colSpan={5} className="px-4 py-8 text-center text-gray-500">Loading...</td></tr>}
            {data?.workflows?.map((wf: any) => (
              <tr key={wf.workflow_id} className="border-b border-gray-700/50 hover:bg-gray-700/30">
                <td className="px-4 py-2 font-mono text-xs text-blue-400">{wf.workflow_id}</td>
                <td className="px-4 py-2 text-gray-300">{wf.type}</td>
                <td className="px-4 py-2"><StatusBadge status={wf.status?.toLowerCase()} /></td>
                <td className="px-4 py-2 text-gray-400 text-xs">
                  {wf.start_time ? new Date(wf.start_time).toLocaleString() : '-'}
                </td>
                <td className="px-4 py-2">
                  <a href={`/temporal/${wf.workflow_id}`} className="text-blue-400 hover:underline text-xs">Details</a>
                </td>
              </tr>
            ))}
            {data?.workflows?.length === 0 && (
              <tr><td colSpan={5} className="px-4 py-6 text-center text-gray-500">None</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default function TemporalExecution() {
  return (
    <div>
      <h1 className="text-2xl font-bold text-white mb-6">Temporal Execution</h1>
      <div className="space-y-6">
        <WorkerStatus />
        <WorkflowTable title="Running Workflows" queryKey="temporal-running" queryFn={api.running} statusColor="bg-blue-900 text-blue-300" />
        <WorkflowTable title="Recently Completed" queryKey="temporal-completed" queryFn={api.completed} statusColor="bg-green-900 text-green-300" />
        <WorkflowTable title="Failed Workflows" queryKey="temporal-failed" queryFn={api.failed} statusColor="bg-red-900 text-red-300" />
      </div>
    </div>
  );
}
