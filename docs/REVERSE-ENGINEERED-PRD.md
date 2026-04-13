# ProjectZeroFactory — Reverse-Engineered PRD

> Generated 2026-04-13 via graphify-ts analysis (975 nodes, 1040 edges, 849 communities, 99 files)

---

## 1. Product Vision

**ProjectZeroFactory** is a governed AI-agent operating system for software product development. It orchestrates 34 AI agents across 7 specialized teams through Temporal workflows, enforcing governance (MCRA 4-eye principle), TDD, and stage-gate quality controls — turning a product vision into shipped, tested, audited software with full traceability.

**One-liner**: The factory that turns a PRD into production code — governed, audited, and workflow-driven.

---

## 2. Problem Statement

| Problem | Impact |
|---------|--------|
| AI agents act independently without governance | Inconsistent quality, security gaps, no audit trail |
| No enforced development lifecycle | Skipped specs, missing tests, undocumented architecture |
| Knowledge lost between sessions/products | Teams repeat mistakes, decisions forgotten |
| No visibility into AI agent work | Black-box execution, no approval gates |
| Manual coordination of multi-agent work | Bottlenecks, race conditions, dropped tasks |

---

## 3. Target Users

| Persona | Use Case |
|---------|----------|
| **Product Owner** | Define vision → get governed spec, architecture, implementation |
| **Engineering Lead** | Monitor agent execution, approve architecture, enforce quality |
| **CTO / Governance** | Audit all decisions, enforce 4-eye review, track compliance |
| **Solo Founder** | Bootstrap entire product development with AI workforce |

---

## 4. Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    React Control Tower                       │
│  Dashboard │ DevMonitor │ Workflows │ Approvals │ Agents    │
│  Artifacts │ AuditLog  │ Failures  │ Activity  │ Temporal  │
└────────────────────────────┬────────────────────────────────┘
                             │ REST API
┌────────────────────────────▼────────────────────────────────┐
│                   FastAPI Backend                            │
│  13 route modules │ Brain service │ Workflow service         │
│  Integration service │ Activity service                     │
└──────┬─────────────────────┬────────────────────────────────┘
       │                     │
┌──────▼──────┐    ┌────────▼────────┐
│  PostgreSQL │    │   Temporal       │
│  12 tables  │    │   7 workflows    │
│  Brain DB   │    │   6 activities   │
│  Audit log  │    │   Signal gates   │
└─────────────┘    └─────────────────┘
                            │
                   ┌────────▼────────┐
                   │  34 AI Agents    │
                   │  7 teams         │
                   │  17 skills       │
                   │  Git worktrees   │
                   └─────────────────┘
