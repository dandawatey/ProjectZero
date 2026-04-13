# 03 - Org Operating Model

## Core Boundary: Factory vs Product

Two repos. Always.

| | Factory Repo | Product Repo |
|---|---|---|
| **What** | Reusable OS | Specific product |
| **Contains** | Agents, skills, workflows, commands, templates, governance, platform/ | Application code, tests, state, configs |
| **Git** | `ProjectZeroFactory` | `MyProduct`, `AnotherProduct`, etc. |
| **Owned by** | Platform/CoE team | Product team |
| **Changes** | Factory upgrades | Product development |

Factory is the engine. Product is the car. You don't fork the engine for each car.

## What Factory Provides

### .claude/ -- The OS

```
.claude/
  core/           # System prompts, orchestration config
  agents/         # 8 teams of specialized agents
  commands/       # Slash commands (/factory-init, /spec, /implement, etc.)
  workflows/      # Temporal workflow definitions
  skills/         # Reusable agent capabilities
  templates/      # Scaffolding templates for products
  checklists/     # Definition-of-done, governance checklists
  guardrails/     # Safety rules, scope limits
```

### platform/ -- The Infrastructure

```
platform/
  backend/        # FastAPI API layer, Temporal client, DB models, migrations
  frontend/       # React Control Tower -- dashboard for monitoring everything
  temporal/       # Temporal worker, workflow definitions, activity implementations
```

### Governance

- BMAD/PRD validation rules
- SPARC stage gates (Temporal-enforced)
- Maker-Checker-Reviewer-Approver chain (Temporal child workflow)
- TDD enforcement
- No Ticket No Work enforcement
- Integration gate validation

## What Product Provides

Product repo contains only product-specific artifacts:

- **Source code** -- the actual application
- **Tests** -- unit, integration, E2E
- **State** -- product-specific Postgres records
- **Configs** -- product `.env`, deployment configs
- **JIRA tickets** -- tracked in JIRA, synced by factory workflows
- **Confluence pages** -- published by factory workflows
- **GitHub PRs** -- created by factory workflows

Product repos have NO factory code. No agents. No workflows. No platform.

## Portfolio Model

Factory manages multiple products simultaneously. Postgres tracks all of them.

```
Factory (1) --> Products (many)
  |               |
  |               +-- MyProduct (GitHub repo, JIRA project, Confluence space)
  |               +-- AnotherProduct (GitHub repo, JIRA project, Confluence space)
  |               +-- ThirdProduct (GitHub repo, JIRA project, Confluence space)
  |
  +-- Temporal: workflows for all products
  +-- Postgres: state for all products
  +-- Redis: cache for all products
  +-- Control Tower: dashboard for all products
```

### Portfolio Tracking

Postgres stores per-product:
- Current phase (0-8)
- Workflow state (active workflows, completed, failed)
- Agent activity (who did what, when)
- Governance records (every gate pass/fail)
- Velocity metrics (stories/sprint, cycle time)
- Quality metrics (coverage, defect density, security findings)

Control Tower (React) visualizes all of this across the portfolio.

## Factory Upgrades

Factory is versioned. Products pin to a factory version.

```
/factory-upgrade --version 2.1.0
```

What upgrades touch:

| Upgraded | NOT Touched |
|---|---|
| Agents | Product source code |
| Commands | Product tests |
| Workflows | Product configs |
| Skills | Product state in Postgres |
| Templates | Product JIRA/Confluence content |
| Platform (backend, frontend, temporal) | Product GitHub repo |
| Governance rules | |
| Checklists | |

Upgrade process (Temporal workflow):
1. Pull new factory version
2. Diff `.claude/` and `platform/`
3. Apply non-conflicting changes
4. Flag conflicts for manual resolution
5. Run integration gate to validate
6. Update factory version record in Postgres

Products don't need to do anything. Factory upgrades are factory-side. Products keep building.

## Org Scaling

### Small (1-5 products)

- 1 factory instance
- 1 person maintains factory (part-time)
- Single Temporal namespace
- Single Postgres database

### Medium (5-20 products)

- 1 factory instance
- 2-3 person CoE team (dedicated)
- Temporal namespace per product (isolation)
- Postgres with schema-per-product or shared with RLS

### Large (20+ products)

- Factory repo with CI/CD, automated testing, staged rollouts
- 4-6 person CoE team
- Temporal cluster (multiple workers, high availability)
- Postgres cluster (read replicas, connection pooling)
- Redis cluster
- Control Tower with role-based access per product team

## Cross-Product Patterns

Factory learns across products. Temporal workflow execution data feeds back into factory improvements.

- If 3 products fail at the same governance gate, the gate rule needs tuning
- If an agent consistently produces low-quality output in a domain, the agent prompt needs refinement
- If a workflow stage times out frequently, the activity timeout or retry policy needs adjustment

Learnings stored in Postgres. Surfaced in Control Tower. Applied by CoE to next factory version.

### Brain: Cross-Product Learning at the DB Level

The Brain (`/api/v1/brain/`) provides structured, queryable cross-product learning that goes beyond Temporal execution data:

- **Patterns** (`/brain/patterns`) -- proven patterns with success rates are promoted from product to factory scope. When a pattern succeeds across 3+ products, it becomes a factory-level recommendation.
- **Decisions** (`/brain/decisions`) -- architecture decisions and their outcomes are stored with full context. New products can query factory-level decisions to avoid repeating analysis.
- **Memory promotion** -- session-level learnings promote to product-level, then to factory-level. The Brain's scoping model (factory/product/session) ensures knowledge flows upward automatically.

This means the factory gets smarter with every product it builds, at the database level rather than through manual CoE curation alone.
