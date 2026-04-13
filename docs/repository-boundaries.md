# Repository Boundaries

## The Factory Structure

ProjectZeroFactory is a single repository containing the operating system (`.claude/`), the platform (`platform/`), documentation, and tooling.

```
ProjectZeroFactory (FACTORY)
├── .claude/                          # Factory OS (agents, workflows, commands, guardrails)
│   ├── agents/                       # Agent definitions by team
│   │   ├── cxo-team/
│   │   ├── engineering-team/
│   │   ├── product-team/
│   │   └── ...
│   ├── commands/                     # Slash command definitions
│   ├── workflows/                    # Temporal workflow definitions
│   ├── guardrails/                   # Quality and governance rules
│   ├── checklists/                   # Validation checklists
│   ├── core/                         # Build methodology, architecture principles
│   ├── memory/                       # Org-level memory
│   ├── learning/                     # Promoted patterns and learnings
│   ├── recovery/                     # Recovery protocols
│   ├── runtime/                      # Execution graph, state machines
│   ├── skills/                       # Reusable skill packages
│   ├── templates/                    # Artifact templates
│   └── devops/                       # Environment and health check configs
├── platform/                         # Temporal-driven execution platform
│   ├── backend/                      # FastAPI + Postgres (API + State)
│   │   ├── app/
│   │   │   ├── api/                  # FastAPI route handlers
│   │   │   ├── models/               # SQLAlchemy/Pydantic models
│   │   │   ├── services/             # Business logic services
│   │   │   ├── sync/                 # Temporal → Postgres sync layer
│   │   │   └── main.py               # FastAPI application entry
│   │   ├── migrations/               # Alembic database migrations
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   ├── frontend/                     # React Control Tower UI
│   │   ├── src/
│   │   │   ├── components/           # React components
│   │   │   ├── pages/                # Page-level views
│   │   │   ├── hooks/                # Custom React hooks
│   │   │   ├── api/                  # API client layer
│   │   │   └── App.tsx
│   │   ├── package.json
│   │   └── Dockerfile
│   └── temporal/                     # Python Temporal SDK (workflows + activities + workers)
│       ├── workflows/                # Workflow definitions
│       ├── activities/               # Activity implementations
│       ├── workers/                  # Worker entry points
│       ├── shared/                   # Shared types, constants
│       ├── requirements.txt
│       └── Dockerfile
├── docs/                             # Process and architecture documentation
├── examples/                         # Sample BMAD, PRD, modules, tickets
└── scripts/                          # Bootstrap, validation, and utility scripts
```

## Product Repository Structure

Product repos are instances created from the factory. They contain product code and product-specific state.

```
ProductRepo (PRODUCT)
├── .claude/
│   ├── delivery/                     # Product delivery state (tickets, sync)
│   ├── reports/                      # Product reports
│   ├── recovery/                     # Product recovery checkpoints
│   ├── memory/                       # Product memory (decisions, patterns)
│   ├── learning/                     # Product-level learnings
│   ├── integrations/                 # Product integration config
│   └── feature-flags/                # Product feature flags
├── src/                              # Product source code
├── tests/                            # Product tests
├── packages/                         # Product packages (ui, shared)
├── docs/                             # Product documentation
├── .env                              # Product secrets (never committed)
└── README.md
```

## What the Factory Owns

| Category | Location | Changes How |
|----------|----------|-------------|
| Agents | `.claude/agents/` | `/factory-upgrade` |
| Workflows | `.claude/workflows/` | `/factory-upgrade` |
| Commands | `.claude/commands/` | `/factory-upgrade` |
| Guardrails | `.claude/guardrails/` | `/factory-upgrade` |
| Checklists | `.claude/checklists/` | `/factory-upgrade` |
| Core | `.claude/core/` | `/factory-upgrade` |
| Skills | `.claude/skills/` | `/factory-upgrade` |
| Templates | `.claude/templates/` | `/factory-upgrade` |
| **Backend API** | `platform/backend/` | PR + review |
| **Frontend UI** | `platform/frontend/` | PR + review |
| **Temporal Workflows** | `platform/temporal/` | PR + review (workflow versioning required) |
| Docs | `docs/` | Manual |
| Examples | `examples/` | Manual |
| Scripts | `scripts/` | Manual |

## What the Product Owns

| Category | Location | Created How |
|----------|----------|-------------|
| Source Code | `src/` | `/implement` (via Temporal workflow) |
| Tests | `tests/` | `/implement` (via Temporal workflow) |
| Packages | `packages/` | `/design-system-init` |
| Delivery State | `product repo .claude/delivery/` | Temporal workflow state sync |
| Reports | `.claude/reports/` | Auto-generated by workflows |
| Recovery State | `.claude/recovery/` | Temporal handles recovery natively |
| Memory | `.claude/memory/` | Built during spec, arch, implement stages |
| Learnings | `.claude/learning/` | Built during implementation |
| Integration Config | `.claude/integrations/` | `/bootstrap-product` |
| Feature Flags | `.claude/feature-flags/` | Temporal workflow configuration |
| Product Docs | `docs/` | `/spec`, `/arch`, `/release` |

## Platform Layer Boundaries

The `platform/` directory has strict internal boundaries:

| Component | Responsibility | Does NOT Do |
|-----------|---------------|-------------|
| **backend** (FastAPI) | API endpoints, request validation, Postgres reads/writes, authentication, authorization, Temporal client calls | Execute workflow logic, run agents, make business decisions |
| **frontend** (React) | UI rendering, user interaction, API calls, real-time state display | Direct Temporal access, direct Postgres access, agent execution |
| **temporal** (Python SDK) | Workflow orchestration, activity execution, signal handling, retry logic, state management | Direct Postgres writes (uses sync layer), UI rendering, API serving |

### Data Flow Between Platform Components

```
React UI
  | HTTP/SSE
  v
FastAPI API
  | Temporal Client SDK        | SQLAlchemy
  v                            v
Temporal Server              Postgres
  | Activity execution
  v
Temporal Workers
  | Sync layer (HTTP to FastAPI)
  v
FastAPI API → Postgres
```

Key constraint: Temporal workers sync state to Postgres ONLY through the FastAPI sync layer, never through direct database writes. This ensures all writes go through validation and audit logging.

## Rules

1. **Factory never contains live product state.** No active tickets, no queue items, no product-specific data in the factory repo.
2. **Product repos never modify factory files.** Factory changes require `/factory-upgrade` or PRs to the factory repo.
3. **Templates flow one way**: Factory -> Product (via `/bootstrap-product`). Never reverse.
4. **Learnings flow upward**: Product -> Factory (via promotion through memory-agent approval).
5. **Governance flows downward**: Factory defines rules. Products inherit and may extend (never weaken).
6. **Platform is shared infrastructure.** All products connect to the same platform instance. Product isolation is enforced at the data layer (product_id foreign keys).
7. **Temporal workflows are versioned.** Breaking changes to workflow definitions require workflow versioning to handle in-flight executions.
8. **Database migrations are forward-only.** Every Alembic migration must have a working downgrade path for rollback.
