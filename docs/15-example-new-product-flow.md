# 15 - Example: New Product Flow -- HealthTracker Pro

## Scenario

A healthcare startup wants to build **HealthTracker Pro**, a patient monitoring SaaS platform. The system allows healthcare providers to monitor patients' vital signs remotely, receive alerts for anomalies, and manage care plans.

**Team**: 1 product owner (human), Claude agents (the factory)
**Stack**: React (frontend), FastAPI (backend), PostgreSQL (database)
**Architecture**: React -> FastAPI -> Postgres -> Temporal -> Agents
**Integrations**: GitHub, JIRA, Confluence, Temporal, Postgres, FastAPI, Claude (all 7)

---

## Step 1: Clone Factory and Run Guided Setup

### Actions

```bash
git clone https://github.com/acme-health/ProjectZeroFactory.git
cd ProjectZeroFactory
```

Run the guided setup script. This walks you through configuring all 7 required integrations:

```bash
./guided-setup.sh
```

The script prompts for:
- GitHub token and org
- JIRA base URL, token, email
- Confluence base URL, token, space key
- Postgres connection string
- Temporal server address
- Claude API key

It writes everything to `.env` and validates each connection as you go.

```
[1/7] GitHub...
  Token: ghp_***
  Org: acme-health
  Connection: OK

[2/7] JIRA...
  URL: https://acme-health.atlassian.net
  Token: ATATT***
  Email: cto@acme-health.com
  Connection: OK

[3/7] Confluence...
  URL: https://acme-health.atlassian.net/wiki
  Token: ATATT***
  Connection: OK

[4/7] Postgres...
  URL: postgresql://pzero:***@localhost:5432/projectzero
  Connection: OK
  Schema: MIGRATED

[5/7] Temporal...
  Address: localhost:7233
  Connection: OK
  UI: http://localhost:8233

[6/7] FastAPI...
  URL: http://localhost:8000
  Health: OK

[7/7] Claude...
  API Key: sk-ant-***
  Connection: OK

All 7 integrations configured. Ready for /factory-init.
```

---

## Step 2: /factory-init (Phase 0)

Open Claude Code in the factory directory.

```
/factory-init
```

This starts `FactoryInitWorkflow` in Temporal.

**Temporal Workflow ID**: `factory-init-20260410-001`

```
Validating factory structure...
  .claude/agents/          OK (12 agents)
  .claude/commands/        OK (22 commands)
  .claude/skills/          OK (17 skills)
  .claude/workflows/       OK
  .claude/contracts/       OK
  .claude/core/            OK
  .claude/design-system/   OK

Validating 7 required integrations...
  [1/7] GitHub          CONNECTED  (acme-health org, 3 repos)
  [2/7] JIRA            CONNECTED  (acme-health.atlassian.net)
  [3/7] Confluence       CONNECTED  (acme-health.atlassian.net/wiki)
  [4/7] Temporal         CONNECTED  (localhost:7233, UI at :8233)
  [5/7] Postgres         CONNECTED  (projectzero db, schema v1.2)
  [6/7] FastAPI          CONNECTED  (localhost:8000, healthy)
  [7/7] Claude           CONNECTED  (API key valid)

Integration gate: 7/7 PASSED

Factory version: 2.0.0
Status: READY for /bootstrap-product
```

---

## Step 3: /bootstrap-product (Phase 1)

```
/bootstrap-product --name "HealthTracker Pro" --type saas --stack "react,fastapi,postgresql"
```

**Temporal Workflow ID**: `bootstrap-healthtracker-pro-20260410-001`

This workflow creates everything the product needs across all 7 integrations:

