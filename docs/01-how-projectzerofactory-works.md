# 01 -- How ProjectZeroFactory Works

## Architecture Overview

ProjectZeroFactory is a governed product development system with five components:

```
┌─────────────────────────────────────────────────────────────┐
│  React UI (Control Tower)                                    │
│  - Feature dashboard, workflow status, approval gates        │
│  - Real-time updates via SSE                                 │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP / SSE
┌──────────────────────▼──────────────────────────────────────┐
│  FastAPI API (Business Logic + State Management)             │
│  - REST endpoints for all operations                         │
│  - Request validation, auth, audit logging                   │
│  - Temporal client: starts workflows, sends signals, queries │
└──────────┬───────────────────────────────┬──────────────────┘
           │ SQLAlchemy                    │ Temporal Client SDK
┌──────────▼──────────┐    ┌──────────────▼──────────────────┐
│  Postgres            │    │  Temporal Server                 │
│  - Feature state     │    │  - Workflow orchestration         │
│  - Approval records  │    │  - Activity scheduling            │
│  - Audit trail       │    │  - Signal routing                 │
│  - Release history   │    │  - Retry and failure handling     │
└─────────────────────┘    └──────────────┬──────────────────┘
                                          │ Task queues
                           ┌──────────────▼──────────────────┐
                           │  Temporal Workers                 │
                           │  - Execute activities             │
                           │  - Invoke agents (Claude)         │
                           │  - Sync state back via FastAPI    │
                           └──────────────────────────────────┘
```

## Brain (Persistent Memory DB)

ProjectZero includes a Postgres-backed persistent memory system called the Brain, accessible at `/api/v1/brain/`. It has four subsystems:

- **`/brain/memory`** -- persistent memories scoped to factory, product, or session. Categorized and promotable (session -> product -> factory).
- **`/brain/decisions`** -- architecture decisions with context, options considered, and rationale.
- **`/brain/patterns`** -- proven patterns with success rates and anti-patterns.
- **`/brain/conversations`** -- conversation history per workflow step, including interaction mode.

Agents read the brain before executing any activity and write back after completion. This replaces file-based memory in `.claude/memory/` with a queryable, structured database.

## Interaction Modes

Every workflow step supports four user interaction modes:

- **chat** -- discuss, ask questions, clarify requirements
- **brainstorm** -- explore ideas, challenge assumptions, generate alternatives
- **plan** -- structure approach, define steps, set priorities
- **implement** -- execute, write code, generate artifacts

Users can switch modes at any step via the Control Tower UI or by sending a Temporal signal. The current mode is stored in the Brain conversations table.

## Activity Monitor

Central user activity tracking is available at `/api/v1/activities/`. Every user action is logged -- workflow starts, approvals, commands, navigation. The Activity Monitor provides:

- Activity summary dashboard with category breakdown
- User timeline view
- System event tracking (integration changes, errors, deployments)

Activity data feeds into the Control Tower dashboard for real-time visibility.

## Core Principle: Feature = Workflow

Every feature, bug fix, release, and governance action is a Temporal workflow. There is no work outside workflow context. This means:

- Every action is tracked, retryable, and auditable
- Every state transition is recorded in Postgres with a correlation_id
- Every human decision arrives as a Temporal signal
- Every failure is handled by Temporal's retry and replay mechanisms
- Workflow state survives crashes, restarts, and network partitions

## The .claude/ Directory as Operating System

The `.claude/` directory defines the factory's operating system -- agents, workflows, commands, guardrails, and governance rules:

```
.claude/
  agents/           # Agent definitions (role, scope, inputs, outputs)
  checklists/       # Pre-flight and post-flight validation checklists
  commands/         # Slash command definitions (user interface)
  core/             # Build methodology, architecture principles, BMAD
  devops/           # Environment and health check configuration
  guardrails/       # Quality, security, and governance rules
  learning/         # Promoted patterns from product instances
  memory/           # Org-level persistent memory
  recovery/         # Recovery and resume protocols
  runtime/          # Execution graph, state machines, agent protocol
  skills/           # Reusable capability packages (code-reviewer, etc.)
  templates/        # Templates for all artifact types
  workflows/        # Workflow definitions (Temporal-backed)
```

## The platform/ Directory as Execution Engine

The `platform/` directory contains the running infrastructure:

```
platform/
  backend/          # FastAPI application (API + Postgres state management)
  frontend/         # React application (Control Tower UI)
  temporal/         # Python Temporal SDK (workflows, activities, workers)
```

### Backend (FastAPI + Postgres)

FastAPI is the API layer and single source of business truth for state:

- **REST API**: All operations go through FastAPI endpoints
- **Postgres**: Persistent state for features, approvals, releases, audit trail
- **Temporal Client**: Starts workflows, sends signals (approvals), queries workflow state
- **Sync Layer**: Receives state updates from Temporal workers, writes to Postgres with idempotency

### Frontend (React Control Tower)

React provides the human interface to the factory:

- **Feature Dashboard**: View all features, their current workflow stage, blockers
- **Approval Queue**: Pending approval requests across all governance gates
- **Workflow Detail**: Drill into any workflow to see stage history, artifacts, decisions
- **Release Board**: Release pipeline with sign-off status
- **Real-time**: Server-Sent Events (SSE) from FastAPI for live status updates

