# ProjectZeroFactory

Managed AI Agent Platform for Building Products.

## What This Is

Workflow-driven AI software factory. Features = workflows. Agents execute. Humans approve. Everything visible.

```
React (Control Tower) → FastAPI (API) → Postgres (State) → Temporal (Engine) → Agents (Work)
```

## What This Is NOT

- Not a code generator
- Not a product repo
- Not a chatbot wrapper

## Quick Start

```bash
git clone git@github.com:dandawatey/ProjectZero.git ProjectZeroFactory
cd ProjectZeroFactory
code .

/factory-init              # validate factory
/bootstrap-product         # create product repo → separate git repo
```

### Have a PRD?
```
/spec → /arch → /implement → /check → /review → /approve → /release
```

### Have a vision but no PRD?
```
/vision-to-prd             # generates PRD + BMAD from your idea
/business-docs --phase discovery   # TAM-SAM-SOM, competitive, team, biz model
/spec → /arch → /implement → ...
```

### After build, need investor docs?
```
/business-docs --phase planning    # financials, costing, GTM, pitch deck
```

## Complete Phase Flow

| Phase | Command | What Happens |
|-------|---------|-------------|
| 0 | `/factory-init` | Validate factory |
| 1 | `/bootstrap-product` | Create product repo |
| 2a | `/vision-to-prd` | Vision → PRD + BMAD (if no PRD) |
| 2b | `/business-docs discovery` | Market analysis, team, biz model |
| 3 | `/spec` | Features → epics → stories |
| 4 | `/arch` | System design, contracts, tech stack |
| 5 | `/implement` | Per-feature Temporal workflows (TDD) |
| 6 | `/check → /review → /approve → /release` | Quality → deploy |
| 7 | `/business-docs planning` | Financials, GTM, pitch deck |
| 8 | `/monitor → /optimize` | Operations |

## Platform Architecture

```
ProjectZeroFactory/
├── .claude/                    ← AI operating system
│   ├── agents/                 ← 34 agents, 7 teams
│   ├── skills/                 ← 17 skill packages
│   ├── workflows/              ← workflow definitions
│   ├── commands/               ← 17+ commands
│   ├── guardrails/             ← governance rules
│   ├── templates/              ← reusable templates + product skeleton
│   └── ...                     ← memory, learning, recovery, design-system
├── platform/                   ← execution infrastructure
│   ├── backend/                ← FastAPI + Postgres (business truth)
│   ├── frontend/               ← React control tower (see everything)
│   └── temporal/               ← Temporal workflows + activities + workers
├── docs/                       ← 20+ process docs
├── examples/                   ← sample BMAD, PRD, module, ticket
└── scripts/                    ← bootstrap + validation
```

## Agent Teams (34 agents)

| Team | Agents |
|------|--------|
| CXO | CEO, CTO, CPO, CFO, CMO, CRO, Ralph Controller |
| Product | Product Manager, Product Analyst, UX Researcher |
| Engineering | Architect, Backend, Frontend, Data, DevOps, QA, SRE |
| Sales | Sales Strategist, Customer Success |
| Marketing | Marketing Strategist, Content Creator |
| Governance | Checker, Reviewer, Approver, Security Reviewer, UX Reviewer |
| Operations | Release Manager, FinOps, Integration, Validators, Pipeline, Memory |

## Temporal Workflows

| Workflow | Purpose |
|----------|---------|
| VisionToPRDWorkflow | Generate PRD from vision |
| BusinessDocsWorkflow | Business document suite |
| FeatureDevelopmentWorkflow | 10-stage feature build |
| BugFixWorkflow | Bug triage → fix → deploy |
| QAValidationWorkflow | Quality gates |
| DeploymentReadinessWorkflow | Pre-deploy checks |
| ReleaseGovernanceWorkflow | Release sign-offs |
| MakerCheckerReviewerWorkflow | Approval chain (child) |

## Governance

- **BMAD** → business model before any code
- **SPARC** → Specification → Architecture → Realization → Completion
- **TDD** → tests first, always
- **No Ticket, No Work** → every change traced
- **Maker → Checker → Reviewer → Approver** → four-eye principle

## Docs

| Doc | Topic |
|-----|-------|
| [Repository Boundaries](docs/repository-boundaries.md) | Factory vs product |
| [Architecture](docs/architecture-temporal.md) | Temporal + FastAPI + React |
| [Workflow Catalog](docs/workflow-catalog.md) | All workflow types |
| [Command Reference](docs/14-command-reference.md) | All commands |
| [Example Flow](docs/15-example-new-product-flow.md) | End-to-end walkthrough |
| [How It Works](docs/01-how-projectzerofactory-works.md) | System architecture |
| [Governance](docs/04-governance-model.md) | Rules and process |