```
Bootstrapping product: HealthTracker Pro

[GitHub] Creating repository...
  Repo: acme-health/healthtracker-pro       CREATED (via GitHub API)
  Branch protection: main                    CONFIGURED
  PR template:                               CREATED
  CI workflow:                               CREATED

[JIRA] Creating project...
  Project key: PZ                            CREATED
  Board: PZ Sprint Board                     CREATED (board ID: 87)
  Issue types: Epic, Story, Task, Bug        CONFIGURED

[Confluence] Creating space...
  Space key: PZ                              CREATED
  Hub page: HealthTracker Pro Hub            CREATED (page ID: 98001)
    /Overview                                CREATED
    /Architecture                            CREATED
    /Modules                                 CREATED
    /Sprints                                 CREATED
    /Risks                                   CREATED
    /Decisions                               CREATED
    /Releases                                CREATED

[Product Repo] Initializing structure...
  src/api/                                   FastAPI application
  src/web/                                   React application
  src/shared/                                Shared types and utilities
  src/design-system/                         Design system (auto-initialized)
  .claude/                                   Agent OS initialized

[Design System] Initializing (Step 10/13)...
  Installing framer-motion, clsx, cva       DONE
  Installing Storybook                       DONE
  src/design-system/tokens.ts               CREATED (colors, typography, spacing, radii, shadows, z-index, breakpoints)
  src/design-system/motion.ts               CREATED (fadeIn, fadeUp, scaleIn, stagger, drawerSlide, buttonTap, cardHover)
  src/design-system/components/Button/      CREATED (+ Button.stories.tsx)
  src/design-system/components/Input/       CREATED (+ Input.stories.tsx)
  src/design-system/components/Card/        CREATED (+ Card.stories.tsx)
  src/design-system/components/Badge/       CREATED (+ Badge.stories.tsx)
  src/design-system/components/Spinner/     CREATED (+ Spinner.stories.tsx)
  src/design-system/components/Avatar/      CREATED (+ Avatar.stories.tsx)
  .storybook/main.ts                        CREATED
  .storybook/preview.tsx                    CREATED

[Postgres] Registering product...
  Product record:                            CREATED (id: prod_htp_001)
  Phase: 1 (bootstrap)                       SET

[Temporal] Product namespace...
  Namespace: healthtracker-pro               REGISTERED

Status: READY for /vision-to-prd
Confluence hub: https://acme-health.atlassian.net/wiki/spaces/PZ/pages/98001
GitHub repo: https://github.com/acme-health/healthtracker-pro
JIRA project: https://acme-health.atlassian.net/jira/software/projects/PZ
```

---

## Step 4: /vision-to-prd (Phase 2a)

The user has a vision but no PRD. The system asks questions and generates one.

```
/vision-to-prd
```

**Temporal Workflow ID**: `vision-to-prd-healthtracker-20260410-001`

The PM agent conducts a structured interview:

```
Product Manager: Describe your product vision.

User: Healthcare providers need to monitor patients with chronic conditions
remotely. Currently they rely on patients self-reporting, which leads to
missed critical events. We want continuous remote monitoring with automated
alerting. Two personas: cardiologists managing 200+ patients who need a
dashboard, and care coordinators who manage daily interactions. B2B SaaS,
$99/seat/month, enterprise tier at $499. HIPAA mandatory.

Product Manager: What are the success metrics?

User: 100 provider accounts in 6 months. Alert-to-acknowledgment under
5 minutes. Patient readmission rate down 15%. NPS above 50.

Product Manager: Technical constraints?

User: HIPAA compliance. Encrypted at rest and in transit. Audit logging.
US-only data residency. 99.9% uptime SLO.
```

After the interview:

```
PRD generated: .claude/knowledge/prd.md
BMAD generated: .claude/knowledge/bmad.md

Sections completed:
  Business Context:            COMPLETE
  Target Users (2 personas):   COMPLETE
  Value Proposition:           COMPLETE
  Revenue Model:               COMPLETE ($99/seat, $499 enterprise)
  Technical Constraints:       COMPLETE (HIPAA, encryption, audit, US residency)
  Non-Functional Requirements: COMPLETE (99.9% uptime)
  Success Metrics:             COMPLETE (4 KPIs)
  Risk Assessment:             COMPLETE (8 risks identified)

[Confluence] Updated: PZ Hub / Overview      page ID: 98002
[Postgres] Product phase: 2a (vision)        UPDATED

Status: READY for /business-docs --phase discovery
```

