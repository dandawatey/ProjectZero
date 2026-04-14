import React from 'react';
import { Link } from 'react-router-dom';
import {
  Activity, CheckCircle, XCircle, ShieldAlert, Clock,
  Github, BookOpen, ExternalLink, Package, Layers,
} from 'lucide-react';
import { useDashboard } from '../hooks/useWorkflows';
import { useQuery } from '@tanstack/react-query';
import { api } from '../services/api';
import StatusBadge from '../components/StatusBadge';

// ── Types ────────────────────────────────────────────────────────────────────

interface Product {
  id: string;
  name: string;
  repo_path: string;
  jira_project_key: string | null;
  github_url: string | null;
  confluence_url: string | null;
  created_at: string;
}

// ── Project Tiles ────────────────────────────────────────────────────────────

function ProjectTile({ p }: { p: Product }) {
  const initials = p.name
    .split(/[\s_-]/)
    .slice(0, 2)
    .map((w) => w[0]?.toUpperCase() ?? '')
    .join('');

  // Derive JIRA board URL from project key if stored
  const jiraUrl = p.jira_project_key
    ? `https://your-org.atlassian.net/jira/software/projects/${p.jira_project_key}/boards`
    : null;

  return (
    <div className="bg-white rounded-xl border border-gray-200 shadow-sm hover:shadow-md transition-shadow p-5 flex flex-col gap-4">
      {/* Header */}
      <div className="flex items-start gap-3">
        <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white font-bold text-sm flex-shrink-0">
          {initials || <Package size={18} />}
        </div>
        <div className="min-w-0">
          <h3 className="font-semibold text-gray-900 truncate">{p.name}</h3>
          {p.jira_project_key && (
            <span className="text-xs text-gray-400 font-mono">{p.jira_project_key}</span>
          )}
        </div>
      </div>

      {/* Links */}
      <div className="flex flex-wrap gap-2">
        {p.github_url && (
          <a
            href={p.github_url}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1.5 text-xs bg-gray-900 hover:bg-gray-700 text-white rounded-md px-2.5 py-1.5 transition-colors"
          >
            <Github size={12} /> GitHub
          </a>
        )}
        {p.confluence_url && (
          <a
            href={p.confluence_url}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1.5 text-xs bg-blue-600 hover:bg-blue-500 text-white rounded-md px-2.5 py-1.5 transition-colors"
          >
            <BookOpen size={12} /> Confluence
          </a>
        )}
        {jiraUrl && (
          <a
            href={jiraUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1.5 text-xs bg-[#0052CC] hover:bg-[#0747A6] text-white rounded-md px-2.5 py-1.5 transition-colors"
          >
            <ExternalLink size={12} /> Jira
          </a>
        )}
        {!p.github_url && !p.confluence_url && !jiraUrl && (
          <span className="text-xs text-gray-400">No links configured</span>
        )}
      </div>

      {/* Footer */}
      <div className="text-xs text-gray-400 mt-auto pt-1 border-t border-gray-100">
        Created {new Date(p.created_at).toLocaleDateString()}
      </div>
    </div>
  );
}

// ── Main Dashboard ────────────────────────────────────────────────────────────

export default function Dashboard() {
  const { data, isLoading, error } = useDashboard();
  const { data: products, isLoading: productsLoading } = useQuery<Product[]>({
    queryKey: ['products'],
    queryFn: () => api.get<Product[]>('/products'),
    staleTime: 60_000,
  });

  if (isLoading) return <Skeleton />;
  if (error) return <p className="text-red-600 p-6">Failed to load dashboard: {(error as Error).message}</p>;
  if (!data) return null;

  const cards = [
    { label: 'Active', value: data.active, icon: Activity, color: 'text-blue-600 bg-blue-50' },
    { label: 'Completed', value: data.completed, icon: CheckCircle, color: 'text-green-600 bg-green-50' },
    { label: 'Failed', value: data.failed, icon: XCircle, color: 'text-red-600 bg-red-50' },
    { label: 'Blocked', value: data.blocked, icon: ShieldAlert, color: 'text-yellow-600 bg-yellow-50' },
    { label: 'Pending Approvals', value: data.pending_approvals, icon: Clock, color: 'text-purple-600 bg-purple-50' },
  ];

  return (
    <div className="space-y-8">
      <h1 className="text-2xl font-bold">Dashboard</h1>

      {/* ── Stat cards ── */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
        {cards.map((c) => (
          <div key={c.label} className="bg-white rounded-lg shadow-sm border p-4">
            <div className="flex items-center gap-3">
              <div className={`p-2 rounded-lg ${c.color}`}>
                <c.icon size={20} />
              </div>
              <div>
                <p className="text-2xl font-bold">{c.value}</p>
                <p className="text-xs text-gray-500">{c.label}</p>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* ── Project tiles ── */}
      <div>
        <div className="flex items-center gap-2 mb-4">
          <Layers size={18} className="text-gray-500" />
          <h2 className="font-semibold text-gray-800">Projects</h2>
          {products && (
            <span className="text-xs text-gray-400 bg-gray-100 rounded-full px-2 py-0.5">
              {products.length}
            </span>
          )}
        </div>

        {productsLoading ? (
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {Array.from({ length: 3 }).map((_, i) => (
              <div key={i} className="h-40 bg-gray-100 rounded-xl animate-pulse" />
            ))}
          </div>
        ) : products && products.length > 0 ? (
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {products.map((p) => (
              <ProjectTile key={p.id} p={p} />
            ))}
          </div>
        ) : (
          <div className="bg-white rounded-xl border border-dashed border-gray-300 p-10 text-center">
            <Package size={32} className="mx-auto text-gray-300 mb-3" />
            <p className="text-sm text-gray-500 font-medium">No projects yet</p>
            <p className="text-xs text-gray-400 mt-1">
              Run <code className="bg-gray-100 px-1 py-0.5 rounded">/bootstrap-product</code> to create your first product
            </p>
          </div>
        )}
      </div>

      {/* ── Recent workflow runs ── */}
      <div className="bg-white rounded-lg shadow-sm border">
        <div className="px-4 py-3 border-b">
          <h2 className="font-semibold">Recent Workflow Runs</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 text-left text-gray-600">
              <tr>
                <th className="px-4 py-2">ID</th>
                <th className="px-4 py-2">Type</th>
                <th className="px-4 py-2">Feature</th>
                <th className="px-4 py-2">Status</th>
                <th className="px-4 py-2">Stage</th>
                <th className="px-4 py-2">Updated</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {data.recent_runs.map((run) => (
                <tr key={run.id} className="hover:bg-gray-50">
                  <td className="px-4 py-2">
                    <Link to={`/app/workflows/${run.id}`} className="text-blue-600 hover:underline font-mono text-xs">
                      {run.id.slice(0, 8)}
                    </Link>
                  </td>
                  <td className="px-4 py-2">{run.workflow_type}</td>
                  <td className="px-4 py-2 font-mono text-xs">{run.feature_id.slice(0, 8)}</td>
                  <td className="px-4 py-2"><StatusBadge status={run.status} /></td>
                  <td className="px-4 py-2 text-gray-600">{run.current_stage}</td>
                  <td className="px-4 py-2 text-gray-500 text-xs">{new Date(run.updated_at).toLocaleString()}</td>
                </tr>
              ))}
              {data.recent_runs.length === 0 && (
                <tr><td colSpan={6} className="px-4 py-8 text-center text-gray-400">No recent runs</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

function Skeleton() {
  return (
    <div className="animate-pulse space-y-6">
      <div className="h-8 bg-gray-200 rounded w-40" />
      <div className="grid grid-cols-5 gap-4">
        {Array.from({ length: 5 }).map((_, i) => (
          <div key={i} className="h-20 bg-gray-200 rounded-lg" />
        ))}
      </div>
      <div className="grid grid-cols-3 gap-4">
        {Array.from({ length: 3 }).map((_, i) => (
          <div key={i} className="h-40 bg-gray-200 rounded-xl" />
        ))}
      </div>
      <div className="h-64 bg-gray-200 rounded-lg" />
    </div>
  );
}
