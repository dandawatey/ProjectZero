/**
 * CXO Project Drill-Down — /cxo/:projectKey (PRJ0-23)
 *
 * Charts:
 *   - Velocity: BarChart (committed vs completed, last N sprints)
 *   - Burndown: LineChart (remaining story points by day)
 *   - Tickets/Assignee: BarChart horizontal (todo + in_progress stacked)
 *   - Cycle Time: ScatterChart (days per ticket)
 *   - Issue Types: PieChart donut
 *   - Throughput: AreaChart (tickets done per day, last 30d)
 */

import React from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  ScatterChart,
  Scatter,
  PieChart,
  Pie,
  Cell,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { ArrowLeft, RefreshCw, Database } from 'lucide-react';
import { useCxoProject, useRefreshCxoProject } from '../hooks/useCxoMetrics';

const COLORS = ['#3b82f6', '#22c55e', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4', '#ec4899'];

function SectionCard({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="bg-white border rounded-xl shadow-sm p-5">
      <h2 className="font-semibold text-gray-800 mb-4">{title}</h2>
      {children}
    </div>
  );
}

export default function CxoProject() {
  const { projectKey = '' } = useParams<{ projectKey: string }>();
  const { data, isLoading, error } = useCxoProject(projectKey);
  const refresh = useRefreshCxoProject();

  if (isLoading) return <Skeleton />;
  if (error) return <p className="text-red-600 p-6">Failed: {(error as Error).message}</p>;
  if (!data) return null;

  const { summary, velocity, burndown, assignees, cycle_time, issue_types, throughput, cached } = data;

  // Assignee chart: combine todo + in_progress for sort, build chart data
  const assigneeData = assignees.map((a) => ({ ...a, total: a.todo + a.in_progress }));

  return (
    <div>
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <Link to="/cxo" className="text-gray-400 hover:text-gray-700">
            <ArrowLeft size={20} />
          </Link>
          <div>
            <h1 className="text-2xl font-bold">{projectKey}</h1>
            <p className="text-sm text-gray-500">
              {summary.total} tickets · {summary.completion_pct}% done
              {cached && (
                <span className="ml-2 inline-flex items-center gap-1 text-xs text-amber-600">
                  <Database size={11} /> cached
                </span>
              )}
            </p>
          </div>
        </div>
        <button
          onClick={() => refresh.mutate(projectKey)}
          disabled={refresh.isPending}
          className="flex items-center gap-1.5 text-sm text-gray-500 hover:text-gray-800 border px-3 py-1.5 rounded-lg disabled:opacity-50"
        >
          <RefreshCw size={14} className={refresh.isPending ? 'animate-spin' : ''} />
          {refresh.isPending ? 'Refreshing…' : 'Refresh from JIRA'}
        </button>
      </div>

      {/* KPI strip */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
        {[
          { label: 'Total', value: summary.total, color: 'text-gray-800' },
          { label: 'Done', value: summary.done, color: 'text-green-600' },
          { label: 'In Progress', value: summary.in_progress, color: 'text-blue-600' },
          { label: 'To Do', value: summary.todo, color: 'text-gray-500' },
        ].map((k) => (
          <div key={k.label} className="bg-white border rounded-xl p-4 shadow-sm text-center">
            <p className={`text-3xl font-extrabold ${k.color}`}>{k.value}</p>
            <p className="text-xs text-gray-500 mt-1">{k.label}</p>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        {/* Velocity */}
        <SectionCard title="Sprint Velocity — Committed vs Completed">
          {velocity.length === 0 ? (
            <Empty msg="No sprint data" />
          ) : (
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={velocity}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="sprint" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip />
                <Legend wrapperStyle={{ fontSize: 12 }} />
                <Bar dataKey="committed" name="Committed" fill="#e5e7eb" radius={[4, 4, 0, 0]} />
                <Bar dataKey="completed" name="Completed" fill="#3b82f6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          )}
        </SectionCard>

        {/* Burndown */}
        <SectionCard title={`Sprint Burndown${burndown.sprint ? ` — ${burndown.sprint}` : ''}`}>
          {burndown.series.length === 0 ? (
            <Empty msg="No active sprint or no resolved issues yet" />
          ) : (
            <ResponsiveContainer width="100%" height={220}>
              <LineChart data={burndown.series}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="date" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip />
                <Line type="monotone" dataKey="remaining" name="Remaining pts" stroke="#ef4444" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          )}
        </SectionCard>

        {/* Tickets per assignee */}
        <SectionCard title="Open Tickets per Assignee">
          {assigneeData.length === 0 ? (
            <Empty msg="No open tickets" />
          ) : (
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={assigneeData} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" horizontal={false} />
                <XAxis type="number" tick={{ fontSize: 11 }} />
                <YAxis dataKey="assignee" type="category" tick={{ fontSize: 11 }} width={120} />
                <Tooltip />
                <Legend wrapperStyle={{ fontSize: 12 }} />
                <Bar dataKey="in_progress" name="In Progress" stackId="a" fill="#3b82f6" />
                <Bar dataKey="todo" name="To Do" stackId="a" fill="#e5e7eb" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          )}
        </SectionCard>

        {/* Issue type breakdown */}
        <SectionCard title="Issue Type Breakdown">
          {issue_types.length === 0 ? (
            <Empty msg="No issues" />
          ) : (
            <ResponsiveContainer width="100%" height={220}>
              <PieChart>
                <Pie
                  data={issue_types}
                  dataKey="count"
                  nameKey="type"
                  cx="50%"
                  cy="50%"
                  innerRadius={55}
                  outerRadius={85}
                  paddingAngle={2}
                >
                  {issue_types.map((_, i) => (
                    <Cell key={i} fill={COLORS[i % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={(v: number) => v} />
                <Legend wrapperStyle={{ fontSize: 12 }} />
              </PieChart>
            </ResponsiveContainer>
          )}
        </SectionCard>

        {/* Cycle time */}
        <SectionCard title="Cycle Time — Days to Complete (last 30)">
          {cycle_time.length === 0 ? (
            <Empty msg="No resolved issues" />
          ) : (
            <ResponsiveContainer width="100%" height={220}>
              <ScatterChart>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="key" tick={{ fontSize: 10 }} angle={-30} textAnchor="end" height={50} />
                <YAxis dataKey="days" name="Days" tick={{ fontSize: 11 }} unit="d" />
                <Tooltip cursor={{ strokeDasharray: '3 3' }} formatter={(v: number) => `${v}d`} />
                <Scatter data={cycle_time} fill="#8b5cf6" />
              </ScatterChart>
            </ResponsiveContainer>
          )}
        </SectionCard>

        {/* Throughput */}
        <SectionCard title="Throughput — Tickets Completed per Day (last 30d)">
          {throughput.length === 0 ? (
            <Empty msg="No resolved issues in last 30 days" />
          ) : (
            <ResponsiveContainer width="100%" height={220}>
              <AreaChart data={throughput}>
                <defs>
                  <linearGradient id="tpGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#22c55e" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#22c55e" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="date" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} allowDecimals={false} />
                <Tooltip />
                <Area type="monotone" dataKey="done" name="Done" stroke="#22c55e" fill="url(#tpGrad)" strokeWidth={2} />
              </AreaChart>
            </ResponsiveContainer>
          )}
        </SectionCard>
      </div>
    </div>
  );
}

function Empty({ msg }: { msg: string }) {
  return <p className="text-gray-400 text-sm text-center py-10">{msg}</p>;
}

function Skeleton() {
  return (
    <div className="animate-pulse space-y-4">
      <div className="h-8 bg-gray-200 rounded w-40" />
      <div className="grid grid-cols-4 gap-3">
        {Array.from({ length: 4 }).map((_, i) => <div key={i} className="h-20 bg-gray-200 rounded-xl" />)}
      </div>
      <div className="grid grid-cols-2 gap-5">
        {Array.from({ length: 6 }).map((_, i) => <div key={i} className="h-60 bg-gray-200 rounded-xl" />)}
      </div>
    </div>
  );
}
