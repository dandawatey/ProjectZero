import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Zap, Shield, Brain, GitBranch, BarChart3, Bot,
  ArrowRight, CheckCircle, ChevronRight, Layers,
  Clock, Users, TrendingUp, Lock, RefreshCw,
} from 'lucide-react';

// ── Animation hook ────────────────────────────────────────────────────────────
function useIntersect(threshold = 0.15) {
  const [visible, setVisible] = useState(false);
  const ref = React.useRef<HTMLDivElement>(null);
  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const obs = new IntersectionObserver(([e]) => { if (e.isIntersecting) setVisible(true); }, { threshold });
    obs.observe(el);
    return () => obs.disconnect();
  }, [threshold]);
  return { ref, visible };
}

function FadeIn({ children, delay = 0, className = '' }: { children: React.ReactNode; delay?: number; className?: string }) {
  const { ref, visible } = useIntersect();
  return (
    <div
      ref={ref}
      className={`transition-all duration-700 ${visible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-6'} ${className}`}
      style={{ transitionDelay: `${delay}ms` }}
    >
      {children}
    </div>
  );
}

// ── Animated terminal ─────────────────────────────────────────────────────────
const TERMINAL_LINES = [
  { delay: 0,    text: '$ /bootstrap-product "AI Analytics Platform"', color: 'text-green-400' },
  { delay: 800,  text: '✓ PRD generated — 12 epics, 47 user stories', color: 'text-gray-300' },
  { delay: 1600, text: '✓ JIRA project created — PAP-001 through PAP-047', color: 'text-gray-300' },
  { delay: 2400, text: '✓ Confluence space provisioned', color: 'text-gray-300' },
  { delay: 3200, text: '$ /sprint — planning Sprint 1 (capacity: 40pts)', color: 'text-green-400' },
  { delay: 4000, text: '✓ 8 stories assigned — velocity estimate: 38pts', color: 'text-gray-300' },
  { delay: 4800, text: '$ /implement PAP-003 "User authentication"', color: 'text-green-400' },
  { delay: 5600, text: '  → Spec  ████████████ done', color: 'text-blue-400' },
  { delay: 6200, text: '  → Build ████████████ done', color: 'text-blue-400' },
  { delay: 6800, text: '  → Tests ████████████ 94% coverage', color: 'text-blue-400' },
  { delay: 7400, text: '  → Gate  ⏳ awaiting PM approval…', color: 'text-yellow-400' },
  { delay: 8200, text: '✓ Approved by yogesh@company.com', color: 'text-green-400' },
  { delay: 9000, text: '✓ Deployed to staging — PAP-003 complete', color: 'text-green-400' },
];

