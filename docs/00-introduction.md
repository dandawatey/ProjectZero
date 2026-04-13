# 00 - Introduction to ProjectZeroFactory

## What It Is

ProjectZeroFactory is a **managed AI agent platform** that builds software products through governed Temporal workflows. It is not a code generator. Not a chatbot. Not a prompt library.

It is a **workflow-driven AI software factory operating system**.

Every action -- spec, arch, implement, test, release -- executes as a Temporal workflow. No workflow, no work. No integration, no execution. No ticket, no code.

## Architecture

```
React (Control Tower) --> FastAPI (API) --> Postgres (State) --> Temporal (Execution Engine) --> Agents
```

- **Control Tower**: React dashboard. Monitors workflows, products, agents, governance gates.
- **FastAPI**: Backend API. Receives commands, dispatches Temporal workflows, reads/writes state.
- **Postgres**: Source of truth. Product state, workflow state, governance records, audit trail.
- **Temporal**: Execution engine. Every feature = workflow. Every governance gate = signal. Every retry = built-in.
- **Agents**: 8 teams, 22+ specialized agents. Execute within Temporal activities. No freelancing.
- **Redis**: Caching, rate limiting, session state.

## What's Inside

```
ProjectZeroFactory/
  .claude/              # Factory OS -- agents, skills, workflows, commands, core
    core/               # System prompts, orchestration, config
    agents/             # 8 teams of specialized agents
    commands/           # Slash commands (/factory-init, /implement, /release, etc.)
    workflows/          # Temporal workflow definitions
    skills/             # Reusable agent capabilities
  platform/             # Infrastructure
    backend/            # FastAPI -- API layer, Temporal client, DB models
    frontend/           # React -- Control Tower dashboard
    temporal/           # Temporal worker, workflow/activity definitions
  docs/                 # This documentation
  examples/             # Reference implementations
```

## Key Principles

### 1. Workflow-First

Everything is a Temporal workflow. Feature development = workflow. Governance review = child workflow. Integration sync = workflow. No direct execution of anything. Temporal handles retries, timeouts, state, and recovery.

### 2. No Integration No Execution

Before any workflow runs, the **integration gate** validates:
- GitHub (repo access, branch permissions)
- JIRA (project exists, API token valid)
- Confluence (space exists, write access)
- Temporal (server running, namespace exists)
- Postgres (connected, migrations current)
- Redis (connected, responsive)
- Anthropic (API key valid, model accessible)

If any gate fails, workflows are blocked. No silent failures. No partial execution.

### 3. TDD -- Not Optional

Implementation workflows enforce test-first. Tests committed before or with implementation code. Coverage thresholds enforced by Temporal activity gates. No test, no merge.

### 4. Governance Chain

Every artifact passes through **Maker-Checker-Reviewer-Approver** -- implemented as a Temporal child workflow with signal-based gates. Bounded retries (max 3 per gate, max 5 total). Escalation on exhaustion.

### 5. Product Repos Are Separate

Factory = reusable OS. Product = separate git repo. Factory provides agents, skills, workflows, commands, templates, governance, platform infrastructure. Product provides code, tests, state, configs. Factory upgrades propagate to all products without touching product code.

## 8-Phase Model

| Phase | Name | What Happens |
|---|---|---|
| 0 | Factory Init | Validate integrations, initialize stores, confirm readiness |
| 1 | Product Creation | Bootstrap product repo, create GitHub/JIRA/Confluence resources |
| 2a | Vision-to-PRD | Generate PRD + BMAD from a vision statement |
| 2b | Business Discovery | TAM, competitive analysis, team model, business model |
| 3 | Specification | Modules, epics, stories, contracts, acceptance criteria |
| 4 | Architecture | ADRs, patterns, infrastructure, security, observability |
| 5 | Implementation | TDD, governance chain per story, branch/PR/merge |
| 6 | Quality + Release | Final testing, security scan, staging, production, monitoring |
| 7 | Business Planning | Financial model, GTM strategy, pitch deck |
| 8 | Operations | Monitor, optimize, incident response, learning capture |

## Agent Teams

8 teams. Each agent has a defined scope. No overlap. No freelancing.

| Team | Agents |
|---|---|
| CXO | Strategic oversight, portfolio decisions |
| Cofounder | Product vision, market strategy |
| Product | Product manager, UX reviewer |
| Engineering | Architect, backend/frontend/data engineers, QA |
| Sales | Sales strategy, demo, competitive positioning |
| Marketing | Content, campaigns, brand |
| Governance | Checker, reviewer, approver, security reviewer |
| Operations | SRE, DevOps, release manager, FinOps |

## What Comes Next

- [02 - How to Start a New Product](02-how-to-start-a-new-product.md) -- step-by-step from zero to running product
- [03 - Org Operating Model](03-org-operating-model.md) -- factory vs product boundary, portfolio management
- [04 - Governance Model](04-governance-model.md) -- how governance enforces quality through Temporal
- [05 - Stage-by-Stage Workflow](05-stage-by-stage-workflow.md) -- the 8-phase model in detail
- [14 - Command Reference](14-command-reference.md) -- all slash commands
