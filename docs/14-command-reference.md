# 14 - Command Reference

## 8-Phase Flow

```
Phase 0: /factory-init
Phase 1: /bootstrap-product, /setup
Phase 2: /vision-to-prd, /business-docs --phase discovery
Phase 3: /spec
Phase 4: /arch
Phase 5: /implement
Phase 6: /check, /review, /approve
Phase 7: /release, /business-docs --phase planning
Phase 8: /monitor, /optimize
```

Full sequence:
```
/factory-init -> /bootstrap-product -> /vision-to-prd -> /business-docs --phase discovery -> /spec -> /arch -> /implement -> /check -> /review -> /approve -> /release -> /business-docs --phase planning -> /monitor -> /optimize
```

---

## Factory Commands (run in factory repo)

### /factory-init

| Field | Value |
|---|---|
| **Command** | `/factory-init` |
| **Phase** | 0 |
| **Scope** | Factory repo |
| **Purpose** | Validate factory repo is healthy and all 7 required integrations are configured and reachable |
| **Temporal Workflow** | `FactoryInitWorkflow` |
| **Inputs** | None (reads .env and factory structure) |
| **Outputs** | Validation report. All 7 integrations checked: GitHub, JIRA, Confluence, Temporal, Postgres, FastAPI, Claude |
| **Next Command** | `/bootstrap-product` |

### /bootstrap-product

| Field | Value |
|---|---|
| **Command** | `/bootstrap-product` |
| **Phase** | 1 |
| **Scope** | Factory repo (creates product repo) |
| **Purpose** | Create product repo with full .claude OS, configure integrations, create JIRA project, create Confluence space with hub |
| **Temporal Workflow** | `BootstrapProductWorkflow` |
| **Inputs** | Product name, type, stack. Optionally BMAD/PRD. |
| **Outputs** | Initialized product repo. GitHub repo created via API. JIRA project created. Confluence space created with hub page. |
| **Next Command** | `/vision-to-prd` (if no PRD) or `/spec` (if PRD provided) |

### /factory-audit

| Field | Value |
|---|---|
| **Command** | `/factory-audit` |
| **Phase** | Any |
| **Scope** | Factory repo |
| **Purpose** | Check factory for product-state leakage, validate structure, verify standards are current |
| **Temporal Workflow** | `FactoryAuditWorkflow` |
| **Inputs** | None |
| **Outputs** | Health report with pass/fail per check |
| **Next Command** | None (diagnostic) |

### /factory-upgrade

| Field | Value |
|---|---|
| **Command** | `/factory-upgrade` |
| **Phase** | Any |
| **Scope** | Factory repo |
| **Purpose** | Add new agents, skills, workflows, governance rules to the factory |
| **Temporal Workflow** | `FactoryUpgradeWorkflow` |
| **Inputs** | Upgrade specification |
| **Outputs** | Updated factory with new capabilities |
| **Next Command** | None |

---

## Product Commands (run in product repo)

### /vision-to-prd

| Field | Value |
|---|---|
| **Command** | `/vision-to-prd` |
| **Phase** | 2a |
| **Scope** | Product repo |
| **Purpose** | Generate structured PRD and BMAD from raw product vision. System asks clarifying questions, then produces documents. |
| **Temporal Workflow** | `VisionToPRDWorkflow` |
| **Inputs** | Vision text (any format -- paragraph, bullet points, voice transcript) |
| **Outputs** | Structured PRD, BMAD document |
| **Next Command** | `/business-docs --phase discovery` |

### /business-docs

| Field | Value |
|---|---|
| **Command** | `/business-docs` |
| **Phase** | 2b (discovery) or 7 (planning) |
| **Scope** | Product repo |
| **Purpose** | Generate business document suite based on phase |
| **Temporal Workflow** | `BusinessDocsWorkflow` |
| **Inputs** | `--phase discovery` or `--phase planning` |
| **Outputs (discovery)** | TAM-SAM-SOM analysis, competitive analysis, team composition plan, business model canvas |
| **Outputs (planning)** | Financial projections, costing analysis, GTM strategy, pitch deck, data room documents |
| **Next Command** | `/spec` (after discovery) or operations (after planning) |