---

## Step 5: /business-docs --phase discovery (Phase 2b)

```
/business-docs --phase discovery
```

**Temporal Workflow ID**: `business-docs-discovery-healthtracker-20260410-001`

```
Generating discovery-phase business documents...

TAM-SAM-SOM Analysis:
  TAM: $2.3B (global remote patient monitoring market)
  SAM: $680M (US cardiology + chronic care)
  SOM: $12M (target segment, first 2 years)

Competitive Analysis:
  Direct competitors: 4 identified
    - BioTelemetry (enterprise, $200+/seat)
    - Philips RPM (hardware-bundled)
    - Current Health (hospital-focused)
    - Vivify Health (care management)
  Differentiator: AI-powered anomaly detection, simpler UX, lower price point

Team Composition Plan:
  Phase 1 (MVP): 1 PO + factory agents
  Phase 2 (Scale): +2 engineers, +1 designer, +1 compliance officer
  Phase 3 (Growth): +sales team, +customer success

Business Model Canvas:                       GENERATED

[Confluence] Created: PZ Hub / Business       page ID: 98010
  /TAM-SAM-SOM                               page ID: 98011
  /Competitive Analysis                      page ID: 98012
  /Team Plan                                 page ID: 98013
  /Business Model                            page ID: 98014

[Postgres] Product phase: 2b (discovery)     UPDATED

Status: READY for /spec
```

---

## Step 6: /spec (Phase 3)

```
/spec
```

**Temporal Workflow ID**: `spec-healthtracker-20260410-001`

```
Starting specification stage...

Loading PRD: .claude/knowledge/prd.md
Loading BMAD: .claude/knowledge/bmad.md

Decomposing into modules (bounded contexts)...

  Module 1: patient-management
    Responsibility: Patient profiles, demographics, medical history
  Module 2: vital-signs
    Responsibility: Vital sign ingestion, storage, querying
  Module 3: alerting
    Responsibility: Anomaly detection, alert generation, notifications
  Module 4: care-plans
    Responsibility: Care plan creation, assignment, progress tracking
  Module 5: provider-dashboard
    Responsibility: Provider-facing UI, patient overview, analytics
  Module 6: auth-and-compliance
    Responsibility: Authentication, authorization, HIPAA audit logging

Total: 6 modules, 34 stories

[JIRA] Creating epics and stories...
  PZ-1: Patient Management (5 stories)       CREATED
    PZ-7: Provider can add a patient          CREATED
    PZ-8: Provider can view patient profile   CREATED
    PZ-9: Provider can update patient info    CREATED
    PZ-10: Provider can search patients       CREATED
    PZ-11: Provider can view medical history  CREATED
  PZ-2: Vital Signs Monitoring (6 stories)   CREATED
    PZ-12 through PZ-17                      CREATED
  PZ-3: Alerting System (6 stories)          CREATED
    PZ-18 through PZ-23                      CREATED
  PZ-4: Care Plan Management (5 stories)     CREATED
    PZ-24 through PZ-28                      CREATED
  PZ-5: Provider Dashboard (7 stories)       CREATED
    PZ-29 through PZ-35                      CREATED
  PZ-6: Auth & HIPAA Compliance (5 stories)  CREATED
    PZ-36 through PZ-40                      CREATED

  Total JIRA issues: 6 epics + 34 stories = 40 issues

[Confluence] Creating specification pages...
  PZ Hub / Modules / patient-management      page ID: 98020
  PZ Hub / Modules / vital-signs             page ID: 98021
  PZ Hub / Modules / alerting                page ID: 98022
  PZ Hub / Modules / care-plans              page ID: 98023
  PZ Hub / Modules / provider-dashboard      page ID: 98024
  PZ Hub / Modules / auth-and-compliance     page ID: 98025

API contracts defined:
  patient-management <-> vital-signs         DEFINED
  vital-signs <-> alerting                   DEFINED
  alerting <-> provider-dashboard            DEFINED
  care-plans <-> patient-management          DEFINED
  auth-and-compliance <-> all modules        DEFINED

[Postgres] Product phase: 3 (specification)  UPDATED
[Postgres] 34 story records created          STORED

Governance: checker PASS, approver APPROVED

Status: READY for /arch
```

