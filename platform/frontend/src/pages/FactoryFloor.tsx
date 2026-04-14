import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import {
  Activity, CheckCircle, XCircle, Clock, AlertTriangle,
  Package, Layers, Zap, RefreshCw, ExternalLink,
} from 'lucide-react';
import { api } from '../services/api';

// ── Types ────────────────────────────────────────────────────────────────────

interface Product {
  product_id: string;
  workflows: { total: number; completed: number; running: number; failed: number };
  completion_pct: number;
  last_activity: string | null;
}

interface InFlight {
  workflow_run_id: string;
  ticket_id: string;
  workflow_type: string;
  product_id: string;
  current_stage: string;
  started_at: string | null;
  elapsed_min: number | null;
  temporal_id: string | null;
}

interface Gate {
  approval_id: string;
  workflow_run_id: string;
  ticket_id: string;
  product_id: string;
  stage: string;
  approval_type: string;
  waiting_hours: number;
  overdue: boolean;
  requested_at: string | null;
}

interface Release {
  key: string;
  product_id: string;
  content: string;
  released_at: string | null;
}

interface FloorData {
  generated_at: string;
  health: {
    workflows: { total: number; running: number; completed: number; failed: number; success_rate_pct: number };
    pending_gates: number;
    overdue_gates: number;
    products_active: number;
    total_artifacts: number;
  };
  products: Product[];
  in_flight: InFlight[];
  pending_gates: Gate[];
  recent_releases: Release[];
}

// ── API call ─────────────────────────────────────────────────────────────────

function fetchFloor(): Promise<FloorData> {
  return api.get<FloorData>('/factory/floor');
}

// ── Helpers ──────────────────────────────────────────────────────────────────

function elapsed(iso: string | null): string {
  if (!iso) return '—';
  const d = (Date.now() - new Date(iso).getTime()) / 1000;
  if (d < 60) return `${Math.round(d)}s`;
  if (d < 3600) return `${Math.round(d / 60)}m`;
  return `${Math.round(d / 3600)}h`;
}

function stageColor(stage: string): string {
  if (stage.includes('approval') || stage.includes('awaiting')) return 'text-yellow-600 bg-yellow-50';
  if (stage.includes('complet')) return 'text-green-600 bg-green-50';
  if (stage.includes('fail')) return 'text-red-600 bg-red-50';
  return 'text-blue-600 bg-blue-50';
}

function workflowLabel(wt: string): string {
  const map: Record<string, string> = {
    ticket_router_story: 'Story', ticket_router_bug: 'Bug', ticket_router_task: 'Task',
    ticket_router_epic: 'Epic', feature_development: 'Story', bug_fix: 'Bug', task: 'Task',
  };
  return map[wt] ?? wt;
}

// ── Sub-components ────────────────────────────────────────────────────────────

function StatCard({ icon: Icon, label, value, sub, color }: {
  icon: React.ElementType; label: string; value: number | string;
  sub?: string; color: string;
}) {
  return (
    <div className="bg-white rounded-xl border shadow-sm p-4 flex items-center gap-4">
      <div className={`p-2.5 rounded-lg ${color}`}><Icon size={20} /></div>
      <div>
        <p className="text-2xl font-bold text-gray-900">{value}</p>
        <p className="text-xs text-gray-500">{label}</p>
        {sub && <p className="text-xs text-gray-400 mt-0.5">{sub}</p>}
      </div>
    </div>
  );
}

function ProgressBar({ pct, color = 'bg-blue-500' }: { pct: number; color?: string }) {
  return (
    <div className="w-full bg-gray-100 rounded-full h-1.5 mt-1">
      <div className={`${color} h-1.5 rounded-full transition-all`} style={{ width: `${pct}%` }} />
    </div>
  );
}

function ProductCard({ p }: { p: Product }) {
  const barColor = p.completion_pct >= 80 ? 'bg-green-500' : p.completion_pct >= 40 ? 'bg-blue-500' : 'bg-gray-400';
  return (
    <div className="bg-white rounded-xl border shadow-sm p-4">
      <div className="flex items-start justify-between mb-2">
        <div>
          <p className="font-semibold text-gray-900 text-sm truncate max-w-[140px]">{p.product_id}</p>
          <p className="text-xs text-gray-400 mt-0.5">{elapsed(p.last_activity)} ago</p>
        </div>
        <span className="text-lg font-bold text-gray-700">{p.completion_pct}%</span>
      </div>
      <ProgressBar pct={p.completion_pct} color={barColor} />
      <div className="flex gap-3 mt-3 text-xs text-gray-500">
        <span className="flex items-center gap-1"><Activity size={11} className="text-blue-500" />{p.workflows.running} running</span>
        <span className="flex items-center gap-1"><CheckCircle size={11} className="text-green-500" />{p.workflows.completed} done</span>
        {p.workflows.failed > 0 && (
          <span className="flex items-center gap-1"><XCircle size={11} className="text-red-500" />{p.workflows.failed} failed</span>
        )}
      </div>
    </div>
  );
}