### /setup

| Field | Value |
|---|---|
| **Command** | `/setup` |
| **Phase** | 1 |
| **Scope** | Product repo |
| **Purpose** | Configure and validate dev environment and integration connections |
| **Temporal Workflow** | `SetupWorkflow` |
| **Inputs** | None (reads .env) |
| **Outputs** | Environment validation report |
| **Next Command** | Next phase command |

### /spec

| Field | Value |
|---|---|
| **Command** | `/spec` |
| **Phase** | 3 |
| **Scope** | Product repo |
| **Purpose** | PM agent decomposes PRD into modules, epics, and stories with acceptance criteria. Creates JIRA tickets automatically. |
| **Temporal Workflow** | `FeatureDevelopmentWorkflow` (intake + spec stages) |
| **Inputs** | PRD/BMAD in product repo memory |
| **Outputs** | Approved specifications, epics, stories with Given/When/Then acceptance criteria. JIRA tickets created. Confluence spec pages created. |
| **Next Command** | `/arch` |

### /arch

| Field | Value |
|---|---|
| **Command** | `/arch` |
| **Phase** | 4 |
| **Scope** | Product repo |
| **Purpose** | Architect agent designs system architecture, API contracts, DB schema, infrastructure plan |
| **Temporal Workflow** | `FeatureDevelopmentWorkflow` (design + architecture stages) |
| **Inputs** | Approved specifications |
| **Outputs** | Architecture document, API contracts (created in product repo), DB schema, ADRs, tech stack decisions, infrastructure plan, security architecture |
| **Next Command** | `/implement` |

### /implement

| Field | Value |
|---|---|
| **Command** | `/implement` |
| **Phase** | 5 |
| **Scope** | Product repo |
| **Purpose** | Start feature development workflow. Agents execute the 10-stage implementation process. |
| **Temporal Workflow** | `FeatureDevelopmentWorkflow` (all 10 stages) |
| **Inputs** | Feature/story from backlog (ticket ID or auto-pick next) |
| **Outputs** | Implemented feature: code, tests, documentation, PR created |
| **Next Command** | `/check` |

### /check

| Field | Value |
|---|---|
| **Command** | `/check` |
| **Phase** | 6 |
| **Scope** | Product repo |
| **Purpose** | Run quality validation: tests, coverage, lint, security scan |
| **Temporal Workflow** | `QAValidationWorkflow` |
| **Inputs** | Implemented code (from `/implement`) |
| **Outputs** | QA report (test results, coverage percentage, lint results, security findings) |
| **Next Command** | `/review` |

### /review

| Field | Value |
|---|---|
| **Command** | `/review` |
| **Phase** | 6 |
| **Scope** | Product repo |
| **Purpose** | Deep code review by reviewer agent |
| **Temporal Workflow** | `MakerCheckerReviewerWorkflow` |
| **Inputs** | Checked code (passed `/check`) |
| **Outputs** | Review report (code quality, security, performance, standards compliance) |
| **Next Command** | `/approve` |

### /approve

| Field | Value |
|---|---|
| **Command** | `/approve` |
| **Phase** | 6 |
| **Scope** | Product repo |
| **Purpose** | Final authorization gate. Human signal required. |
| **Temporal Workflow** | Approval signal on `MakerCheckerReviewerWorkflow` |
| **Inputs** | Reviewed work (passed `/review`) |
| **Outputs** | Approval or rejection with reason |
| **Next Command** | `/release` (if approved) or `/implement` (if rejected, fix and redo) |

### /release