```

---

## 5. Stage Model (8 Phases)

Every product progresses through sequential, non-skippable stages:

| # | Stage | Agent | Gate | Output |
|---|-------|-------|------|--------|
| 1 | **Intake** | Product Agent | — | Parsed requirements |
| 2 | **Specification** | Product Agent | MCRA | User stories, acceptance criteria, tickets |
| 3 | **Design** | Design Agent | MCRA | UX specs, wireframes, design system |
| 4 | **Architecture** | Architecture Agent | MCRA | ADRs, API contracts, DB schemas, tech stack |
| 5 | **Implementation** | Coding Agent | — | Code (TDD: test first → implement → refactor) |
| 6 | **Testing** | QA Agent | — | Test suites, coverage ≥80% |
| 7 | **Review** | Review Agent | MCRA | Code review, quality validation |
| 8 | **Approval → Release** | Governance + Release | Human | Tagged release, changelog, learnings |

---

## 6. Governance Frameworks

### BMAD (Business, Market, Architecture, Delivery)
All four dimensions documented before any code.

### SPARC (Specification, Pseudocode, Architecture, Refinement, Completion)
Sequential development flow enforced by stage gates.

### TDD (Test-Driven Development)
Non-negotiable: failing test → implement → refactor → commit. 80% minimum coverage.

### MCRA (Maker-Checker-Reviewer-Approver)
4-eye principle implemented as Temporal child workflow with signal-based approval gates.

### No Ticket No Work
Every commit references a ticket. No speculative coding.

---

## 7. Data Model (12 PostgreSQL Tables)

| Table | Purpose | Key Fields |
|-------|---------|------------|
| `workflow_runs` | Track workflow execution | workflow_type, status, current_stage, temporal_run_id |
| `workflow_steps` | Individual stage execution | stage_name, agent_type, status, duration |
| `workflow_approvals` | MCRA gate records | approval_type, status, resolved_by |
| `workflow_artifacts` | Generated files/docs | artifact_type, content_path, metadata |
| `workflow_audit` | Complete audit trail | action, agent_id, details (JSON), correlation_id |
| `workflow_triggers` | How workflows start | trigger_type (manual/api/webhook/schedule) |
| `agent_contributions` | Agent action log | agent_type, action, result, duration_ms |
| `memories` | Persistent memory (Brain) | scope, category, content, confidence, is_promoted |
| `decisions` | Architecture decisions | context, options, chosen, rationale, status |
| `patterns` | Reusable patterns | problem, solution, anti_pattern, success_rate |
| `conversations` | Workflow conversations | stage, mode, messages, decisions_made |
| `user_activities` | User activity tracking | action, category, page, duration_ms |

---

## 8. API Surface (28+ Endpoints)

Base: `/api/v1/`

| Group | Endpoints | Purpose |
|-------|-----------|---------|
| `/workflows` | CRUD + signal + catalog | Workflow lifecycle management |
| `/steps` | GET/POST | Step status tracking |
| `/approvals` | pending + resolve | MCRA approval gates |
| `/agents` | list + contributions | Agent registry and performance |
| `/artifacts` | GET/POST | Generated artifact storage |
| `/audit` | GET | Complete audit trail |
| `/dashboard` | summary | Overview statistics |
| `/brain/memory` | GET/POST | Persistent memory operations |
| `/brain/decisions` | GET/POST | Architecture decision records |
| `/brain/patterns` | GET/POST | Reusable pattern library |
| `/brain/conversations` | GET/POST | Conversation history |
| `/activities` | track + list | User activity monitoring |
| `/temporal` | status + query | Temporal health and workflow queries |
| `/triggers` | GET/POST | Workflow trigger configuration |
| `/integrations` | sync | GitHub, JIRA, Confluence sync |
| `/dev` | overview + worktrees | Real-time dev monitor |
| `/health` | GET | Health check |

---

## 9. Non-Negotiable Rules (The 10 Commandments)

1. **Truthful completion** — No fake "done". Ever.
2. **TDD** — Tests first. No exceptions.
3. **80% minimum coverage** — Enforced, not aspirational.
4. **No Ticket No Work** — Every change tracked.
5. **MCRA 4-eye principle** — On all significant changes.
6. **No silent mutations** — Every change visible and explained.
7. **Stage gates** — Cannot skip stages.
8. **Memory recording** — Learnings captured after every action.
9. **Honest reporting** — Blocked means blocked.
10. **Factory inheritance** — Products inherit rules, can extend but not weaken.

---

## 10. Integration Points

| System | Purpose | Config |
|--------|---------|--------|
| **GitHub** | Source control, PRs, branch management | Token + org |
| **JIRA** | Ticket management, sprint tracking | Base URL + project key |
| **Confluence** | Documentation publishing | Space key + templates |
| **Temporal** | Workflow orchestration engine | Host + namespace + task queue |
| **PostgreSQL** | State, Brain, audit trail | Connection string |
| **Redis** | Caching, queue support | Connection string |
| **Anthropic API** | AI agent execution (Claude) | API key + model |
| **Sentry** | Error tracking (optional) | DSN |
| **PostHog** | Product analytics (optional) | API key |
| **Datadog** | Infrastructure monitoring (optional) | API key |

---

## 11. Success Metrics

| Metric | Target |
|--------|--------|
| Test coverage on all implemented code | ≥ 80% |
| Audit trail completeness | 100% of actions logged |
| MCRA compliance | 100% of significant changes reviewed |
| Memory capture rate | Every decision + blocker recorded |
| Stage-gate adherence | Zero stage skips |
| Workflow completion rate | Track via Failures page |
| Agent utilization | Track via Agent Contributions |

---

# Feature Catalog

## F01: Factory Initialization (`/factory-init`)

**What**: Validates environment, loads governance rules, checks all integrations (GitHub, JIRA, Confluence, Temporal, Postgres, Redis, Anthropic), reads memory from Brain.

**How to use**:
```
/factory-init
```
Run at start of every session. Validates `.env` config, confirms all services reachable, loads factory settings from `.claude/settings.json`. Reports status of each integration.

**Key files**: [scripts/validate-env.sh](scripts/validate-env.sh), [scripts/validate-integrations.sh](scripts/validate-integrations.sh), [.claude/commands/factory-init.md](.claude/commands/factory-init.md)

---

## F02: Product Bootstrap (`/bootstrap-product`)

**What**: Creates new product repository from factory template. Sets up directory structure, copies `.claude/` configuration, initializes git, validates environment.

**How to use**:
```
/bootstrap-product
```
Provide product name, description, tech stack preferences. Creates isolated product repo with factory governance inherited. Supports greenfield (new repo) and brownfield (existing repo) modes.

**Key files**: [scripts/bootstrap-product.sh](scripts/bootstrap-product.sh), [.claude/templates/product-skeleton/](.claude/templates/product-skeleton/)

---

## F03: Vision-to-PRD (`/vision-to-prd`)

**What**: Converts product vision statement into structured PRD + BMAD document through 7-stage Temporal workflow.

**How to use**:
```
/vision-to-prd
```
Input: raw vision statement or brief. Output: structured PRD (problem, users, features, success metrics) + BMAD (Business, Market, Architecture, Delivery) document. Supports `brainstorm` mode for exploration.

**Workflow stages**: vision_intake → structure_extraction → gap_analysis → prd_generation → bmad_generation → user_review → store_and_handoff

**Key files**: [platform/temporal/workflows/vision_to_prd.py](platform/temporal/workflows/vision_to_prd.py), [.claude/workflows/vision-to-prd.md](.claude/workflows/vision-to-prd.md)

---

## F04: Specification (`/spec`)

**What**: Parses PRD, generates user stories with acceptance criteria, creates JIRA tickets, prioritizes backlog, identifies dependencies and risks.

**How to use**:
```
/spec
```
Requires completed PRD (from F03 or manual). Product Agent breaks PRD into epics → stories → tasks. Each story gets acceptance criteria, priority, story points. Output synced to JIRA if configured.

**Key files**: [.claude/commands/spec.md](.claude/commands/spec.md), [.claude/workflows/sparc-specification.md](.claude/workflows/sparc-specification.md)

---

## F05: Architecture (`/arch`)

**What**: Designs system architecture, selects tech stack, defines API contracts, creates data models, writes ADRs, defines component boundaries.

**How to use**:
```
/arch
```
Requires completed specification. Architecture Agent produces: system diagram, API contracts (OpenAPI), DB schemas (DDL), ADRs, component boundaries, security model, scalability plan. MCRA gate must pass before proceeding.

**Key files**: [.claude/commands/arch.md](.claude/commands/arch.md), [.claude/workflows/sparc-architecture.md](.claude/workflows/sparc-architecture.md), [.claude/templates/api-contract-template.yaml](.claude/templates/api-contract-template.yaml), [.claude/templates/db-schema-template.sql](.claude/templates/db-schema-template.sql)

---

## F06: Implementation (`/implement`)

**What**: 10-stage feature development workflow. Picks next ticket, writes tests first (TDD), implements, runs quality gates, commits with ticket reference.

**How to use**:
```
/implement
```
Follows strict TDD cycle: red → green → refactor. Each implementation produces git worktree isolation via tmux sessions. Agents work in parallel where possible (max 3 concurrent agents). MCRA gates at spec, design, architecture, and review stages.

**10 stages**: intake → specification → design → architecture → implementation → testing → review → approval → release_readiness → completion

**Key files**: [platform/temporal/workflows/feature_development.py](platform/temporal/workflows/feature_development.py), [.claude/workflows/feature-development.md](.claude/workflows/feature-development.md)

---

## F07: Quality Gates (`/check`)

**What**: Runs test suite, checks coverage (≥80%), linting (zero errors), type checking (zero errors). Binary pass/fail.

**How to use**:
```
/check
```
Run repeatedly until all gates pass. Required before `/review`. Reports exact failures with actionable fix guidance. No partial passes — either everything green or blocked.

**Key files**: [.claude/commands/check.md](.claude/commands/check.md), [.claude/guardrails/testing-rules.md](.claude/guardrails/testing-rules.md)

---

## F08: Review (`/review`)

**What**: Creates PR with full description, runs automated review checks, requests human review. Reviewer Agent validates code quality, architecture alignment, coverage.

**How to use**:
```
/review
```
Requires `/check` passing. Auto-generates PR description from ticket + implementation notes. Review Agent checks: code quality, architecture conformance, test coverage, security. Flags issues with specific line references.

**Key files**: [.claude/commands/review.md](.claude/commands/review.md), [.claude/workflows/sparc-completion.md](.claude/workflows/sparc-completion.md)

---

## F09: Approval (`/approve`)

**What**: Final human approval gate. Merge only after explicit approval. Governance Agent validates business requirements met.

**How to use**:
```
/approve
```
Requires completed review. Presents summary of all changes, test results, coverage report. Human must explicitly approve. No auto-merge. Approval recorded in audit trail with resolver identity.

**Key files**: [.claude/commands/approve.md](.claude/commands/approve.md), [.claude/guardrails/stage-gates.md](.claude/guardrails/stage-gates.md)

---

## F10: Release (`/release`)

**What**: Tags release, updates changelog, captures learnings in Brain, notifies stakeholders.

**How to use**:
```
/release
```
Requires approval. Generates changelog from commits + tickets. Tags semantic version. Writes learnings to Brain (memories, decisions, patterns). Triggers notification to stakeholders. 

**Workflow**: changelog → version_bump → final_validation → stakeholder_approval → tag_release → notify

**Key files**: [platform/temporal/workflows/release_governance.py](platform/temporal/workflows/release_governance.py), [.claude/commands/release.md](.claude/commands/release.md)

---

## F11: Brain — Persistent Memory System

**What**: Postgres-backed persistent memory storing memories, decisions, patterns, and conversations across sessions and products.

**How to use**:
- Automatic: agents read Brain before every action, write after every action
- Manual: query via API endpoints
- UI: visible in Control Tower dashboard

**4 subsystems**:
| Subsystem | Endpoint | Purpose |
|-----------|----------|---------|
| **Memories** | `/brain/memory` | Facts, learnings, context (factory/product/session scope) |
| **Decisions** | `/brain/decisions` | Architecture decisions with options, rationale, status |
| **Patterns** | `/brain/patterns` | Reusable solutions with problem/solution/anti-pattern |
| **Conversations** | `/brain/conversations` | Chat history per workflow step per mode |

**Promotion flow**: Product-scoped patterns → factory-scoped knowledge (requires approval)

**Key files**: [platform/backend/app/models/brain.py](platform/backend/app/models/brain.py), [platform/backend/app/api/routes/brain.py](platform/backend/app/api/routes/brain.py)

---

## F12: Control Tower (React Frontend)

**What**: 13-page React dashboard for monitoring, approving, and auditing all factory operations.

**How to use**: Run `npm run dev` in `platform/frontend/`. Access at `localhost:3000`.

**Pages**:

| Page | Purpose | Key Actions |
|------|---------|-------------|
| **Dashboard** | Overview stats — active workflows, pending approvals, agent status | Scan for blockers |
| **Dev Monitor** | Real-time agent execution activity | Watch live progress |
| **Temporal Execution** | Temporal workflow state viewer | Debug workflow issues |
| **Workflow Runs** | List all workflows with filters | Start new, inspect existing |
| **Workflow Detail** | Step-by-step timeline with agent assignments | Track individual feature progress |
| **Approvals** | Pending MCRA gates | Approve or reject with feedback |
| **Agents List** | All 34 agents with status and team | Check agent availability |
| **Agent Detail** | Individual agent performance metrics | Identify bottlenecks |
| **Agent Contributions** | Agent action history with results | Audit agent decisions |
| **Artifacts** | Browse all generated files/docs | Download specs, contracts, code |
| **Activity Monitor** | User interaction timeline | Track who did what |
| **Audit Log** | Complete audit trail | Compliance reporting |
| **Failures** | Failed workflow analysis | Root cause investigation |

**Key files**: [platform/frontend/src/](platform/frontend/src/), [platform/frontend/src/App.tsx](platform/frontend/src/App.tsx)

---

## F13: Temporal Workflow Engine

**What**: 7 Temporal workflow definitions with durable execution, signal-based approval gates, retry policies, and child workflows.

**How to use**: Workers auto-start. Workflows triggered by commands or API. Monitor via Control Tower Temporal page.

**Workflows**:

| Workflow | Stages | MCRA Gates | Purpose |
|----------|--------|------------|---------|
| `FeatureDevelopmentWorkflow` | 10 | 4 | Full feature lifecycle |
| `BugFixWorkflow` | 5 | 1 | Bug triage → fix → deploy |
| `QAValidationWorkflow` | 6 | 0 | Test suite execution |
| `DeploymentReadinessWorkflow` | 5 | 0 | Pre-deploy validation |
| `ReleaseGovernanceWorkflow` | 6 | 1 | Release sign-off chain |
| `VisionToPRDWorkflow` | 7 | 1 | Vision → PRD generation |
| `BusinessDocsWorkflow` | varies | 0 | Business document generation |

**Key features**: Signal-based human approval gates, child workflows for MCRA, automatic retry on failure, state sync to Postgres, correlation IDs for audit trail.

**Key files**: [platform/temporal/workflows/](platform/temporal/workflows/), [platform/temporal/activities/core.py](platform/temporal/activities/core.py)

---

## F14: Agent System (34 Agents, 7 Teams)

**What**: Organized AI agent workforce with defined missions, scopes, boundaries, and handoff protocols.

**How to use**: Agents auto-assigned by workflow stage via `STAGE_AGENT_MAP`. Monitor via Control Tower Agent pages.

| Team | Agents | Responsibility |
|------|--------|----------------|
| **CXO** (7) | CEO, CTO, CPO, CFO, CMO, CRO, Ralph Controller | Executive decisions, orchestration |
| **Product** (3) | PM, Analyst, UX Researcher | Specs, stories, user research |
| **Engineering** (7) | Architect, Backend, Frontend, Data, DevOps, QA, SRE | Build, test, deploy |
| **Sales** (2) | Strategist, Customer Success | Revenue, pipeline |
| **Marketing** (2) | Strategist, Content Creator | Brand, campaigns |
| **Governance** (5) | Checker, Reviewer, Approver, Security, UX Reviewer | Quality gates |
| **Operations** (8) | Release Mgr, FinOps, Integration, Plugin/Repo/Readiness Validators, Pipeline, Memory Agent | Infrastructure, releases |

**Key files**: [.claude/agents/](/.claude/agents/), [.claude/agents/AGENT_REGISTRY.md](.claude/agents/AGENT_REGISTRY.md)

---

## F15: Git Worktree Parallel Execution

**What**: Agents execute in isolated git worktrees with tmux sessions for parallel work without branch conflicts.

**How to use**: Automatic during `/implement`. Max 3 concurrent agents (configurable). Monitor via `/dev/worktrees` endpoint.

**Key files**: [platform/temporal/activities/worktree.py](platform/temporal/activities/worktree.py)

---

## F16: MCRA Governance (Maker-Checker-Reviewer-Approver)

**What**: 4-eye principle implemented as Temporal child workflow. Every significant change requires 4 sequential approvals.

**How to use**: Automatic at configured stage gates. Approval requests appear in Control Tower Approvals page. Resolve via UI or API signal.

**Flow**: Maker (agent produces) → Checker (automated validation) → Reviewer (quality review) → Approver (human sign-off)

**Key files**: [.claude/workflows/maker-checker-reviewer-approver.md](.claude/workflows/maker-checker-reviewer-approver.md), [platform/backend/app/api/routes/approvals.py](platform/backend/app/api/routes/approvals.py)

---

## F17: Interaction Modes (4 Modes)

**What**: Every workflow step supports 4 collaboration modes: chat, brainstorm, plan, implement.

**How to use**: Switch mode via Control Tower UI or Temporal signal at any point during a workflow step.

| Mode | Agent Behavior |
|------|---------------|
| `chat` | Answer questions, clarify, report status |
| `brainstorm` | Explore alternatives, challenge assumptions, no commitment |
| `plan` | Structure approach, define steps, estimate effort |
| `implement` | Execute directly — write code, generate artifacts |

**Key files**: [platform/backend/app/models/brain.py](platform/backend/app/models/brain.py) (Conversation.mode field)

---

## F18: Activity Monitor

**What**: Centralized activity tracking at `/api/v1/activities/`. Logs all user actions, mode switches, approvals, command executions.

**How to use**: Automatic logging. View in Control Tower Activity Monitor page. Filter by user, action, category, product.

**Key files**: [platform/backend/app/api/routes/activities.py](platform/backend/app/api/routes/activities.py), [platform/frontend/src/pages/ActivityMonitor.tsx](platform/frontend/src/pages/ActivityMonitor.tsx)

---

## F19: Audit Trail

**What**: Complete audit log of every action in every workflow. Immutable. Includes agent ID, action, details (JSON), correlation ID, timestamp.

**How to use**: View in Control Tower Audit Log page. Query via `/api/v1/audit` with filters. Use correlation IDs to trace action chains.

**Key files**: [platform/backend/app/api/routes/audit.py](platform/backend/app/api/routes/audit.py), [platform/frontend/src/pages/AuditLog.tsx](platform/frontend/src/pages/AuditLog.tsx)

---

## F20: Business Document Generation (`/business-docs`)

**What**: Generates business documents (TAM/SAM/SOM, competitive analysis, financial projections, GTM strategy, pitch deck, costing) using templates.

**How to use**:
```
/business-docs
```
Select document type. Agent fills template with product-specific data from Brain + PRD. Supports discovery phase and planning phase docs.

**Templates available**: TAM/SAM/SOM, competitive analysis, costing, financial projections, GTM strategy, pitch deck

**Key files**: [.claude/commands/business-docs.md](.claude/commands/business-docs.md), [.claude/templates/](/.claude/templates/)

---

## F21: Guardrails System (9 Rule Sets)

**What**: Codified governance rules enforced by agents and quality gates.

| Guardrail | Enforces |
|-----------|----------|
| `core-guardrails` | Base safety rules (no secrets, no silent mutations) |
| `testing-rules` | TDD, 80% coverage, no skipped tests |
| `security-rules` | OWASP top 10, dependency scanning, secret detection |
| `modularity-rules` | Code structure, component boundaries, DRY |
| `observability-rules` | Logging, metrics, tracing requirements |
| `stage-gates` | Sequential stage enforcement, no skipping |
| `ticket-enforcement` | Every commit → ticket, every PR → ticket |
| `jira-ticket-quality` | Story structure, acceptance criteria, estimation |
| `truthful-completion` | Done = code + tests + coverage + types + lint |

**Key files**: [.claude/guardrails/](.claude/guardrails/)

---

## F22: Skills System (17 Specialized Capabilities)

**What**: Pluggable skill packages that extend agent capabilities.

**Available skills**: code-reviewer, debug-skill, design-sprint, feature-forge, frontend-design, hooked-ux, ios-hig-design, playwright-skill, rag-architect, refactoring-ui, secure-code-guardian, spec-miner, superpowers, the-fool, ui-ux-pro-max, using-git-worktrees, ux-heuristics

**How to use**: Skills auto-loaded by agents based on task context. Can also invoke directly as slash commands.

**Key files**: [.claude/skills/](.claude/skills/)

---

## F23: Template Library (25+ Templates)

**What**: Pre-built templates for all artifact types generated by the factory.

**Categories**:
- **Technical**: API contracts (OpenAPI), DB schemas (DDL), TypeScript types
- **Product**: PRD, module specs, epic/story templates
- **Business**: TAM/SAM/SOM, competitive analysis, costing, financial projections, GTM, pitch deck
- **Confluence**: 12 page templates for documentation publishing
- **Infrastructure**: Product skeleton for bootstrap

**Key files**: [.claude/templates/](.claude/templates/)

---

## F24: Recovery & Resume

**What**: Failure recovery with checkpointing. Interrupted workflows resume from last successful step, not from scratch.

**How to use**:
```
/resume          # Continue interrupted session
/recover-workflow  # Resume failed workflow
/recover-ticket    # Recover stuck ticket
```

**Config**: `recovery.checkpointEnabled: true`, `recovery.maxRetries: 3`, `recovery.autoResume: true`

**Key files**: [.claude/commands/resume.md](.claude/commands/resume.md), [.claude/commands/recover-workflow.md](.claude/commands/recover-workflow.md), [.claude/recovery/](.claude/recovery/)

---

## F25: Factory Self-Management

**What**: Factory auditing, upgrading, and monitoring tools.

**Commands**:
```
/factory-audit    # Audit factory state, config drift, rule compliance
/factory-upgrade  # Upgrade factory version across products
/monitor          # Check workflow progress and agent status
/optimize         # Performance optimization recommendations
```

**Key files**: [.claude/commands/factory-audit.md](.claude/commands/factory-audit.md), [.claude/commands/factory-upgrade.md](.claude/commands/factory-upgrade.md)

---

## F26: Integration Service

**What**: Validates and syncs with external services (GitHub, JIRA, Confluence, Temporal, Postgres, Redis, Anthropic).

**How to use**: Auto-validated on `/factory-init`. Manual sync via `/api/v1/integrations/sync`. Individual validators for each service.

**Key files**: [platform/backend/app/services/integration_service.py](platform/backend/app/services/integration_service.py), [scripts/validate-integrations.sh](scripts/validate-integrations.sh)

---

## F27: Dev Monitor (Real-time)

**What**: Real-time developer activity monitor showing live agent execution, worktree status, and workflow progress.

**How to use**: Access via Control Tower "Dev Monitor" page or `/api/v1/dev/overview` endpoint.

**Key files**: [platform/backend/app/api/routes/dev_monitor.py](platform/backend/app/api/routes/dev_monitor.py), [platform/frontend/src/pages/DevMonitor.tsx](platform/frontend/src/pages/DevMonitor.tsx)

---

## F28: Interactive HTML Guide

**What**: 12-page styled HTML documentation for onboarding and reference.

**Pages**: index, getting-started, architecture, workflows, agents, commands, control-tower, governance, phases, business-docs, recovery, diagrams (14 architecture diagrams)

**How to use**: Open [guide/index.html](guide/index.html) in browser. Fully self-contained, no build step.

**Key files**: [guide/](guide/)

---

## F29: Graphify Knowledge Graph

**What**: Auto-generated knowledge graph of entire codebase (975 nodes, 1040 edges, 849 communities). Identifies god nodes, bridge nodes, semantic anomalies, and community structure.

**How to use**: 
```bash
npx graphify-ts generate . --wiki --svg
```
Read [.claude/graphify-out/GRAPH_REPORT.md](.claude/graphify-out/GRAPH_REPORT.md) for architecture insights. Browse [.claude/graphify-out/wiki/](.claude/graphify-out/wiki/) for generated documentation.

**Key files**: [.claude/graphify-out/](.claude/graphify-out/)

---

## F30: Comprehensive Documentation (22 Docs)

**What**: 22 markdown guides covering every aspect of the factory.

| Doc | Topic |
|-----|-------|
| `00-introduction` | What ProjectZeroFactory is |
| `01-how-projectzerofactory-works` | Deep architecture dive |
| `02-how-to-start-a-new-product` | Step-by-step new product |
| `03-org-operating-model` | Factory vs product boundary |
| `04-governance-model` | Governance rules |
| `05-stage-by-stage-workflow` | 8-phase model |
| `06-agent-model` | Agent teams and interactions |
| `07-plugin-and-skill-model` | Skills and extensibility |
| `08-jira-confluence-github-model` | External tool integration |
| `09-memory-and-learning-model` | Brain and knowledge management |
| `10-recovery-and-resume-model` | Failure handling |
| `11-design-system-and-storybook-model` | UI standards |
| `12-pipeline-and-runtime-model` | Dagster pipelines |
| `13-release-and-operations-model` | Release process |
| `14-command-reference` | All slash commands |
| `15-example-new-product-flow` | Complete walkthrough |

**Key files**: [docs/](docs/)

---

## Quick Reference: Command Flow

```
/factory-init          ← Start here. Every session.
    │
/bootstrap-product     ← New product? Start here.
    │
/vision-to-prd         ← No PRD? Generate one.
    │
/spec                  ← Parse PRD → stories → tickets
    │
/arch                  ← Design system → ADRs → contracts
    │
/implement             ← TDD cycle → code → tests
    │
/check                 ← Quality gates (repeat until green)
    │
/review                ← PR → automated review
    │
/approve               ← Human approval gate
    │
/release               ← Tag → changelog → notify
```

---

## Tech Stack Summary

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, TypeScript, Vite, TailwindCSS, React Router, TanStack Query |
| Backend | Python, FastAPI, SQLAlchemy, Pydantic, uvicorn |
| Database | PostgreSQL (async via asyncpg) |
| Workflow Engine | Temporal (Python SDK) |
| AI | Claude (Anthropic API) |
| Parallel Execution | Git worktrees + tmux |
| Caching | Redis |
| Analysis | graphify-ts |
| External | GitHub, JIRA, Confluence |
| Monitoring | Sentry, PostHog, Datadog (optional) |