---

## Step 7: /arch (Phase 4)

```
/arch
```

**Temporal Workflow ID**: `arch-healthtracker-20260410-001`

The user switches to **brainstorm** mode to explore architecture options before committing:

```
[Mode: brainstorm]

User: Should we use WebSockets or SSE for real-time vital signs?

Architect Agent: Let me check Brain for relevant patterns...

  [Brain] Pattern recalled: "WebSocket vs SSE for real-time data"
    Success rate: 87% for WebSockets when bidirectional needed
    Anti-pattern: SSE with high-frequency data (>1 msg/sec) causes connection pooling issues

Architect Agent: Based on patterns in Brain, WebSockets are preferred for
vital signs because we need bidirectional communication (device -> server
and server -> dashboard). SSE would work for alerts (server -> client only)
but not for the vital signs ingestion path.

User: Good. Let's go with WebSockets for vitals, SSE for alerts. Switch to plan mode.

[Mode: plan]

Architect Agent: Structuring the architecture approach:
  1. WebSocket gateway for vital sign ingestion (ADR-003)
  2. SSE for alert push to dashboard
  3. Redis pub/sub as internal message bus (ADR-004)
  4. PostgreSQL with row-level security for data isolation (ADR-001)

User: Proceed. Switch to implement mode.

[Mode: implement]
```

The Brain records this conversation and the decisions made. When later stories reference the alerting module, agents will recall from Brain that SSE was chosen for alerts and WebSockets for vitals.

```
Starting architecture stage...

Loading specifications for 6 modules...

Data models designed:
  patient-management:  5 entities, 12 relationships    DESIGNED
  vital-signs:         4 entities, 8 relationships      DESIGNED
  alerting:            3 entities, 6 relationships       DESIGNED
  care-plans:          3 entities, 5 relationships       DESIGNED
  provider-dashboard:  2 entities, 3 relationships       DESIGNED
  auth-and-compliance: 4 entities, 7 relationships       DESIGNED

Architecture Decision Records:
  ADR-001: PostgreSQL with row-level security for multi-tenant isolation
  ADR-002: JWT with refresh tokens for authentication
  ADR-003: WebSockets for real-time vital sign updates
  ADR-004: Redis pub/sub for alert distribution
  ADR-005: AES-256 encryption for PHI at rest
  ADR-006: OpenTelemetry for distributed tracing (observability strategy)
  ADR-007: React with server components for dashboard
  ADR-008: Structured logging with correlation IDs (every request)
  ADR-009: Prometheus metrics + Grafana dashboards for SLO tracking

[Brain] Decisions stored:
  brain/decisions/ADR-001 through ADR-007        PERSISTED
  Context: problem statement, options, rationale  STORED
  Conversation history (brainstorm session)       STORED

API contracts created in product repo:
  contracts/patient-management.yaml          CREATED
  contracts/vital-signs.yaml                 CREATED
  contracts/alerting.yaml                    CREATED
  contracts/care-plans.yaml                  CREATED
  contracts/auth.yaml                        CREATED

Infrastructure plan:
  Compute: 2 API servers (2 vCPU, 4GB each)
  Database: PostgreSQL 16 (encrypted, RDS)
  Cache: Redis 7 for pub/sub
  Storage: S3 for documents (encrypted)
  Estimated monthly cost: $850-1200

Security architecture:
  Authentication: JWT + refresh tokens (ADR-002)
  Authorization: RBAC + row-level security (ADR-001)
  Encryption: AES-256 at rest, TLS 1.3 in transit
  Audit: Every data access logged (HIPAA)
  OWASP Top 10: Mitigation plan complete

[Confluence] Updated: PZ Hub / Architecture   page ID: 98030
  /ADRs                                       page ID: 98031
  /Infrastructure                             page ID: 98032
  /Security                                   page ID: 98033

[Postgres] Product phase: 4 (architecture)   UPDATED

Governance: checker PASS, approver APPROVED

Status: READY for /implement
```