function InFlightRow({ r }: { r: InFlight }) {
  return (
    <tr className="hover:bg-gray-50 border-b last:border-0">
      <td className="px-4 py-3">
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-blue-500 animate-pulse" />
          <Link to={`/workflows/${r.workflow_run_id}`} className="font-mono text-xs text-blue-600 hover:underline">
            {r.ticket_id}
          </Link>
        </div>
      </td>
      <td className="px-4 py-3">
        <span className="text-xs bg-gray-100 text-gray-600 rounded px-2 py-0.5">{workflowLabel(r.workflow_type)}</span>
      </td>
      <td className="px-4 py-3 text-xs text-gray-500">{r.product_id}</td>
      <td className="px-4 py-3">
        <span className={`text-xs rounded px-2 py-0.5 font-medium ${stageColor(r.current_stage)}`}>
          {r.current_stage.replace(/_/g, ' ')}
        </span>
      </td>
      <td className="px-4 py-3 text-xs text-gray-400">{elapsed(r.started_at)} ago</td>
      <td className="px-4 py-3">
        {r.temporal_id && (
          <a href={`http://localhost:8233/namespaces/default/workflows/${r.temporal_id}`}
            target="_blank" rel="noopener noreferrer"
            className="text-gray-400 hover:text-gray-600">
            <ExternalLink size={13} />
          </a>
        )}
      </td>
    </tr>
  );
}

function GateRow({ g }: { g: Gate }) {
  return (
    <tr className={`border-b last:border-0 ${g.overdue ? 'bg-red-50' : 'hover:bg-gray-50'}`}>
      <td className="px-4 py-3">
        <div className="flex items-center gap-2">
          {g.overdue && <AlertTriangle size={13} className="text-red-500 flex-shrink-0" />}
          <Link to={`/workflows/${g.workflow_run_id}`} className="font-mono text-xs text-blue-600 hover:underline">
            {g.ticket_id}
          </Link>
        </div>
      </td>
      <td className="px-4 py-3 text-xs text-gray-500">{g.product_id}</td>
      <td className="px-4 py-3">
        <span className="text-xs bg-yellow-100 text-yellow-700 rounded px-2 py-0.5 font-medium">
          {g.stage.replace(/_/g, ' ')}
        </span>
      </td>
      <td className="px-4 py-3 text-xs text-gray-500 capitalize">{g.approval_type}</td>
      <td className={`px-4 py-3 text-xs font-medium ${g.overdue ? 'text-red-600' : 'text-gray-500'}`}>
        {g.waiting_hours >= 1 ? `${Math.round(g.waiting_hours)}h` : `${Math.round(g.waiting_hours * 60)}m`}
        {g.overdue && ' ⚠️'}
      </td>
      <td className="px-4 py-3">
        <Link to="/approvals"
          className="text-xs bg-indigo-600 text-white rounded px-2 py-1 hover:bg-indigo-700">
          Review
        </Link>
      </td>
    </tr>
  );
}

// ── Main page ─────────────────────────────────────────────────────────────────

