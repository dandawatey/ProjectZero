import React from 'react';
import { Routes, Route, NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  GitBranch,
  ShieldCheck,
  Bot,
  Package,
  ScrollText,
  AlertTriangle,
  Zap,
  Activity,
} from 'lucide-react';
import Dashboard from './pages/Dashboard';
import WorkflowRuns from './pages/WorkflowRuns';
import WorkflowDetail from './pages/WorkflowDetail';
import Approvals from './pages/Approvals';
import AgentContributions from './pages/AgentContributions';
import Artifacts from './pages/Artifacts';
import AuditLog from './pages/AuditLog';
import Failures from './pages/Failures';
import TemporalExecution from './pages/TemporalExecution';
import ActivityMonitor from './pages/ActivityMonitor';

const navItems = [
  { to: '/', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/temporal', label: 'Temporal', icon: Zap },
  { to: '/workflows', label: 'Workflows', icon: GitBranch },
  { to: '/approvals', label: 'Approvals', icon: ShieldCheck },
  { to: '/agents', label: 'Agents', icon: Bot },
  { to: '/activities', label: 'Activity Monitor', icon: Activity },
  { to: '/artifacts', label: 'Artifacts', icon: Package },
  { to: '/audit', label: 'Audit Log', icon: ScrollText },
  { to: '/failures', label: 'Failures', icon: AlertTriangle },
];

export default function App() {
  return (
    <div className="flex h-screen">
      {/* Sidebar */}
      <aside className="w-56 bg-gray-900 text-gray-300 flex flex-col flex-shrink-0">
        <div className="px-4 py-4 border-b border-gray-800">
          <h1 className="text-white font-bold text-lg tracking-tight">ProjectZero</h1>
          <p className="text-[11px] text-gray-500 mt-0.5">Control Tower</p>
        </div>
        <nav className="flex-1 py-3 space-y-0.5 overflow-y-auto">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === '/'}
              className={({ isActive }) =>
                `flex items-center gap-3 px-4 py-2 text-sm transition-colors ${
                  isActive
                    ? 'bg-gray-800 text-white font-medium'
                    : 'hover:bg-gray-800/50 hover:text-white'
                }`
              }
            >
              <item.icon size={18} />
              {item.label}
            </NavLink>
          ))}
        </nav>
        <div className="px-4 py-3 border-t border-gray-800 text-[11px] text-gray-600">
          v1.0.0
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-y-auto bg-gray-50 p-6">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/workflows" element={<WorkflowRuns />} />
          <Route path="/workflows/:id" element={<WorkflowDetail />} />
          <Route path="/approvals" element={<Approvals />} />
          <Route path="/agents" element={<AgentContributions />} />
          <Route path="/artifacts" element={<Artifacts />} />
          <Route path="/audit" element={<AuditLog />} />
          <Route path="/failures" element={<Failures />} />
          <Route path="/temporal" element={<TemporalExecution />} />
          <Route path="/activities" element={<ActivityMonitor />} />
        </Routes>
      </main>
    </div>
  );
}