---

## Step 8: /implement (Phase 5)

```
/implement PZ-36
```

(PZ-36: "As a provider, I can log in with email and password so that I can access the dashboard")

**Temporal Workflow ID**: `feature-PZ-36-20260410-001`

The `FeatureDevelopmentWorkflow` runs all 10 stages:

```
Starting implementation: PZ-36
Module: auth-and-compliance

--- 10-Stage Feature Development Workflow ---

[1/10] Intake: Loading context...
  Module: auth-and-compliance
  Architecture: ADR-002 (JWT authentication)
  Data model: User, Role, Session
  Contracts: contracts/auth.yaml

[2/10] Spec validation: Acceptance criteria verified
  3 Given/When/Then scenarios confirmed

[3/10] Design: UI flow designed
  Login page -> Dashboard redirect

[4/10] Architecture alignment: Verified against ADR-002
  JWT + refresh token flow confirmed

[5/10] TDD - Writing tests first...
  tests/unit/test_auth_service.py          8 tests (RED)
  tests/integration/test_auth_api.py       3 tests (RED)
  tests/e2e/test_login_flow.py             1 test (RED)

[6/10] Implementation...
  src/api/routes/auth.py                   POST /api/auth/login
  src/api/services/auth_service.py         Auth logic
  src/api/models/user.py                   User, Session models
  src/api/middleware/auth.py               JWT middleware
  src/web/pages/login.tsx                  Login page (React)
  src/web/components/LoginForm.tsx         Login form (design system)

[7/10] Tests passing...
  Unit: 8/8 GREEN
  Integration: 3/3 GREEN
  E2E: 1/1 GREEN
  Coverage: 92%

[8/10] Documentation updated
  API docs, module docs refreshed

[9/10] Integration sync
  [GitHub] Branch: feature/PZ-36-provider-login    PUSHED
  [GitHub] PR #1 created                           CREATED
  [JIRA] PZ-36 status: In Review                   UPDATED
  [Confluence] Auth module page                     UPDATED

[10/10] Governance chain (Temporal child workflow)
  Checker: PASS (spec compliance, tests, coverage, contracts)
  Reviewer: APPROVE (code quality, security, performance)
  Approver: APPROVED (waiting for human signal... APPROVED)

[JIRA] PZ-36 status: Done                         UPDATED
[Postgres] Story PZ-36: completed                  STORED

Feature PZ-36 COMPLETE.
Next in queue: PZ-37
```

The team continues with `/implement` for each story. The factory processes stories in dependency order across all 6 modules.

---

## Step 9: /check, /review, /approve (Phase 6)

These run as part of the governance chain within `/implement`. They can also be run standalone:

```
/check PZ-36
```
**Temporal Workflow ID**: `qa-PZ-36-20260410-001`

```
QA Validation:
  Unit tests: 8/8 PASS
  Integration tests: 3/3 PASS
  E2E tests: 1/1 PASS
  Coverage: 92% (threshold: 80%)
  Lint: 0 errors
  Security scan: 0 critical, 0 high
  Result: PASS
```

```
/review PZ-36
```
**Temporal Workflow ID**: `review-PZ-36-20260410-001`