export default function FactoryFloor() {
  const { data, isLoading, error, refetch, isFetching } = useQuery<FloorData>({
    queryKey: ['factory-floor'],
    queryFn: fetchFloor,
    refetchInterval: 15_000,
  });

  if (isLoading) return <FloorSkeleton />;
  if (error) return (
    <p className="text-red-500 p-6">Failed to load factory floor: {(error as Error).message}</p>
  );
  if (!data) return null;

  const { health, products, in_flight, pending_gates, recent_releases } = data;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Factory Floor</h1>
          <p className="text-sm text-gray-500 mt-0.5">
            Live view — updated every 15s &nbsp;·&nbsp;
            {new Date(data.generated_at).toLocaleTimeString()}
          </p>
        </div>
        <button onClick={() => refetch()}
          className="flex items-center gap-1.5 text-sm text-gray-500 hover:text-gray-700 border rounded-lg px-3 py-1.5">
          <RefreshCw size={14} className={isFetching ? 'animate-spin' : ''} />
          Refresh
        </button>
      </div>

      {/* Stat cards */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
        <StatCard icon={Activity} label="Running" value={health.workflows.running}
          color="text-blue-600 bg-blue-50" />
        <StatCard icon={CheckCircle} label="Completed" value={health.workflows.completed}
          sub={`${health.workflows.success_rate_pct}% success`} color="text-green-600 bg-green-50" />
        <StatCard icon={XCircle} label="Failed" value={health.workflows.failed}
          color="text-red-600 bg-red-50" />
        <StatCard icon={Clock} label="Pending Gates"
          value={health.pending_gates}
          sub={health.overdue_gates > 0 ? `${health.overdue_gates} overdue` : undefined}
          color={health.overdue_gates > 0 ? 'text-red-600 bg-red-50' : 'text-yellow-600 bg-yellow-50'} />
        <StatCard icon={Package} label="Artifacts" value={health.total_artifacts}
          color="text-purple-600 bg-purple-50" />
      </div>

      {/* Products grid */}
      {products.length > 0 && (
        <section>
          <h2 className="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
            <Layers size={15} /> Products ({products.length})
          </h2>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-3">
            {products.map(p => <ProductCard key={p.product_id} p={p} />)}
          </div>
        </section>
      )}

      {/* In-flight + Pending gates — side by side */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* In-flight */}
        <section className="bg-white rounded-xl border shadow-sm overflow-hidden">
          <div className="px-4 py-3 border-b flex items-center justify-between">
            <h2 className="font-semibold text-gray-800 flex items-center gap-2">
              <Zap size={15} className="text-blue-500" /> In Flight
              <span className="ml-1 text-xs bg-blue-100 text-blue-700 rounded-full px-2">{in_flight.length}</span>
            </h2>
            <Link to="/workflows" className="text-xs text-blue-600 hover:underline">View all</Link>
          </div>
          {in_flight.length === 0 ? (
            <p className="px-4 py-8 text-sm text-center text-gray-400">No active workflows</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-gray-50 text-left text-xs text-gray-500">
                  <tr>
                    <th className="px-4 py-2">Ticket</th>
                    <th className="px-4 py-2">Type</th>
                    <th className="px-4 py-2">Product</th>
                    <th className="px-4 py-2">Stage</th>
                    <th className="px-4 py-2">Age</th>
                    <th className="px-4 py-2"></th>
                  </tr>
                </thead>
                <tbody>
                  {in_flight.map(r => <InFlightRow key={r.workflow_run_id} r={r} />)}
                </tbody>
              </table>
            </div>
          )}
        </section>

        {/* Pending gates */}
        <section className="bg-white rounded-xl border shadow-sm overflow-hidden">
          <div className="px-4 py-3 border-b flex items-center justify-between">
            <h2 className="font-semibold text-gray-800 flex items-center gap-2">
              <Clock size={15} className="text-yellow-500" /> Pending Gates
              <span className="ml-1 text-xs bg-yellow-100 text-yellow-700 rounded-full px-2">{pending_gates.length}</span>
              {health.overdue_gates > 0 && (
                <span className="text-xs bg-red-100 text-red-700 rounded-full px-2">
                  {health.overdue_gates} overdue
                </span>
              )}
            </h2>
            <Link to="/approvals" className="text-xs text-blue-600 hover:underline">Approve</Link>
          </div>
          {pending_gates.length === 0 ? (
            <p className="px-4 py-8 text-sm text-center text-gray-400">No pending approvals</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-gray-50 text-left text-xs text-gray-500">
                  <tr>
                    <th className="px-4 py-2">Ticket</th>
                    <th className="px-4 py-2">Product</th>
                    <th className="px-4 py-2">Stage</th>
                    <th className="px-4 py-2">Type</th>
                    <th className="px-4 py-2">Waiting</th>
                    <th className="px-4 py-2"></th>
                  </tr>
                </thead>
                <tbody>
                  {pending_gates.map(g => <GateRow key={g.approval_id} g={g} />)}
                </tbody>
              </table>
            </div>
          )}
        </section>
      </div>

      {/* Recent releases */}
      {recent_releases.length > 0 && (
        <section className="bg-white rounded-xl border shadow-sm overflow-hidden">
          <div className="px-4 py-3 border-b">
            <h2 className="font-semibold text-gray-800 flex items-center gap-2">
              <CheckCircle size={15} className="text-green-500" /> Recent Releases
            </h2>
          </div>
          <div className="divide-y">
            {recent_releases.map(r => (
              <div key={r.key} className="px-4 py-3 flex items-start justify-between gap-4">
                <div>
                  <p className="text-sm font-medium text-gray-800">{r.product_id}</p>
                  <p className="text-xs text-gray-500 mt-0.5 line-clamp-1">{r.content}</p>
                </div>
                <p className="text-xs text-gray-400 whitespace-nowrap flex-shrink-0">
                  {r.released_at ? elapsed(r.released_at) + ' ago' : '—'}
                </p>
              </div>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}

function FloorSkeleton() {
  return (
    <div className="space-y-6 animate-pulse">
      <div className="h-8 bg-gray-200 rounded w-48" />
      <div className="grid grid-cols-5 gap-4">
        {Array.from({ length: 5 }).map((_, i) => (
          <div key={i} className="h-20 bg-gray-200 rounded-xl" />
        ))}
      </div>
      <div className="grid grid-cols-4 gap-3">
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="h-28 bg-gray-200 rounded-xl" />
        ))}
      </div>
      <div className="grid grid-cols-2 gap-6">
        <div className="h-64 bg-gray-200 rounded-xl" />
        <div className="h-64 bg-gray-200 rounded-xl" />
      </div>
    </div>
  );
}
