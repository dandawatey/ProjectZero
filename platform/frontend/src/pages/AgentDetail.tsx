import { useParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { StatusBadge } from '../components/StatusBadge';

const api = {
  agentWork: (agentType: string) => 
    fetch(`/api/v1/agents/work/${agentType}`).then(r => r.json()),
};

export default function AgentDetail() {
  const { agentType } = useParams<{ agentType: string }>();
  const { data, isLoading } = useQuery({
    queryKey: ['agent-work', agentType],
    queryFn: () => api.agentWork(agentType!),
    refetchInterval: 5000,
    enabled: !!agentType,
  });

  if (isLoading) return <div className="text-gray-500">Loading agent data...</div>;

  return (
    <div>
      <h1 className="text-2xl font-bold text-white mb-1">{agentType}</h1>
      <p className="text-gray-400 text-sm mb-6">Agent work history and status</p>

      {/* Current Work */}
      <div className="bg-gray-800 rounded-lg border border-gray-700 mb-6">
        <div className="px-4 py-3 border-b border-gray-700 flex items-center gap-2">
          <span className="h-2 w-2 rounded-full bg-green-500 animate-pulse" />
          <h3 className="text-white font-medium">Currently Working On</h3>
        </div>
        {data?.current?.length > 0 ? (
          <div className="divide-y divide-gray-700/50">
            {data.current.map((item: any, i: number) => (
              <div key={i} className="px-4 py-3">
                <div className="flex items-center justify-between">
                  <div>
                    <span className="text-blue-400 font-mono text-sm">{item.feature_id}</span>
                    <span className="text-gray-500 mx-2">|</span>
                    <span className="text-gray-300">{item.stage}</span>
                  </div>
                  <StatusBadge status="running" />
                </div>
                <p className="text-gray-500 text-xs mt-1">
                  Started {item.started_at ? new Date(item.started_at).toLocaleString() : 'unknown'}
                </p>
              </div>
            ))}
          </div>
        ) : (
          <div className="px-4 py-6 text-center text-gray-500">Idle — no active work</div>
        )}
      </div>

      {/* Pending Work */}
      <div className="bg-gray-800 rounded-lg border border-gray-700 mb-6">
        <div className="px-4 py-3 border-b border-gray-700">
          <h3 className="text-white font-medium">Pending Work Items ({data?.pending?.length ?? 0})</h3>
        </div>
        {data?.pending?.length > 0 ? (
          <table className="w-full text-sm">
            <thead className="text-gray-400 border-b border-gray-700">
              <tr>
                <th className="px-4 py-2 text-left">Feature</th>
                <th className="px-4 py-2 text-left">Stage</th>
                <th className="px-4 py-2 text-left">Priority</th>
                <th className="px-4 py-2 text-left">Status</th>
              </tr>
            </thead>
            <tbody>
              {data.pending.map((item: any, i: number) => (
                <tr key={i} className="border-b border-gray-700/50">
                  <td className="px-4 py-2 font-mono text-xs text-blue-400">{item.feature_id}</td>
                  <td className="px-4 py-2 text-gray-300">{item.stage}</td>
                  <td className="px-4 py-2">
                    <span className={`text-xs px-2 py-0.5 rounded ${
                      item.priority === 'P1' ? 'bg-red-900 text-red-300' :
                      item.priority === 'P2' ? 'bg-yellow-900 text-yellow-300' :
                      'bg-gray-700 text-gray-300'
                    }`}>{item.priority || 'P3'}</span>
                  </td>
                  <td className="px-4 py-2"><StatusBadge status={item.status} /></td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <div className="px-4 py-6 text-center text-gray-500">No pending work</div>
        )}
      </div>

      {/* Completed Work */}
      <div className="bg-gray-800 rounded-lg border border-gray-700">
        <div className="px-4 py-3 border-b border-gray-700">
          <h3 className="text-white font-medium">Completed ({data?.completed?.length ?? 0})</h3>
        </div>
        {data?.completed?.length > 0 ? (
          <table className="w-full text-sm">
            <thead className="text-gray-400 border-b border-gray-700">
              <tr>
                <th className="px-4 py-2 text-left">Feature</th>
                <th className="px-4 py-2 text-left">Action</th>
                <th className="px-4 py-2 text-left">Result</th>
                <th className="px-4 py-2 text-left">Duration</th>
                <th className="px-4 py-2 text-left">When</th>
              </tr>
            </thead>
            <tbody>
              {data.completed.map((item: any, i: number) => (
                <tr key={i} className="border-b border-gray-700/50 hover:bg-gray-700/30">
                  <td className="px-4 py-2 font-mono text-xs text-blue-400">{item.feature_id}</td>
                  <td className="px-4 py-2 text-gray-300">{item.action}</td>
                  <td className="px-4 py-2">
                    <span className={`text-xs ${item.result === 'success' ? 'text-green-400' : 'text-red-400'}`}>
                      {item.result}
                    </span>
                  </td>
                  <td className="px-4 py-2 text-gray-400 text-xs">{item.duration_ms}ms</td>
                  <td className="px-4 py-2 text-gray-500 text-xs">
                    {item.created_at ? new Date(item.created_at).toLocaleString() : '-'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <div className="px-4 py-6 text-center text-gray-500">No completed work yet</div>
        )}
      </div>
    </div>
  );
}