| Field | Value |
|---|---|
| **Command** | `/release` |
| **Phase** | 7 |
| **Scope** | Product repo |
| **Purpose** | Deploy to production through deployment and release governance |
| **Temporal Workflow** | `DeploymentReadinessWorkflow` + `ReleaseGovernanceWorkflow` |
| **Inputs** | `--version X.Y.Z` or `--rollback vX.Y.Z` |
| **Outputs** | Deployed application, release notes, changelog, git tag, Confluence release page |
| **Next Command** | `/monitor` |

### /monitor

| Field | Value |
|---|---|
| **Command** | `/monitor` |
| **Phase** | 8 |
| **Scope** | Product repo |
| **Purpose** | Post-release health check. Queries Temporal, Postgres, Prometheus, Grafana, Sentry. |
| **Temporal Workflow** | `HealthCheckWorkflow` |
| **Inputs** | Deployed application |
| **Outputs** | Health report: error rate, latency, workflow status, integration health, alerts |
| **Next Command** | `/optimize` (if issues found) |

### /optimize

| Field | Value |
|---|---|
| **Command** | `/optimize` |
| **Phase** | 8 |
| **Scope** | Product repo |
| **Purpose** | Analyze monitoring data and create optimization tickets for the next iteration |
| **Temporal Workflow** | `OptimizationWorkflow` |
| **Inputs** | Monitoring data, performance metrics |
| **Outputs** | Optimization tickets in JIRA, fed back into `/implement` cycle |
| **Next Command** | `/implement` (new cycle) |

---

## Recovery Commands

### /resume

| Field | Value |
|---|---|
| **Command** | `/resume` |
| **Phase** | Any |
| **Scope** | Product repo |
| **Purpose** | Resume interrupted work from last Temporal checkpoint |
| **When to Use** | IDE crash, context overflow, network failure |
| **Temporal** | Queries Temporal for last workflow state, resumes from checkpoint |
| **Inputs** | None (auto-detects last workflow) |
| **Outputs** | Resumed workflow continues from where it stopped |

### /recover-ticket

| Field | Value |
|---|---|
| **Command** | `/recover-ticket` |
| **Phase** | Any |
| **Scope** | Product repo |
| **Purpose** | Recover a specific failed ticket workflow |
| **When to Use** | A single ticket's workflow failed |
| **Temporal** | Finds the failed workflow for the ticket, analyzes failure, retries or creates new workflow |
| **Inputs** | Ticket ID (e.g., `--ticket HTP-13`) |
| **Outputs** | Recovered workflow |

### /recover-workflow

| Field | Value |
|---|---|
| **Command** | `/recover-workflow` |
| **Phase** | Any |
| **Scope** | Product repo |
| **Purpose** | Recover an entire failed workflow |
| **When to Use** | Workflow-level failure (not just a single ticket) |
| **Temporal** | Finds the failed workflow, analyzes failure reason, retries from last successful activity |
| **Inputs** | Workflow ID (e.g., `--workflow-id deploy-healthtracker-1.0.0`) |
| **Outputs** | Recovered workflow |

---

## UI/Design Commands

### /design-system-init

| Field | Value |
|---|---|
| **Command** | `/design-system-init` |
| **Phase** | 1 (during bootstrap) |
| **Scope** | Factory repo (standards) + Product repo (implementation) |
| **Purpose** | Initialize design system: tokens in factory, packages/ui with Storybook in product repo |
| **Temporal Workflow** | `initialize_design_system` activity |
| **Inputs** | None (uses factory defaults) or `--regenerate-tokens` to refresh |
| **Outputs** | `.claude/design-system/` in factory, `packages/ui/` in product repo |

### /component-create

| Field | Value |
|---|---|
| **Command** | `/component-create` |
| **Phase** | 5 (during implementation) |
| **Scope** | Product repo |
| **Purpose** | Create a new shared UI component with design, implementation, tests, and stories |
| **Temporal Workflow** | `ComponentCreateWorkflow` |
| **Inputs** | `--name ComponentName --module module-name` |
| **Outputs** | Component in `packages/ui/src/components/`, stories, tests, registry entry |
| **Next Command** | `/component-review` |