function AnimatedTerminal() {
  const [shown, setShown] = useState(0);
  useEffect(() => {
    const timers = TERMINAL_LINES.map((l, i) =>
      setTimeout(() => setShown(i + 1), l.delay)
    );
    const reset = setTimeout(() => setShown(0), 12000);
    return () => { timers.forEach(clearTimeout); clearTimeout(reset); };
  }, [shown === 0 ? 0 : -1]); // restart when reset fires

  // Restart loop
  useEffect(() => {
    if (shown === 0) {
      const start = setTimeout(() => setShown(0), 100);
      return () => clearTimeout(start);
    }
  }, [shown]);

  return (
    <div className="rounded-xl bg-gray-950 border border-gray-800 shadow-2xl overflow-hidden font-mono text-sm">
      {/* Window chrome */}
      <div className="flex items-center gap-2 px-4 py-3 bg-gray-900 border-b border-gray-800">
        <div className="w-3 h-3 rounded-full bg-red-500/80" />
        <div className="w-3 h-3 rounded-full bg-yellow-500/80" />
        <div className="w-3 h-3 rounded-full bg-green-500/80" />
        <span className="ml-3 text-xs text-gray-500">ProjectZero Factory — Control Tower</span>
      </div>
      <div className="p-5 space-y-1.5 min-h-[300px]">
        {TERMINAL_LINES.slice(0, shown).map((line, i) => (
          <div key={i} className={`${line.color} leading-relaxed`}>
            {line.text}
            {i === shown - 1 && shown < TERMINAL_LINES.length && (
              <span className="inline-block w-2 h-4 bg-green-400 ml-1 animate-pulse align-middle" />
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

// ── Data ──────────────────────────────────────────────────────────────────────
const FEATURES = [
  {
    icon: Brain,
    color: 'from-purple-500 to-purple-700',
    bg: 'bg-purple-500/10',
    border: 'border-purple-500/20',
    title: 'Persistent Brain',
    desc: 'Cross-product memory. Every decision, pattern, and lesson learned is stored and recalled — so agents get smarter with every build.',
  },
  {
    icon: Zap,
    color: 'from-blue-500 to-blue-700',
    bg: 'bg-blue-500/10',
    border: 'border-blue-500/20',
    title: 'Temporal Workflows',
    desc: 'Durable, resumable workflows that survive restarts. Epics, stories, bugs, and tasks each route to the right workflow — automatically.',
  },
  {
    icon: Shield,
    color: 'from-green-500 to-green-700',
    bg: 'bg-green-500/10',
    border: 'border-green-500/20',
    title: 'Governance Gates',
    desc: 'Risk-based approval gates built in. Low-risk changes ship automatically. High-stakes releases wait for human sign-off — with auto-escalation.',
  },
  {
    icon: GitBranch,
    color: 'from-orange-500 to-orange-700',
    bg: 'bg-orange-500/10',
    border: 'border-orange-500/20',
    title: 'Stage Model',
    desc: 'Spec → Architecture → Realization → Completion. Every ticket follows the stage model. No skipping, no shortcuts, no silent mutations.',
  },
  {
    icon: Bot,
    color: 'from-pink-500 to-pink-700',
    bg: 'bg-pink-500/10',
    border: 'border-pink-500/20',
    title: 'AI Agents',
    desc: 'Specialized agents for spec, architecture, implementation, review, and deployment — each reading Brain before acting, writing back after.',
  },
  {
    icon: BarChart3,
    color: 'from-cyan-500 to-cyan-700',
    bg: 'bg-cyan-500/10',
    border: 'border-cyan-500/20',
    title: 'CXO Reporting',
    desc: 'Auto-generated executive dashboards. Metrics aggregated, narrative written by Claude, published to Confluence — on schedule.',
  },
];

const STEPS = [
  {
    num: '01',
    title: 'Bootstrap your product',
    desc: 'Run /bootstrap-product. Claude generates a PRD, creates your JIRA project, provisions a Confluence space, and seeds the Brain — in under 2 minutes.',
    tag: 'ProductBootstrapWorkflow',
  },
  {
    num: '02',
    title: 'Plan sprints automatically',
    desc: 'Run /sprint. The factory fetches your backlog, estimates velocity, selects stories, and publishes the sprint plan — waiting for PM approval before committing.',
    tag: 'SprintPlanningWorkflow',
  },
  {
    num: '03',
    title: 'Submit tickets — agents build',
    desc: 'Every JIRA ticket triggers a workflow routed by type: Stories get full 5-stage development. Bugs get Diagnose→Fix→Verify. Tasks ship straight through.',
    tag: 'TicketRouterWorkflow',
  },
  {
    num: '04',
    title: 'Approve gates, not minutiae',
    desc: 'You review decisions, not diffs. Governance gates surface at spec review and pre-release. Everything else is automated. Overdue gates auto-escalate.',
    tag: 'ApprovalEscalationWorkflow',
  },
  {
    num: '05',
    title: 'Release with confidence',
    desc: 'Run /release. Automated verification, changelog generation, Confluence publish, your sign-off, then stakeholder notification — fully audited.',
    tag: 'ReleaseWorkflow',
  },
];

const STATS = [
  { value: '11', label: 'Temporal Workflows', icon: Zap },
  { value: '30+', label: 'Specialized Activities', icon: RefreshCw },
  { value: '4', label: 'Interaction Modes', icon: Users },
  { value: '80%', label: 'Min Test Coverage', icon: TrendingUp },
];

const PRINCIPLES = [
  'No ticket, no work — every change is tracked',
  'TDD always — tests before implementation',
  'Truthful completion — done means done',
  'Four-eye principle on all significant changes',
  'No silent mutations — every change visible in git',
  'Stage gates cannot be skipped',
  'ISO 42001 audit trail built in',
  'Memory recorded — every lesson captured',
];

// ── Component ─────────────────────────────────────────────────────────────────
export default function LandingPage() {
  const navigate = useNavigate();
  const [terminalKey, setTerminalKey] = useState(0);

  // Restart terminal animation on loop
  useEffect(() => {
    const t = setInterval(() => setTerminalKey(k => k + 1), 13000);
    return () => clearInterval(t);
  }, []);

  return (
    <div className="min-h-screen bg-gray-950 text-white overflow-x-hidden">

      {/* ── Nav ── */}
      <nav className="fixed top-0 inset-x-0 z-50 border-b border-white/5 bg-gray-950/80 backdrop-blur-md">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
              <Layers size={16} className="text-white" />
            </div>
            <span className="font-bold text-lg tracking-tight">ProjectZero</span>
            <span className="hidden sm:inline text-xs text-gray-500 border border-gray-800 rounded px-2 py-0.5">Factory</span>
          </div>
          <div className="flex items-center gap-4">
            <button
              onClick={() => navigate('/login')}
              className="text-sm text-gray-400 hover:text-white transition-colors"
            >
              Sign in
            </button>
            <button
              onClick={() => navigate('/login')}
              className="text-sm bg-blue-600 hover:bg-blue-500 text-white px-4 py-2 rounded-lg font-medium transition-colors flex items-center gap-1.5"
            >
              Launch Control Tower <ArrowRight size={14} />
            </button>
          </div>
        </div>
      </nav>

      {/* ── Hero ── */}
      <section className="relative pt-32 pb-24 px-6">
        {/* Background glow */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-[800px] h-[400px] bg-blue-600/10 rounded-full blur-3xl" />
          <div className="absolute top-1/3 left-1/3 w-[500px] h-[300px] bg-purple-600/8 rounded-full blur-3xl" />
        </div>

        <div className="relative max-w-7xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-16 items-center">
            {/* Left */}
            <div>
              <div className="inline-flex items-center gap-2 text-xs bg-blue-500/10 border border-blue-500/20 text-blue-400 rounded-full px-3 py-1.5 mb-6">
                <div className="w-1.5 h-1.5 rounded-full bg-blue-400 animate-pulse" />
                Governed AI product development
              </div>

              <h1 className="text-5xl lg:text-6xl font-black leading-tight tracking-tight mb-6">
                Build products.
                <br />
                <span className="bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
                  Ship with discipline.
                </span>
              </h1>

              <p className="text-xl text-gray-400 leading-relaxed mb-10 max-w-xl">
                ProjectZero is an AI-native factory that turns ideas into governed,
                auditable products — with Temporal workflows, approval gates,
                persistent memory, and ISO 42001 compliance built in from day one.
              </p>

              <div className="flex flex-wrap gap-4">
                <button
                  onClick={() => navigate('/login')}
                  className="group flex items-center gap-2 bg-gradient-to-r from-blue-600 to-blue-500 hover:from-blue-500 hover:to-blue-400 text-white px-6 py-3 rounded-xl font-semibold text-sm transition-all shadow-lg shadow-blue-600/20 hover:shadow-blue-500/30"
                >
                  Open Control Tower
                  <ArrowRight size={16} className="group-hover:translate-x-1 transition-transform" />
                </button>
                <a
                  href="#how-it-works"
                  className="flex items-center gap-2 border border-gray-700 hover:border-gray-600 text-gray-300 hover:text-white px-6 py-3 rounded-xl font-semibold text-sm transition-all"
                >
                  See how it works <ChevronRight size={16} />
                </a>
              </div>

              {/* Trust badges */}
              <div className="flex flex-wrap gap-6 mt-10 text-xs text-gray-500">
                {['ISO 42001 audit trail', 'Temporal durable execution', 'TDD enforced', 'Four-eye gates'].map(b => (
                  <span key={b} className="flex items-center gap-1.5">
                    <CheckCircle size={12} className="text-green-500" /> {b}
                  </span>
                ))}
              </div>
            </div>

            {/* Right — Terminal */}
            <div className="lg:pl-8">
              <AnimatedTerminal key={terminalKey} />
            </div>
          </div>
        </div>
      </section>

      {/* ── Stats ── */}
      <section className="border-y border-white/5 bg-white/2 py-12 px-6">
        <div className="max-w-7xl mx-auto grid grid-cols-2 lg:grid-cols-4 gap-8">
          {STATS.map((s, i) => (
            <FadeIn key={s.label} delay={i * 100} className="text-center">
              <div className="text-4xl font-black text-white mb-1">{s.value}</div>
              <div className="text-sm text-gray-500">{s.label}</div>
            </FadeIn>
          ))}
        </div>
      </section>

      {/* ── Features ── */}
      <section className="py-24 px-6">
        <div className="max-w-7xl mx-auto">
          <FadeIn className="text-center mb-16">
            <h2 className="text-4xl font-black mb-4">
              Everything a product needs to{' '}
              <span className="bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
                ship safely
              </span>
            </h2>
            <p className="text-gray-400 text-lg max-w-2xl mx-auto">
              Not just a code generator. A governed execution system — with memory, workflows, gates, and audits.
            </p>
          </FadeIn>

          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-5">
            {FEATURES.map((f, i) => (
              <FadeIn key={f.title} delay={i * 80}>
                <div className={`rounded-2xl border ${f.border} ${f.bg} p-6 h-full hover:border-opacity-60 transition-all group`}>
                  <div className={`w-10 h-10 rounded-xl bg-gradient-to-br ${f.color} flex items-center justify-center mb-4 group-hover:scale-105 transition-transform`}>
                    <f.icon size={20} className="text-white" />
                  </div>
                  <h3 className="font-bold text-white mb-2">{f.title}</h3>
                  <p className="text-sm text-gray-400 leading-relaxed">{f.desc}</p>
                </div>
              </FadeIn>
            ))}
          </div>
        </div>
      </section>

      {/* ── How it works ── */}
      <section id="how-it-works" className="py-24 px-6 bg-white/2 border-y border-white/5">
        <div className="max-w-7xl mx-auto">
          <FadeIn className="text-center mb-16">
            <h2 className="text-4xl font-black mb-4">From idea to release — governed</h2>
            <p className="text-gray-400 text-lg max-w-2xl mx-auto">
              Five commands, five workflows, zero manual orchestration.
            </p>
          </FadeIn>

          <div className="relative">
            {/* Connector line */}
            <div className="hidden lg:block absolute left-[2.35rem] top-10 bottom-10 w-px bg-gradient-to-b from-blue-500/50 via-purple-500/50 to-pink-500/50" />

            <div className="space-y-8">
              {STEPS.map((step, i) => (
                <FadeIn key={step.num} delay={i * 100}>
                  <div className="lg:flex gap-8 items-start group">
                    {/* Number */}
                    <div className="flex-shrink-0 w-[4.7rem] hidden lg:flex items-center justify-center">
                      <div className="w-12 h-12 rounded-full bg-gray-900 border border-gray-700 group-hover:border-blue-500/50 flex items-center justify-center text-sm font-black text-gray-400 group-hover:text-blue-400 transition-colors z-10 relative">
                        {step.num}
                      </div>
                    </div>

                    {/* Card */}
                    <div className="flex-1 bg-gray-900 border border-gray-800 group-hover:border-gray-700 rounded-2xl p-6 transition-colors">
                      <div className="flex items-start justify-between gap-4 mb-2">
                        <h3 className="font-bold text-white text-lg">{step.title}</h3>
                        <span className="flex-shrink-0 text-xs font-mono text-blue-400 bg-blue-500/10 border border-blue-500/20 rounded px-2 py-1">
                          {step.tag}
                        </span>
                      </div>
                      <p className="text-gray-400 leading-relaxed">{step.desc}</p>
                    </div>
                  </div>
                </FadeIn>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* ── Principles ── */}
      <section className="py-24 px-6">
        <div className="max-w-7xl mx-auto grid lg:grid-cols-2 gap-16 items-center">
          <FadeIn>
            <div className="inline-flex items-center gap-2 text-xs bg-green-500/10 border border-green-500/20 text-green-400 rounded-full px-3 py-1.5 mb-6">
              <Lock size={12} /> Non-negotiable governance
            </div>
            <h2 className="text-4xl font-black mb-6">
              Rules that cannot be broken.
              <br />
              <span className="text-gray-500">By anyone. Including AI.</span>
            </h2>
            <p className="text-gray-400 leading-relaxed mb-8">
              ProjectZero's operating contract is embedded in every workflow. Agents don't freelance.
              They follow the stage model, respect governance rules, record their work,
              and never claim completion unless the work is genuinely done.
            </p>
            <button
              onClick={() => navigate('/login')}
              className="group flex items-center gap-2 text-sm text-blue-400 hover:text-blue-300 font-medium transition-colors"
            >
              See the operating contract in Control Tower
              <ArrowRight size={14} className="group-hover:translate-x-1 transition-transform" />
            </button>
          </FadeIn>

          <FadeIn delay={150}>
            <div className="grid sm:grid-cols-2 gap-3">
              {PRINCIPLES.map((p, i) => (
                <div
                  key={i}
                  className="flex items-start gap-3 bg-gray-900 border border-gray-800 rounded-xl p-4"
                >
                  <CheckCircle size={16} className="text-green-500 flex-shrink-0 mt-0.5" />
                  <span className="text-sm text-gray-300">{p}</span>
                </div>
              ))}
            </div>
          </FadeIn>
        </div>
      </section>

      {/* ── Architecture ── */}
      <section className="py-24 px-6 bg-white/2 border-y border-white/5">
        <div className="max-w-7xl mx-auto">
          <FadeIn className="text-center mb-16">
            <h2 className="text-4xl font-black mb-4">Clean architecture. Visible execution.</h2>
            <p className="text-gray-400 text-lg max-w-2xl mx-auto">
              Every layer has one job. Nothing hidden, nothing magic.
            </p>
          </FadeIn>

          <FadeIn delay={100}>
            <div className="max-w-4xl mx-auto">
              {[
                {
                  layer: 'Control Tower', sub: 'React + TypeScript',
                  desc: 'Command interface, live workflow monitor, approval gates, Factory Floor dashboard',
                  color: 'from-blue-500 to-blue-600',
                },
                {
                  layer: 'API', sub: 'FastAPI + Python',
                  desc: 'REST API, JWT auth, workflow orchestration, ticket routing, JIRA/Confluence integration',
                  color: 'from-purple-500 to-purple-600',
                },
                {
                  layer: 'Brain', sub: 'PostgreSQL',
                  desc: 'Persistent memory, decisions, patterns, conversation history, CXO metrics cache',
                  color: 'from-pink-500 to-pink-600',
                },
                {
                  layer: 'Engine', sub: 'Temporal',
                  desc: '11 durable workflows — ticket routing, development, sprint planning, releases, escalation, CXO reporting',
                  color: 'from-orange-500 to-orange-600',
                },
                {
                  layer: 'Agents', sub: 'Claude claude-sonnet-4-6',
                  desc: 'Spec, architecture, implementation, review, deployment — reading Brain before acting, writing back after',
                  color: 'from-green-500 to-green-600',
                },
              ].map((item, i) => (
                <div key={item.layer} className="flex items-stretch gap-0 mb-1 last:mb-0">
                  {/* Arrow connector */}
                  {i > 0 && (
                    <div className="absolute -mt-4 ml-24 text-gray-700 text-lg select-none">↓</div>
                  )}
                  <div className={`w-2 rounded-l-xl bg-gradient-to-b ${item.color} flex-shrink-0`} />
                  <div className="flex-1 bg-gray-900 border border-gray-800 border-l-0 rounded-r-xl px-6 py-4 flex items-center gap-6">
                    <div className="w-32 flex-shrink-0">
                      <div className="font-bold text-white">{item.layer}</div>
                      <div className="text-xs text-gray-500 mt-0.5">{item.sub}</div>
                    </div>
                    <div className="h-8 w-px bg-gray-800 flex-shrink-0" />
                    <p className="text-sm text-gray-400">{item.desc}</p>
                  </div>
                </div>
              ))}
            </div>
          </FadeIn>
        </div>
      </section>

      {/* ── CTA ── */}
      <section className="py-32 px-6 relative overflow-hidden">
        <div className="absolute inset-0 pointer-events-none">
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[300px] bg-blue-600/10 rounded-full blur-3xl" />
        </div>
        <div className="relative max-w-3xl mx-auto text-center">
          <FadeIn>
            <h2 className="text-5xl font-black mb-6">
              Ready to build{' '}
              <span className="bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
                something real?
              </span>
            </h2>
            <p className="text-xl text-gray-400 mb-10">
              Sign in to the Control Tower and run your first{' '}
              <code className="text-blue-400 bg-blue-500/10 px-1.5 py-0.5 rounded text-base">/bootstrap-product</code>
            </p>
            <button
              onClick={() => navigate('/login')}
              className="group inline-flex items-center gap-3 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 text-white px-10 py-4 rounded-2xl font-bold text-lg transition-all shadow-2xl shadow-blue-600/20 hover:shadow-blue-500/30 hover:-translate-y-0.5"
            >
              Open Control Tower
              <ArrowRight size={20} className="group-hover:translate-x-1 transition-transform" />
            </button>
          </FadeIn>
        </div>
      </section>

      {/* ── Footer ── */}
      <footer className="border-t border-white/5 py-8 px-6">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-6 h-6 rounded-md bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
              <Layers size={12} className="text-white" />
            </div>
            <span className="text-sm font-semibold text-gray-400">ProjectZero Factory</span>
          </div>
          <div className="text-xs text-gray-600">
            Governed AI product development
          </div>
        </div>
      </footer>

    </div>
  );
}
