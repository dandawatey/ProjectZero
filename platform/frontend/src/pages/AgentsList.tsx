import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Bot, Clock, CheckCircle, XCircle, Loader2 } from 'lucide-react';
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

interface AgentExecution {
  id: string;
  agent_id: string;
  skill_id: string;
  ticket_id: string | null;
  workflow_run_id: string | null;
  started_at: string | null;
  completed_at: string | null;
  duration_ms: number | null;
  status: 'running' | 'ok' | 'failed' | 'retried';
  quality_gate_passed: boolean | null;
  brain_written: boolean;
  error_message: string | null;
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

function relTime(iso: string | null): string {
  if (!iso) return '—';
  const diff = (Date.now() - new Date(iso).getTime()) / 1000;
  if (diff < 60) return 'just now';
  if (diff < 3600) return `${Math.round(diff / 60)}m ago`;
  if (diff < 86400) return `${Math.round(diff / 3600)}h ago`;
  return `${Math.round(diff / 86400)}d ago`;
}

function fmtDuration(ms: number | null): string {
  if (ms == null) return '—';
  if (ms < 1000) return `${ms}ms`;
  return `${(ms / 1000).toFixed(1)}s`;
}

function SkeletonRow({ cols }: { cols: number }) {
  return (
    <tr className="border-b border-gray-700/50 animate-pulse">
      {Array.from({ length: cols }).map((_, i) => (
        <td key={i} className="px-4 py-3">
          <div className="h-4 bg-gray-700 rounded w-24" />
        </td>
      ))}
    </tr>
  );
}

function StatusBadge({ status }: { status: AgentExecution['status'] }) {
  switch (status) {
    case 'ok':
      return (
        <span className="inline-flex items-center gap-1 bg-green-900/40 text-green-400 text-xs px-2 py-1 rounded-full font-medium">
          OK
        </span>
      );
    case 'failed':
      return (
        <span className="inline-flex items-center gap-1 bg-red-900/40 text-red-400 text-xs px-2 py-1 rounded-full font-medium">
          Failed
        </span>
      );
    case 'retried':
      return (
        <span className="inline-flex items-center gap-1 bg-yellow-900/40 text-yellow-400 text-xs px-2 py-1 rounded-full font-medium">
          Retried
        </span>
      );
    case 'running':
      return (
        <span className="inline-flex items-center gap-1.5 bg-blue-900/40 text-blue-400 text-xs px-2 py-1 rounded-full font-medium">
          <Loader2 className="w-3 h-3 animate-spin" />
          Running
        </span>
      );
  }
}

function QualityGateCell({ value }: { value: boolean | null }) {
  if (value === null) return <span className="text-gray-500">—</span>;
  return value ? (
    <CheckCircle className="w-4 h-4 text-green-400" />
  ) : (
    <XCircle className="w-4 h-4 text-red-400" />
  );
}

function BrainCell({ value }: { value: boolean }) {
  return value ? (
    <CheckCircle className="w-4 h-4 text-green-400" />
  ) : (
    <span className="text-gray-500">—</span>
  );
}

export default function AgentsList() {
  const [tab, setTab] = useState<'registry' | 'history'>('registry');
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

  const { data: executions, isLoading: executionsLoading } = useQuery<AgentExecution[]>({
    queryKey: ['agent-executions'],
    queryFn: () => api.agentRegistry.executions(),
    refetchInterval: 15000,
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

      {/* Tab Bar */}
      <div className="flex gap-1 mb-6 p-1 bg-gray-800 border border-gray-700 rounded-lg w-fit">
        <button
          onClick={() => setTab('registry')}
          className={`px-4 py-1.5 rounded-md text-sm font-medium transition-colors ${
            tab === 'registry'
              ? 'bg-gray-900 text-white'
              : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          Registry
        </button>
        <button
          onClick={() => setTab('history')}
          className={`px-4 py-1.5 rounded-md text-sm font-medium transition-colors ${
            tab === 'history'
              ? 'bg-gray-900 text-white'
              : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          Execution History
        </button>
      </div>

      {/* Registry Tab */}
      {tab === 'registry' && (
        <>
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
                  {agentsLoading && [1, 2, 3, 4, 5].map(i => <SkeletonRow key={i} cols={6} />)}

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
        </>
      )}

      {/* Execution History Tab */}
      {tab === 'history' && (
        <div className="bg-gray-800 rounded-lg border border-gray-700">
          <div className="px-4 py-3 border-b border-gray-700">
            <h2 className="text-white font-medium">Execution History</h2>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="text-gray-400 border-b border-gray-700 text-xs uppercase tracking-wide">
                <tr>
                  <th className="px-4 py-3 text-left">Agent</th>
                  <th className="px-4 py-3 text-left">Skill</th>
                  <th className="px-4 py-3 text-left">Ticket</th>
                  <th className="px-4 py-3 text-left">Status</th>
                  <th className="px-4 py-3 text-left">Quality Gate</th>
                  <th className="px-4 py-3 text-left">Brain</th>
                  <th className="px-4 py-3 text-left">Duration</th>
                  <th className="px-4 py-3 text-left">Started</th>
                </tr>
              </thead>
              <tbody>
                {executionsLoading && [1, 2, 3, 4, 5].map(i => <SkeletonRow key={i} cols={8} />)}

                {!executionsLoading && (!executions || executions.length === 0) && (
                  <tr>
                    <td colSpan={8} className="px-4 py-8 text-center text-gray-500">
                      No executions yet — run a workflow to see agent activity
                    </td>
                  </tr>
                )}

                {executions?.map(exec => (
                  <tr key={exec.id} className="border-b border-gray-700/50 hover:bg-gray-700/20 transition-colors">
                    {/* Agent */}
                    <td className="px-4 py-3">
                      <span className="font-mono text-xs text-gray-300">{exec.agent_id}</span>
                    </td>

                    {/* Skill */}
                    <td className="px-4 py-3">
                      <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${skillPillClass(exec.skill_id)}`}>
                        {exec.skill_id}
                      </span>
                    </td>

                    {/* Ticket */}
                    <td className="px-4 py-3">
                      {exec.ticket_id ? (
                        <span className="font-mono text-xs text-gray-300">{exec.ticket_id}</span>
                      ) : (
                        <span className="text-gray-500">—</span>
                      )}
                    </td>

                    {/* Status */}
                    <td className="px-4 py-3">
                      <StatusBadge status={exec.status} />
                    </td>

                    {/* Quality Gate */}
                    <td className="px-4 py-3">
                      <QualityGateCell value={exec.quality_gate_passed} />
                    </td>

                    {/* Brain */}
                    <td className="px-4 py-3">
                      <BrainCell value={exec.brain_written} />
                    </td>

                    {/* Duration */}
                    <td className="px-4 py-3">
                      <span className="text-gray-400 text-xs">{fmtDuration(exec.duration_ms)}</span>
                    </td>

                    {/* Started */}
                    <td className="px-4 py-3">
                      <span className="text-gray-400 text-xs">{relTime(exec.started_at)}</span>
                    </td>
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