### Temporal (Python SDK)

Temporal is the execution engine:

- **Workflows**: Orchestrate multi-stage processes (feature dev, bug fix, release)
- **Activities**: Individual units of work executed by agents
- **Workers**: Python processes that poll task queues and execute activities
- **Signals**: External inputs (human approvals) that unblock waiting workflows
- **Queries**: Read workflow state without affecting execution

## How Commands Map to Workflows

Commands are the user interface. Each command maps to a Temporal operation:

| Command | Temporal Action |
|---------|----------------|
| `/implement` | Start `feature_development_workflow` |
| `/spec` | Start `feature_development_workflow` at specification stage |
| `/arch` | Query current workflow, advance to architecture stage |
| `/check` | Query `qa_validation_workflow` status |
| `/review` | Send review signal to running workflow |
| `/approve` | Send approval signal to running workflow |
| `/release` | Start `release_governance_workflow` |
| `/monitor` | Query workflow and deployment status |

## Data Flow: Feature Lifecycle

```
1. User creates feature in React UI
   └─> POST /api/features → FastAPI creates record in Postgres

2. FastAPI starts Temporal workflow
   └─> temporal_client.start_workflow(FeatureDevelopmentWorkflow, ...)

3. Temporal executes intake_activity
   └─> Worker picks up from task queue → Agent processes → Sync result to FastAPI → Postgres

4. Temporal executes specification_activity
   └─> Agent writes spec → Starts MCRA child workflow for governance

5. MCRA creates approval request
   └─> Activity calls FastAPI → Creates approval_request in Postgres → React UI shows pending

6. Human approves in React UI
   └─> POST /api/approvals/{id} → FastAPI sends signal to Temporal → MCRA advances

7. Workflow continues through design → architecture → implementation → testing

8. Testing stage starts qa_validation_workflow as child
   └─> Unit tests → Integration tests → E2E tests → Coverage check → Report

9. Review stage starts another MCRA child workflow
   └─> Checker → Reviewer → Approver gates with signals

10. Release readiness starts deployment_readiness_workflow
    └─> Environment → Config → Infra → Monitoring → Rollback → Security

11. Release governance collects sign-offs
    └─> Engineering → Product → Ops sign-offs via signals

12. Completion: deploy, verify, capture learnings
    └─> Workflow completes → Final state synced to Postgres → UI reflects completion
```

## Factory Repo vs Product Repo

### Factory Repo (This Repository)

Contains:
- The `.claude/` OS (agents, workflows, commands, guardrails, core rules)
- The `platform/` execution infrastructure (backend, frontend, temporal)
- Documentation (`docs/`)
- Examples and scripts

The factory repo is maintained by the Center of Excellence. It is versioned. Products track which factory version they were created from.

### Product Repo (Instance)

When you run `/factory-init` followed by `/bootstrap-product`, the factory creates a product instance. This is a separate repository that contains:
- Product source code
- Product-specific `.claude/` state (memory, learnings, delivery tracking)
- Product configuration

The product repo connects to the shared platform for workflow execution. Product isolation is enforced at the data layer via `product_id`.

## Workflow Types

| Workflow | Purpose |
|----------|---------|
| `feature_development_workflow` | End-to-end feature delivery (10 stages) |
| `bug_fix_workflow` | Bug triage through deployment (7 stages) |
| `qa_validation_workflow` | Full test pipeline (6 stages) |
| `deployment_readiness_workflow` | Pre-deploy validation (7 checks) |
| `release_governance_workflow` | Release approval chain (6 stages) |
| `maker_checker_reviewer_approver_workflow` | Governance gate (3 sequential gates) |

## Configuration

### Platform Configuration

| Variable | Purpose |
|----------|---------|
| `DATABASE_URL` | Postgres connection string |
| `TEMPORAL_HOST` | Temporal server address |
| `TEMPORAL_NAMESPACE` | Temporal namespace |
| `FASTAPI_URL` | Backend API URL (for sync layer) |
| `SENTRY_DSN` | Error tracking |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | OpenTelemetry collector |

### Product Configuration

| Variable | Purpose |
|----------|---------|
| `JIRA_BASE_URL` | Atlassian instance URL |
| `JIRA_PROJECT_KEY` | JIRA project key |
| `CONFLUENCE_SPACE_KEY` | Confluence documentation space |
| `GITHUB_ORG` | GitHub organization |
| `PRODUCT_ID` | Unique product identifier in the platform |

## Observability

Every component emits telemetry:

- **Prometheus**: Workflow duration, activity success/failure rates, queue depths
- **Grafana**: Dashboards for workflow pipeline, approval latency, release frequency
- **Sentry**: Error tracking with Temporal workflow context
- **OpenTelemetry**: Distributed traces from React -> FastAPI -> Temporal -> Workers

## Offline Mode

When external integrations (JIRA, Confluence, GitHub) are unavailable, the factory operates in offline mode:
- Tickets stored as JSON in product repo `.claude/delivery/jira/issues/`
- Pages stored as Markdown in product repo `.claude/delivery/confluence/pages/`
- Git operations performed on local repository
- Reconciliation syncs when integrations come back online

The platform itself (FastAPI, Postgres, Temporal) must be running for workflow execution. There is no fully offline workflow execution mode.
