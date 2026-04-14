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
  Monitor,
  ExternalLink,
  BookOpen,
  Factory,
} from 'lucide-react';

import Dashboard from './pages/Dashboard';
import WorkflowRuns from './pages/WorkflowRuns';
import WorkflowDetail from './pages/WorkflowDetail';
import Approvals from './pages/Approvals';
import AgentsList from './pages/AgentsList';
import AgentDetail from './pages/AgentDetail';
import Artifacts from './pages/Artifacts';
import AuditLog from './pages/AuditLog';
import Failures from './pages/Failures';
import TemporalExecution from './pages/TemporalExecution';
import ActivityMonitor from './pages/ActivityMonitor';
import DevMonitor from './pages/DevMonitor';
import UserGuide from './pages/UserGuide';
import FactoryFloor from './pages/FactoryFloor';
import CreateProduct from './pages/CreateProduct';
import LandingPage from './pages/LandingPage';
import LoginPage from './pages/LoginPage';
import ProtectedRoute from './components/ProtectedRoute';
import ProfileMenu from './components/ProfileMenu';

const navItems = [
  { to: '/app', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/app/floor', label: 'Factory Floor', icon: Factory },
  { to: '/app/dev', label: 'Dev Monitor', icon: Monitor },
  { to: '/app/temporal', label: 'Temporal', icon: Zap },
  { to: '/app/workflows', label: 'Workflows', icon: GitBranch },
  { to: '/app/approvals', label: 'Approvals', icon: ShieldCheck },
  { to: '/app/agents', label: 'Agents', icon: Bot },
  { to: '/app/activities', label: 'Activity', icon: Activity },
  { to: '/app/artifacts', label: 'Artifacts', icon: Package },
  { to: '/app/audit', label: 'Audit Log', icon: ScrollText },
  { to: '/app/failures', label: 'Failures', icon: AlertTriangle },
  { to: '/app/guide', label: 'User Guide', icon: BookOpen },
];

// External links rendered separately in sidebar
const CONFLUENCE_CXO_URL = import.meta.env.VITE_CONFLUENCE_CXO_URL ?? '';

function AppShell() {
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
              end={item.to === '/app'}
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
          {CONFLUENCE_CXO_URL && (
            <a
              href={CONFLUENCE_CXO_URL}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-3 px-4 py-2 text-sm text-gray-400 hover:bg-gray-800/50 hover:text-white transition-colors"
            >
              <ExternalLink size={18} />
              CXO Dashboard ↗
            </a>
          )}
        </nav>
        <ProfileMenu />
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-y-auto bg-gray-50 p-6">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/floor" element={<FactoryFloor />} />
          <Route path="/new-product" element={<CreateProduct />} />
          <Route path="/workflows" element={<WorkflowRuns />} />
          <Route path="/workflows/:id" element={<WorkflowDetail />} />
          <Route path="/approvals" element={<Approvals />} />
          <Route path="/agents" element={<AgentsList />} />
          <Route path="/agents/:agentType" element={<AgentDetail />} />
          <Route path="/artifacts" element={<Artifacts />} />
          <Route path="/audit" element={<AuditLog />} />
          <Route path="/failures" element={<Failures />} />
          <Route path="/temporal" element={<TemporalExecution />} />
          <Route path="/activities" element={<ActivityMonitor />} />
          <Route path="/dev" element={<DevMonitor />} />
          <Route path="/guide" element={<UserGuide />} />
        </Routes>
      </main>
    </div>
  );
}

export default function App() {
  return (
    <Routes>
      {/* Public */}
      <Route path="/" element={<LandingPage />} />
      <Route path="/login" element={<LoginPage />} />
      {/* Protected — all app routes require auth */}
      <Route element={<ProtectedRoute />}>
        <Route path="/app/*" element={<AppShell />} />
      </Route>
    </Routes>
  );
}