### /component-review

| Field | Value |
|---|---|
| **Command** | `/component-review` |
| **Phase** | 5-6 |
| **Scope** | Product repo |
| **Purpose** | Review component through governance chain (maker -> checker -> reviewer -> approver as Temporal child workflow) |
| **Temporal Workflow** | Governance child workflow |
| **Inputs** | `--name ComponentName` |
| **Outputs** | Review report, approval/rejection |

### /story-create

| Field | Value |
|---|---|
| **Command** | `/story-create` |
| **Phase** | 5 |
| **Scope** | Product repo |
| **Purpose** | Create Storybook stories for a component |
| **Temporal Workflow** | Activity within `ComponentCreateWorkflow` |
| **Inputs** | `--component ComponentName` |
| **Outputs** | `.stories.tsx` file with all required story variants |

### /story-validate

| Field | Value |
|---|---|
| **Command** | `/story-validate` |
| **Phase** | 5-6 |
| **Scope** | Product repo |
| **Purpose** | Validate all Storybook stories render correctly and pass accessibility checks |
| **Temporal Workflow** | Activity within `UIAuditWorkflow` |
| **Inputs** | None (validates all stories) or `--component ComponentName` |
| **Outputs** | Validation report per story |

### /ui-audit

| Field | Value |
|---|---|
| **Command** | `/ui-audit` |
| **Phase** | Any |
| **Scope** | Product repo |
| **Purpose** | Audit entire UI for design system compliance, accessibility (WCAG 2.1 AA), token usage |
| **Temporal Workflow** | `UIAuditWorkflow` |
| **Inputs** | None |
| **Outputs** | Audit report with pass/fail per component, overall compliance score |

---

## Interaction Modes

Every workflow step supports 4 user interaction modes. The user can switch modes at any time via the UI or by sending a Temporal signal. The current mode is stored in the Brain conversations table.

| Mode | Purpose | When to Use |
|---|---|---|
| **chat** | Discuss, ask questions, clarify requirements | When you need information or have questions about the current step |
| **brainstorm** | Explore ideas, challenge assumptions, generate alternatives | During `/vision-to-prd`, `/arch`, or any creative/exploratory phase |
| **plan** | Structure approach, define steps, set priorities | During `/spec`, `/arch`, or when organizing work for `/implement` |
| **implement** | Execute, write code, generate artifacts | During `/implement`, `/check`, `/release` -- action-oriented steps |

Mode switching is available on all product commands (`/vision-to-prd`, `/spec`, `/arch`, `/implement`, `/check`, `/review`, `/release`, `/monitor`, `/optimize`). The factory commands (`/factory-init`, `/bootstrap-product`) default to **implement** mode.

## Brain Integration

All commands that involve agent execution read from and write to the Brain (`/api/v1/brain/`):

- **Before execution**: Agent loads relevant memories, decisions, and patterns from Brain
- **During execution**: Conversation history is written to Brain conversations table
- **After execution**: Learnings, new patterns, and decisions are persisted to Brain

Brain data is scoped (factory/product/session) and categorized. Use `GET /api/v1/brain/memory`, `/brain/decisions`, `/brain/patterns`, or `/brain/conversations` to inspect Brain state directly.

---

## Integration Gate (7 Required Systems)

All 7 must be validated during `/factory-init`:

| # | System | Purpose | Validated By |
|---|---|---|---|
| 1 | GitHub | Source control, PRs, CI/CD | API token test |
| 2 | JIRA | Ticket management, sprint tracking | API connection test |
| 3 | Confluence | Documentation hub | API connection test |
| 4 | Temporal | Workflow engine | gRPC connection test |
| 5 | Postgres | System of record | Connection + schema test |
| 6 | FastAPI | Backend API layer | Health endpoint test |
| 7 | Claude | AI agent execution | API key validation |
