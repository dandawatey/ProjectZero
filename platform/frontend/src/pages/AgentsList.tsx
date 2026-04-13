import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';

const AGENT_TEAMS = [
  { team: 'CXO', agents: ['ceo', 'cto', 'cpo', 'cfo', 'cmo', 'cro', 'ralph-controller'], color: 'border-purple-500' },
  { team: 'Product', agents: ['product-manager', 'product-analyst', 'ux-researcher'], color: 'border-blue-500' },
  { team: 'Engineering', agents: ['architect', 'backend-engineer', 'frontend-engineer', 'data-engineer', 'devops-engineer', 'qa-engineer', 'sre-engineer'], color: 'border-cyan-500' },
  { team: 'Sales', agents: ['sales-strategist', 'customer-success'], color: 'border-green-500' },
  { team: 'Marketing', agents: ['marketing-strategist', 'content-creator'], color: 'border-yellow-500' },
  { team: 'Governance', agents: ['checker', 'reviewer', 'approver', 'security-reviewer', 'ux-reviewer'], color: 'border-orange-500' },
  { team: 'Operations', agents: ['release-manager', 'finops-analyst', 'integration-agent', 'plugin-validator', 'repo-validator', 'readiness-validator', 'pipeline-agent', 'memory-agent'], color: 'border-red-500' },
];

const fetchAgentStatus = () => fetch('/api/v1/dev/agents/live').then(r => r.json());

export default function AgentsList() {
  const { data: liveData } = useQuery({ queryKey: ['agents-live'], queryFn: fetchAgentStatus, refetchInterval: 5000 });
  const activeAgents = new Set((liveData?.active_agents || []).map((a: any) => a.agent_type));

  return (
    <div>
      <h1 className="text-2xl font-bold text-white mb-2">Agent Directory</h1>
      <p className="text-gray-400 text-sm mb-6">34 agents across 7 teams. Click any agent to see their work.</p>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {AGENT_TEAMS.map(({ team, agents, color }) => (
          <div key={team} className={`bg-gray-800 rounded-lg border-l-4 ${color} border border-gray-700`}>
            <div className="px-4 py-3 border-b border-gray-700">
              <h3 className="text-white font-medium">{team} Team</h3>
              <span className="text-gray-500 text-xs">{agents.length} agents</span>
            </div>
            <div className="divide-y divide-gray-700/50">
              {agents.map(agent => (
                <Link
                  key={agent}
                  to={`/agents/${agent}`}
                  className="flex items-center justify-between px-4 py-2.5 hover:bg-gray-700/30 transition-colors"
                >
                  <span className="text-gray-300 text-sm">{agent}</span>
                  {activeAgents.has(agent) ? (
                    <span className="flex items-center gap-1.5">
                      <span className="h-2 w-2 rounded-full bg-green-500 animate-pulse" />
                      <span className="text-green-400 text-xs">Active</span>
                    </span>
                  ) : (
                    <span className="text-gray-600 text-xs">Idle</span>
                  )}
                </Link>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
