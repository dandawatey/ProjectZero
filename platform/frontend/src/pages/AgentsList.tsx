import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Bot, Clock } from 'lucide-react';
import { api } from '../services/api';

interface Agent {
  id: string;
  agent_id: string;
  name: string;
  skills: string[];
  model: string;
  status: 'active' | 'inactive';
  last_used_at: string | null;
  created_at: string;
}

interface Skill {
  skill_id: string;
  name: string;
  description: string;
}

const SKILL_COLORS: Record<string, string> = {
  spec: 'bg-blue-100 text-blue-700',
  arch: 'bg-purple-100 text-purple-700',
  implement: 'bg-green-100 text-green-700',
  review: 'bg-orange-100 text-orange-700',
  deploy: 'bg-red-100 text-red-700',
};

function skillPillClass(skill: string): string {
  const key = Object.keys(SKILL_COLORS).find(k => skill.toLowerCase().includes(k));
  return key ? SKILL_COLORS[key] : 'bg-gray-100 text-gray-700';
}

function relativeTime(ts: string | null): string {
  if (!ts) return 'never';
  const diff = Date.now() - new Date(ts).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return 'just now';
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  return `${Math.floor(hrs / 24)}d ago`;
}

function SkeletonRow() {
  return (
    <tr className="border-b border-gray-700/50 animate-pulse">
      {[1, 2, 3, 4, 5, 6].map(i => (
        <td key={i} className="px-4 py-3">
          <div className="h-4 bg-gray-700 rounded w-24" />
        </td>
      ))}
    </tr>
  );
}

export default function AgentsList() {
  const qc = useQueryClient();

  const { data: agents, isLoading: agentsLoading } = useQuery<Agent[]>({
    queryKey: ['agents'],
    queryFn: () => api.agentRegistry.list(),
    refetchInterval: 30000,
  });

  const { data: skills, isLoading: skillsLoading } = useQuery<Skill[]>({
    queryKey: ['agent-skills'],
    queryFn: () => api.agentRegistry.skills(),
  });

  const toggleStatus = useMutation({
    mutationFn: ({ agent_id, status }: { agent_id: string; status: 'active' | 'inactive' }) =>
      api.agentRegistry.patch(agent_id, { status }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['agents'] }),
  });

  return (
    <div>
      {/* Header */}
      <h1 className="text-2xl font-bold text-white mb-1">Agents</h1>
      <p className="text-gray-400 text-sm mb-6">Factory agent registry — 5 core agents</p>

      {/* Agent Registry Table */}
      <div className="bg-gray-800 rounded-lg border border-gray-700 mb-8">
        <div className="px-4 py-3 border-b border-gray-700">
          <h2 className="text-white font-medium">Agent Registry</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="text-gray-400 border-b border-gray-700 text-xs uppercase tracking-wide">
              <tr>
                <th className="px-4 py-3 text-left">Agent</th>
                <th className="px-4 py-3 text-left">Skills</th>
                <th className="px-4 py-3 text-left">Model</th>
                <th className="px-4 py-3 text-left">Status</th>
                <th className="px-4 py-3 text-left">Last Used</th>
                <th className="px-4 py-3 text-left">Action</th>
              </tr>
            </thead>
            <tbody>
              {agentsLoading && [1, 2, 3, 4, 5].map(i => <SkeletonRow key={i} />)}

              {!agentsLoading && (!agents || agents.length === 0) && (
                <tr>
                  <td colSpan={6} className="px-4 py-8 text-center text-gray-500">
                    No agents registered
                  </td>
                </tr>
              )}

              {agents?.map(agent => (
                <tr key={agent.id} className="border-b border-gray-700/50 hover:bg-gray-700/20 transition-colors">
                  {/* Agent */}
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-3">
                      <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gray-700 flex items-center justify-center">
                        <Bot className="w-4 h-4 text-gray-300" />
                      </div>
                      <div>
                        <div className="text-white font-medium">{agent.name}</div>
                        <div className="text-gray-500 font-mono text-xs">{agent.agent_id}</div>
                      </div>
                    </div>
                  </td>

                  {/* Skills */}
                  <td className="px-4 py-3">
                    <div className="flex flex-wrap gap-1">
                      {agent.skills.map(skill => (
                        <span
                          key={skill}
                          className={`rounded-full px-2 py-0.5 text-xs font-medium ${skillPillClass(skill)}`}
                        >
                          {skill}
                        </span>
                      ))}
                    </div>
                  </td>

                  {/* Model */}
                  <td className="px-4 py-3">
                    <span className="font-mono text-xs bg-gray-700 text-gray-300 px-2 py-1 rounded">
                      {agent.model}
                    </span>
                  </td>

                  {/* Status */}
                  <td className="px-4 py-3">
                    {agent.status === 'active' ? (
                      <span className="inline-flex items-center gap-1.5 bg-green-900/40 text-green-400 text-xs px-2 py-1 rounded-full">
                        <span className="h-1.5 w-1.5 rounded-full bg-green-400" />
                        Active
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1.5 bg-gray-700 text-gray-400 text-xs px-2 py-1 rounded-full">
                        <span className="h-1.5 w-1.5 rounded-full bg-gray-500" />
                        Inactive
                      </span>
                    )}
                  </td>

                  {/* Last Used */}
                  <td className="px-4 py-3">
                    <span className="flex items-center gap-1.5 text-gray-400 text-xs">
                      <Clock className="w-3 h-3" />
                      {relativeTime(agent.last_used_at)}
                    </span>
                  </td>

                  {/* Action */}
                  <td className="px-4 py-3">
                    <button
                      onClick={() =>
                        toggleStatus.mutate({
                          agent_id: agent.agent_id,
                          status: agent.status === 'active' ? 'inactive' : 'active',
                        })
                      }
                      disabled={toggleStatus.isPending}
                      className={`text-xs px-3 py-1.5 rounded border transition-colors disabled:opacity-50 ${
                        agent.status === 'active'
                          ? 'border-red-700 text-red-400 hover:bg-red-900/30'
                          : 'border-green-700 text-green-400 hover:bg-green-900/30'
                      }`}
                    >
                      {agent.status === 'active' ? 'Deactivate' : 'Activate'}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Skill Catalog */}
      <div>
        <h2 className="text-white font-medium mb-4">Skill Catalog</h2>
        {skillsLoading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {[1, 2, 3, 4, 5].map(i => (
              <div key={i} className="bg-gray-800 border border-gray-700 rounded-xl p-4 animate-pulse">
                <div className="h-4 bg-gray-700 rounded w-16 mb-2" />
                <div className="h-4 bg-gray-700 rounded w-32 mb-2" />
                <div className="h-3 bg-gray-700 rounded w-full" />
              </div>
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {skills?.map(skill => (
              <div
                key={skill.skill_id}
                className="bg-white border border-gray-200 rounded-xl p-4"
              >
                <span className={`inline-block rounded-full px-2 py-0.5 text-xs font-medium mb-2 ${skillPillClass(skill.skill_id)}`}>
                  {skill.skill_id}
                </span>
                <h3 className="text-gray-900 font-medium text-sm mb-1">{skill.name}</h3>
                <p className="text-gray-500 text-xs leading-relaxed">{skill.description}</p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
