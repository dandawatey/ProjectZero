# Agent Model

35 agents. 8 teams. Every agent executes inside Temporal workflow steps. No exceptions.

## Architecture

```
React UI → FastAPI → Postgres → Temporal → Agents
```

Each workflow step = one assigned agent. Execution tracked. Contribution recorded. Every feature is a Temporal workflow.

## Agent Types

| Type | Description |
|---|---|
| **System** | Factory infrastructure agents. Orchestration, validation, integration. |
| **AI** | Claude-powered agents. Implementation, review, analysis. |
| **Human** | Human-in-the-loop checkpoints. Approval, override, escalation. |
| **Integration** | External system agents. JIRA, Confluence, GitHub, CI/CD. |

## Teams and Agents

### CXO Team (3 agents)

| Agent | Role | Key Responsibility |
|---|---|---|
| CEO Agent | Strategic direction | Product vision validation, go/no-go decisions |
| CTO Agent | Technical leadership | Architecture approval, tech stack decisions |
| CFO Agent | Financial oversight | Budget validation, cost-benefit analysis |

### Cofounder Team (3 agents)

| Agent | Role | Key Responsibility |
|---|---|---|
| Product Cofounder | Product strategy | PRD validation, market fit assessment |
| Technical Cofounder | Technical strategy | System design review, scalability decisions |
| Growth Cofounder | Growth strategy | GTM validation, growth metric definition |

### Product Team (5 agents)

| Agent | Role | Key Responsibility |
|---|---|---|
| Product Manager | Requirements | Spec writing, backlog prioritization, acceptance criteria |
| UX Designer | User experience | User flows, wireframes, usability validation |
| UX Reviewer | UX quality gate | Heuristic evaluation, accessibility audit, design compliance |
| Spec Miner | Requirement extraction | Unstructured docs to structured specs |
| Design Sprint Lead | Rapid ideation | Compressed design sprint facilitation |

### Engineering Team (8 agents)

| Agent | Role | Key Responsibility |
|---|---|---|
| Architect | System design | Module boundaries, API contracts, DB schemas |
| Backend Engineer | Server-side code | APIs, business logic, database operations (TDD) |
| Frontend Engineer | Client-side code | Components, pages, state management, Storybook |
| Data Engineer | Data pipelines | ETL, data models, analytics infrastructure |
| DevOps Engineer | Infrastructure | CI/CD, IaC, environments, monitoring setup |
| QA Engineer | Quality validation | Test plans, integration tests, E2E tests |
| SRE Engineer | Reliability | Monitoring, alerting, SLOs, runbooks |
| Security Reviewer | Security gate | OWASP, dependency audit, auth review, secret scanning |

### Sales Team (3 agents)

| Agent | Role | Key Responsibility |
|---|---|---|
| Sales Strategist | Sales planning | Pricing model, sales funnel design |
| Demo Builder | Product demos | Demo environment setup, showcase scripts |
| Proposal Writer | Sales collateral | Pitch decks, proposals, competitive positioning |

### Marketing Team (3 agents)

| Agent | Role | Key Responsibility |
|---|---|---|
| Content Strategist | Content planning | Blog posts, landing pages, SEO strategy |
| Brand Manager | Brand consistency | Messaging, tone, visual identity enforcement |
| Analytics Lead | Marketing metrics | Campaign tracking, conversion analysis |

### Governance Team (5 agents)

| Agent | Role | Key Responsibility |
|---|---|---|
| Checker | First gate | Compilation, tests, linting, security scan, ticket compliance |
| Reviewer | Second gate | Code quality, architecture alignment, test coverage |
| Approver | Final gate | Business validation, governance compliance, merge auth |
| FinOps Analyst | Cost governance | Cloud cost tracking, budget alerts, rightsizing |
| Compliance Agent | Regulatory | Policy enforcement, audit trail, regulatory checks |

### Operations Team (5 agents)

| Agent | Role | Key Responsibility |
|---|---|---|
| Ralph Controller | Orchestrator | Routes work, tracks progress, manages flow. NEVER implements. |
| Release Manager | Release ops | Release branching, changelog, deployment, rollback |
| Integration Agent | External sync | JIRA/Confluence/GitHub synchronization |
| Memory Agent | Knowledge ops | Context loading, learning capture, pattern promotion |
| Pipeline Agent | Async execution | Pipeline management, background task orchestration |

## Agent Execution Model

Agents execute ONLY inside Temporal workflow steps.

```
Temporal Workflow
  └── Step 1: assigned_agent=product-manager
       ├── Read memory (Temporal activity)
       ├── Execute task (Temporal activity)
       ├── Record contribution (Temporal activity)
       └── Write learning (Temporal activity)
  └── Step 2: assigned_agent=architect
       ├── Read memory
       ├── Execute task
       ├── Record contribution
       └── Write learning
  └── ...
```

Each step:
1. Agent assigned by workflow definition
2. Execution tracked in Temporal event history
3. Contribution recorded in product repo
4. Step completion triggers next step

No agent runs outside a workflow. No freelancing.

## Agent Communication

Two channels:

1. **Temporal signals** — async. Agent-to-agent messages within workflows. Handoffs, status updates, escalations.
2. **FastAPI sync** — request/response. UI queries agent state. Dashboard reads. Status checks.

All communication logged. All state in Postgres. Temporal event history is the source of truth.

## Learning Contract

Every agent MUST:

1. **Before execution**: Read relevant memory from product repo `.claude/memory/`. Temporal activity loads context.
2. **After completion**: Write structured learnings to product repo `.claude/learning/`. Temporal activity persists.
3. **Never self-mutate**: No agent changes its own definition without approval.
4. **Promote through process**: Learnings promoted only via memory-agent approval workflow.

No shortcuts. No skipping. The contract is enforced by Temporal workflow logic.

## Brain Integration (Persistent Memory DB)

In addition to file-based memory in `.claude/memory/`, agents read and write the Brain -- a Postgres-backed persistent memory system at `/api/v1/brain/`. The Brain provides structured, queryable storage that replaces flat-file memory for most operations.

### Agent-Brain Protocol

Every agent follows this protocol during workflow step execution:

1. **Before execution**: Query `/brain/memory` for relevant memories (scoped to current session, product, and factory). Query `/brain/patterns` for proven patterns in the current domain. Query `/brain/decisions` for relevant architecture decisions.
2. **During execution**: Write conversation entries to `/brain/conversations` with the current workflow step and interaction mode.
3. **After completion**: Write new memories to `/brain/memory` (session-scoped by default). Record any new patterns discovered to `/brain/patterns`. Record any decisions made to `/brain/decisions`.

### Memory Promotion

Memories promote through scopes: session -> product -> factory. The Memory Agent evaluates session-level memories for promotion to product-level based on reuse frequency and validation. Product-level patterns that succeed across multiple products are promoted to factory-level by the CoE.

### Brain vs File Memory

| | Brain (Postgres) | File Memory (.claude/memory/) |
|---|---|---|
| **Storage** | Postgres via `/api/v1/brain/` | Markdown files in product repo |
| **Queryable** | Yes -- filtered by scope, category, domain | Manual search |
| **Cross-product** | Yes -- factory-scoped memories shared | No -- per-repo only |
| **Structured** | Yes -- typed records with metadata | Semi-structured markdown |
| **Promotable** | Yes -- session -> product -> factory | Manual copy |

Agents use Brain as the primary memory source. File memory remains as a fallback and for offline scenarios.