```
Code Review:
  Code quality: APPROVE
  Security: APPROVE (bcrypt, parameterized queries, JWT signed)
  Performance: APPROVE (indexed queries, connection pooling)
  Standards: APPROVE
  Result: APPROVED
```

```
/approve PZ-36
```

Sends approval signal to the Temporal workflow. Human confirms.

---

## Step 10: /release (Phase 7)

After all 34 stories are implemented and approved:

```
/release --version 1.0.0
```

**Temporal Workflow ID (deployment)**: `deploy-healthtracker-1.0.0`
**Temporal Workflow ID (governance)**: `release-gov-healthtracker-1.0.0`

```
DeploymentReadinessWorkflow:
  [1/7] build_check:    PASS (all tests green, coverage 89%)
  [2/7] security_scan:  PASS (0 critical, 0 high)
  [3/7] staging:        DEPLOYED (staging.healthtracker.acme-health.com)
  [4/7] smoke_test:     PASS (12/12 scenarios)
  [5/7] approval:       APPROVED (human signal received)
  [6/7] prod:           DEPLOYED (healthtracker.acme-health.com)
  [7/7] health_check:   PASS (error rate 0%, P95 latency 120ms)

ReleaseGovernanceWorkflow:
  [1/6] changelog:              GENERATED (34 stories)
  [2/6] version_bump:           1.0.0 in package.json + pyproject.toml
  [3/6] validation:             34/34 stories approved, 6/6 module gates passed
  [4/6] stakeholder_approval:   APPROVED
  [5/6] tag:                    v1.0.0 tagged, GitHub release created
  [6/6] notify:                 Confluence release page updated, notifications sent

[JIRA] All stories: Done                     VERIFIED
[Confluence] Release page: v1.0.0            CREATED (page ID: 98050)
[GitHub] Release: v1.0.0                     PUBLISHED
[Postgres] Product phase: 7 (released)       UPDATED

HealthTracker Pro v1.0.0 is LIVE.
```

---

## Step 11: /business-docs --phase planning (Phase 7)

```
/business-docs --phase planning
```

**Temporal Workflow ID**: `business-docs-planning-healthtracker-20260410-001`

```
Generating planning-phase business documents...
(Based on actual built product, real infra costs, real feature set)

Financial Projections:
  Year 1 revenue: $142K (120 seats x $99 x 12 months)
  Year 2 revenue: $890K (projected growth)
  Infrastructure cost: $1,050/month
  Break-even: Month 14

Costing Analysis:
  Infrastructure: $12,600/year
  Team (Phase 2): $480K/year
  Tooling: $24K/year

GTM Strategy:
  Channel 1: Direct sales to cardiology practices
  Channel 2: EHR integration partnerships
  Channel 3: Conference presence (ACC, HIMSS)

Pitch Deck:                                  GENERATED (12 slides)
Data Room:                                   GENERATED (8 documents)

[Confluence] Created: PZ Hub / Business / Planning   page ID: 98060
  /Financial Projections                              page ID: 98061
  /GTM Strategy                                       page ID: 98062
  /Pitch Deck                                         page ID: 98063

[Postgres] Business docs: planning complete          STORED
```

---

## Step 12: /monitor (Phase 8)

```
/monitor
```

**Temporal Workflow ID**: `health-check-healthtracker-20260410-001`

```
HealthTracker Pro v1.0.0 -- Health Report

Temporal:
  Active workflows: 2 (health-check, nightly-backup)
  Failed workflows: 0
  Task queue depth: 0 (all queues empty)

Application:
  Error rate: 0.02%
  P50 latency: 45ms
  P95 latency: 120ms
  P99 latency: 280ms
  Requests/min: 340

Infrastructure:
  CPU: 22%
  Memory: 1.8GB / 4GB (45%)
  Postgres connections: 12 / 100
  Disk: 34%

Integrations:
  GitHub:      HEALTHY (last sync: 2 min ago)
  JIRA:        HEALTHY (last sync: 5 min ago)
  Confluence:  HEALTHY (last sync: 5 min ago)
  Temporal:    HEALTHY (workers: 2, heartbeat: 1s ago)
  Postgres:    HEALTHY (connections: 12/100)
  Sentry:      HEALTHY (0 unresolved errors)

Observability:
  Prometheus:     SCRAPING (47 metrics)
  Grafana:        4 dashboards active
  Sentry:         0 unresolved issues
  OpenTelemetry:  Traces flowing (avg span: 23ms)

Status: ALL HEALTHY
```

