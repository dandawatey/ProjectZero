/**
 * CXO Dashboard — Portfolio home (PRJ0-22)
 *
 * Cards per project: completion %, done/in-progress/todo counts.
 * Recharts: PieChart per card (completion), BarChart throughput overview.
 * Click card → /cxo/:key drill-down.
 */

import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { RefreshCw } from 'lucide-react';
import { useCxoPortfolio } from '../hooks/useCxoMetrics';
import type { ProjectSummary } from '../types/cxo';

const STATUS_COLORS = ['#22c55e', '#3b82f6', '#e5e7eb']; // done / in_progress / todo

function CompletionPie({ summary }: { summary: ProjectSummary }) {
  const data = [
    { name: 'Done', value: summary.done },
    { name: 'In Progress', value: summary.in_progress },
    { name: 'To Do', value: summary.todo },
  ];
  return (
    <PieChart width={80} height={80}>
      <Pie data={data} dataKey="value" cx={38} cy={38} innerRadius={22} outerRadius={36} strokeWidth={0}>
        {data.map((_, i) => (
          <Cell key={i} fill={STATUS_COLORS[i]} />
        ))}
      </Pie>
      <Tooltip formatter={(v: number) => v} />
    </PieChart>
  );
}

function ProjectCard({ p }: { p: ProjectSummary }) {
  const navigate = useNavigate();
  return (
    <div
      onClick={() => navigate(`/cxo/${p.key}`)}
      className="bg-white border rounded-xl shadow-sm p-5 flex gap-4 items-center cursor-pointer hover:shadow-md hover:border-blue-300 transition-all"
    >
      <CompletionPie summary={p} />
      <div className="flex-1 min-w-0">
        <p className="font-bold text-gray-900 text-sm">{p.key}</p>
        <p className="text-2xl font-extrabold text-blue-600">{p.completion_pct}%</p>
        <div className="flex gap-3 mt-1 text-xs text-gray-500">
          <span className="text-green-600 font-medium">{p.done} done</span>
          <span className="text-blue-500 font-medium">{p.in_progress} active</span>
          <span>{p.todo} todo</span>
        </div>
        <p className="text-xs text-gray-400 mt-1">{p.total} total tickets</p>
      </div>
      <div className="text-gray-300 text-lg">›</div>
    </div>
  );
}

function PortfolioBarChart({ projects }: { projects: ProjectSummary[] }) {
  return (
    <ResponsiveContainer width="100%" height={260}>
      <BarChart data={projects} margin={{ top: 8, right: 16, left: 0, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" vertical={false} />
        <XAxis dataKey="key" tick={{ fontSize: 12 }} />
        <YAxis tick={{ fontSize: 12 }} />
        <Tooltip />
        <Legend wrapperStyle={{ fontSize: 12 }} />
        <Bar dataKey="done" name="Done" stackId="a" fill="#22c55e" radius={[0, 0, 0, 0]} />
        <Bar dataKey="in_progress" name="In Progress" stackId="a" fill="#3b82f6" />
        <Bar dataKey="todo" name="To Do" stackId="a" fill="#e5e7eb" radius={[4, 4, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}

export default function CxoDashboard() {
  const { data, isLoading, error, refetch } = useCxoPortfolio();

  if (isLoading) return <Skeleton />;
  if (error) return <p className="text-red-600 p-6">Failed to load portfolio: {(error as Error).message}</p>;
  if (!data) return null;

  const { projects } = data;
  const totalTickets = projects.reduce((s, p) => s + p.total, 0);
  const totalDone = projects.reduce((s, p) => s + p.done, 0);
  const overallPct = totalTickets ? Math.round((totalDone / totalTickets) * 100) : 0;

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold">CXO Dashboard</h1>
          <p className="text-sm text-gray-500 mt-0.5">
            {projects.length} projects · {totalTickets} tickets · {overallPct}% overall done
          </p>
        </div>
        <button
          onClick={() => refetch()}
          className="flex items-center gap-1.5 text-sm text-gray-500 hover:text-gray-800 border px-3 py-1.5 rounded-lg"
        >
          <RefreshCw size={14} /> Refresh
        </button>
      </div>

      {/* Project cards grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4 mb-8">
        {projects.map((p) => (
          <ProjectCard key={p.key} p={p} />
        ))}
        {projects.length === 0 && (
          <p className="text-gray-400 col-span-3 py-12 text-center">No JIRA projects found.</p>
        )}
      </div>

      {/* Stacked bar overview */}
      {projects.length > 0 && (
        <div className="bg-white border rounded-xl shadow-sm p-5">
          <h2 className="font-semibold mb-4">Portfolio Overview — Ticket Status</h2>
          <PortfolioBarChart projects={projects} />
        </div>
      )}
    </div>
  );
}

function Skeleton() {
  return (
    <div className="animate-pulse space-y-4">
      <div className="h-8 bg-gray-200 rounded w-48" />
      <div className="grid grid-cols-3 gap-4">
        {Array.from({ length: 6 }).map((_, i) => (
          <div key={i} className="h-28 bg-gray-200 rounded-xl" />
        ))}
      </div>
      <div className="h-64 bg-gray-200 rounded-xl" />
    </div>
  );
}