---

## Summary: Full Artifact Trail

| Step | Command | Phase | Temporal Workflow ID | JIRA | Confluence | GitHub |
|---|---|---|---|---|---|---|
| 1 | `guided-setup.sh` | - | - | - | - | - |
| 2 | `/factory-init` | 0 | `factory-init-20260410-001` | - | - | - |
| 3 | `/bootstrap-product` | 1 | `bootstrap-healthtracker-pro-20260410-001` | Project PZ created | Space PZ, hub page 98001 | Repo created |
| 4 | `/vision-to-prd` | 2a | `vision-to-prd-healthtracker-20260410-001` | - | Overview updated (98002) | - |
| 5 | `/business-docs --phase discovery` | 2b | `business-docs-discovery-healthtracker-20260410-001` | - | Business pages (98010-98014) | - |
| 6 | `/spec` | 3 | `spec-healthtracker-20260410-001` | 6 epics + 34 stories (PZ-1 to PZ-40) | Module pages (98020-98025) | - |
| 7 | `/arch` | 4 | `arch-healthtracker-20260410-001` | - | Architecture pages (98030-98033) | Contracts committed |
| 8 | `/implement` (x34) | 5 | `feature-PZ-{N}-20260410-*` | Each story -> Done | Module pages updated | 34 PRs merged |
| 9 | `/check` + `/review` + `/approve` | 6 | Governance child workflows | Status updates | - | PR approvals |
| 10 | `/release` | 7 | `deploy-healthtracker-1.0.0` | - | Release page (98050) | v1.0.0 tag + release |
| 11 | `/business-docs --phase planning` | 7 | `business-docs-planning-healthtracker-20260410-001` | - | Planning pages (98060-98063) | - |
| 12 | `/monitor` | 8 | `health-check-healthtracker-20260410-001` | - | - | - |

---

## Key Observations

1. **All work is Temporal workflows**. Every command starts a workflow. Every workflow is visible in the Temporal UI at localhost:8233.
2. **7 integrations validated upfront**. The integration gate at `/factory-init` catches configuration problems before any work begins.
3. **8 phases, strict order**. You cannot skip phases. Each command validates that prerequisites from prior phases are met.
4. **Postgres is the system of record**. Every state change is persisted. Temporal syncs via idempotent activities.
5. **JIRA tickets created automatically**. 6 epics and 34 stories created during `/spec`. Updated automatically as work progresses.
6. **Confluence updated at every step**. Hub page, module pages, architecture pages, release pages -- all created and updated by workflows.
7. **Governance chain on everything**. Every story goes through maker -> checker -> reviewer -> approver as a Temporal child workflow.
8. **Recovery built in**. If anything fails, `/resume`, `/recover-ticket`, or `/recover-workflow` picks up from the last checkpoint.
9. **Business docs tied to reality**. Post-release `/business-docs --phase planning` generates financials based on the actual built product, not projections.
10. **Caveman simple**. Run the commands in order. The factory handles the rest.
11. **Brain remembers everything**. Decisions stored in Brain during `/arch` are recalled during `/implement`. Patterns learned during early stories improve later stories. Conversation history in Brain means `/resume` picks up exactly where you left off.
12. **Interaction modes match your intent**. Brainstorm mode during architecture explores options freely. Plan mode structures the approach. Implement mode executes. Switch anytime.
