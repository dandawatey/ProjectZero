# 15 - Example: New Product Flow -- HealthTracker Pro

## Scenario

A healthcare startup wants to build **HealthTracker Pro**, a patient monitoring SaaS platform. The system allows healthcare providers to monitor patients' vital signs remotely, receive alerts for anomalies, and manage care plans. The team is using ProjectZeroFactory to build it from scratch.

**Team**: 1 product owner (human), Claude agents (the factory)
**Stack**: Next.js (frontend), FastAPI (backend), PostgreSQL (database)
**Integrations**: JIRA, Confluence, GitHub (all configured)

---

## Step 1: Clone and Initialize

### Actions

```bash
git clone https://github.com/acme-health/ProjectZeroFactory.git HealthTrackerPro
cd HealthTrackerPro
```

Open Claude Code in the directory.

```
/factory-init
```

### Factory Output

```
Validating factory structure...
  .claude/agents/          OK
  .claude/commands/        OK
  .claude/skills/          OK (17 skills found)
  .claude/workflows/       OK
  .claude/contracts/       OK
  .claude/core/            OK
  .claude/delivery/        OK
  .claude/memory/          OK
  .claude/recovery/        OK

Initializing stores...
  Memory store:   INITIALIZED
  Recovery store: INITIALIZED
  Learning store: INITIALIZED
  Queue:          INITIALIZED

Factory version: 1.0.0
Status: READY for /bootstrap-product
```

---

## Step 2: Bootstrap the Product

### Actions

```
/bootstrap-product --name "HealthTracker Pro" --type saas --stack "nextjs,fastapi,postgresql"
```

### Factory Output

```
Bootstrapping product: HealthTracker Pro
Type: SaaS
Stack: Next.js, FastAPI, PostgreSQL

Creating project structure...
  src/
    api/                   FastAPI application
    web/                   Next.js application
    shared/                Shared types and utilities
  packages/
    ui/                    Design system and component library
  tests/
    unit/
    integration/
    e2e/

Initializing package managers...
  package.json             CREATED (Next.js + Storybook)
  pyproject.toml           CREATED (FastAPI + pytest)

Configuring agents...
  product-manager          ENABLED
  architect                ENABLED
  backend-engineer         ENABLED (FastAPI)
  frontend-engineer        ENABLED (Next.js)
  qa-engineer              ENABLED
  security-reviewer        ENABLED
  ux-reviewer              ENABLED
  sre-engineer             ENABLED
  devops-engineer          ENABLED
  data-engineer            SKIPPED (no data pipeline stack)
  finops-analyst           ENABLED

Design system: INITIALIZED (default tokens)
Git: Initial commit created

Status: READY for integration configuration
```

---

## Step 3: Configure JIRA

### Actions

Edit `.env`:
```env
JIRA_BASE_URL=https://acme-health.atlassian.net
JIRA_API_TOKEN=ATATT3xFfGF0...
JIRA_USER_EMAIL=cto@acme-health.com
JIRA_PROJECT_KEY=HTP
JIRA_BOARD_ID=42
```

```
/setup jira
```

### Factory Output

```
Testing JIRA connection...
  Base URL:     https://acme-health.atlassian.net   OK
  Auth:         cto@acme-health.com                 OK
  Project:      HTP (HealthTracker Pro)             OK
  Board:        42 (Sprint Board)                   OK

Syncing board state...
  Current sprint: None (new project)
  Backlog: Empty

JIRA integration: CONNECTED
```

---

## Step 4: Configure Confluence

### Actions

```env
CONFLUENCE_BASE_URL=https://acme-health.atlassian.net/wiki
CONFLUENCE_API_TOKEN=ATATT3xFfGF0...
CONFLUENCE_SPACE_KEY=HTP
```

```
/setup confluence
```

### Factory Output

```
Testing Confluence connection...
  Base URL:     https://acme-health.atlassian.net/wiki   OK
  Space:        HTP                                      OK

Creating project hub...
  HealthTracker Pro Hub        CREATED (page ID: 12345)
    Overview                   CREATED
    Architecture               CREATED
    Modules                    CREATED
    Sprints                    CREATED
    Risks                      CREATED
    Decisions                  CREATED
    Releases                   CREATED

Confluence integration: CONNECTED
Project hub URL: https://acme-health.atlassian.net/wiki/spaces/HTP/pages/12345
```

---

## Step 5: Configure GitHub

### Actions

```env
GITHUB_TOKEN=ghp_abc123...
GITHUB_ORG=acme-health
GITHUB_DEFAULT_BRANCH=main
```

```
/setup github
```

### Factory Output

```
Testing GitHub connection...
  Org:          acme-health                         OK
  Repo:         healthtracker-pro                   OK
  Branch:       main                                OK

Configuring repository...
  Branch protection: CONFIGURED (require PR, require checks)
  PR template:       CREATED
  CI pipeline:       GitHub Actions workflow created

GitHub integration: CONNECTED
```

---

## Step 6: Create the BMAD

### Actions

```
/spec --type bmad
```

### Factory Output (Interactive)

The product-manager agent conducts a structured interview:

```
Product Manager: Let's define the Business Model Architecture Document for HealthTracker Pro.

1. BUSINESS CONTEXT
   What problem does HealthTracker Pro solve?

User: Healthcare providers need to monitor patients with chronic conditions
remotely. Currently they rely on patients self-reporting, which leads to
missed critical events. We enable continuous remote monitoring with
automated alerting.

Product Manager: Understood. Who are the target users?

User: Two primary personas:
- Dr. Sarah (Cardiologist): Monitors 200+ patients, needs dashboard to
  see all patients at a glance, get alerts for anomalies
- Nurse Mike (Care Coordinator): Manages daily patient interactions,
  needs to see care plans, update vitals, communicate with patients

Product Manager: What is the revenue model?

User: B2B SaaS. Per-provider seat pricing. $99/month per provider.
Enterprise tier at $499/month with API access and custom integrations.

Product Manager: What are the key technical constraints?

User: HIPAA compliance is mandatory. Data must be encrypted at rest
and in transit. Audit logging required. US-only data residency.
99.9% uptime SLO.

Product Manager: What are the success metrics?

User: 
- 100 provider accounts in first 6 months
- Average alert-to-acknowledgment time under 5 minutes
- Patient readmission rate reduction of 15%
- NPS score above 50
```

After the interview completes:

```
BMAD document created: .claude/knowledge/bmad.md

Sections:
  Business Context:            COMPLETE
  Target Users (2 personas):   COMPLETE
  Value Proposition:           COMPLETE
  Revenue Model:               COMPLETE
  Competitive Landscape:       COMPLETE
  Technical Constraints:       COMPLETE (HIPAA, encryption, audit, US data residency)
  Non-Functional Requirements: COMPLETE (99.9% uptime, HIPAA)
  Success Metrics:             COMPLETE (4 KPIs with targets)
  Risk Assessment:             COMPLETE (8 risks identified)

BMAD validation: PASSED
```

---

## Step 7: Validate Readiness

### Actions

```
/setup validate
```

### Factory Output

```
Running readiness validation...

  Required:
    .claude/ structure intact       PASS
    .env configured                 PASS
    Product name set                PASS (HealthTracker Pro)
    Stack defined                   PASS (nextjs, fastapi, postgresql)
    BMAD loaded                     PASS
    Memory store accessible         PASS
    Recovery store accessible       PASS

  Optional:
    JIRA connected                  PASS
    Confluence connected            PASS
    GitHub connected                PASS
    Design system initialized       PASS

Readiness: ALL CHECKS PASSED (7 required, 4 optional)
Status: READY to begin /spec
```

---

## Step 8: Run Specification

### Actions

```
/spec
```

### Factory Output

```
Starting Specification stage...

Loading BMAD: .claude/knowledge/bmad.md

Decomposing into modules (bounded contexts)...

Module 1: patient-management
  Responsibility: Patient profiles, demographics, medical history
  Entities: Patient, MedicalHistory, Insurance
  
Module 2: vital-signs
  Responsibility: Vital sign data ingestion, storage, querying
  Entities: VitalSign, DeviceReading, AlertThreshold
  
Module 3: alerting
  Responsibility: Anomaly detection, alert generation, notification delivery
  Entities: Alert, AlertRule, NotificationPreference
  
Module 4: care-plans
  Responsibility: Care plan creation, assignment, progress tracking
  Entities: CarePlan, CareTask, CarePlanAssignment
  
Module 5: provider-dashboard
  Responsibility: Provider-facing UI, patient overview, analytics
  Entities: DashboardConfig, SavedView
  
Module 6: auth-and-compliance
  Responsibility: Authentication, authorization, HIPAA audit logging
  Entities: User, Role, AuditLog, Session

Creating epics...
  HTP-1: Patient Management (6 stories)
  HTP-2: Vital Signs Monitoring (8 stories)
  HTP-3: Alerting System (7 stories)
  HTP-4: Care Plan Management (5 stories)
  HTP-5: Provider Dashboard (9 stories)
  HTP-6: Auth & HIPAA Compliance (8 stories)

Total: 6 epics, 43 stories

Creating JIRA epics and stories... 43 issues created
Creating Confluence specification pages... 6 module pages created

Defining API contracts...
  patient-management <-> vital-signs          DEFINED
  vital-signs <-> alerting                    DEFINED
  alerting <-> provider-dashboard             DEFINED
  care-plans <-> patient-management           DEFINED
  auth-and-compliance <-> all modules         DEFINED

Running checker on specification...
  Completeness:     PASS (all modules have specs)
  Consistency:      PASS (no contradictions)
  Acceptance criteria: PASS (all 43 stories have Given/When/Then)
  Contracts:        PASS (all inter-module contracts defined)

Running approver...
  Specification: APPROVED

Checkpoint saved: cp-20260122-001 (specification-complete)

Specification stage COMPLETE.
Ready for /arch
```

---

## Step 9: Run Architecture

### Actions

```
/arch
```

### Factory Output

```
Starting Architecture stage...

Loading specifications for 6 modules...

--- Design Sub-Stage ---

Data models:
  patient-management:  5 entities, 12 relationships    DESIGNED
  vital-signs:         4 entities, 8 relationships      DESIGNED
  alerting:            3 entities, 6 relationships       DESIGNED
  care-plans:          3 entities, 5 relationships       DESIGNED
  provider-dashboard:  2 entities, 3 relationships       DESIGNED
  auth-and-compliance: 4 entities, 7 relationships       DESIGNED

Pseudocode:
  Anomaly detection algorithm    WRITTEN (vital-signs module)
  Alert escalation logic         WRITTEN (alerting module)
  HIPAA audit trail generation   WRITTEN (auth-and-compliance module)
  Role-based access control      WRITTEN (auth-and-compliance module)

UI flows:
  Provider dashboard flow        DESIGNED (5 screens, 3 user flows)
  Patient management flow        DESIGNED (4 screens, 2 user flows)
  Care plan management flow      DESIGNED (3 screens, 2 user flows)
  Alert management flow          DESIGNED (3 screens, 2 user flows)

Test plans:
  43 stories -> 43 test plans    CREATED

--- Architecture Sub-Stage ---

Architecture Decision Records:
  ADR-001: Use PostgreSQL with row-level security for multi-tenant isolation
  ADR-002: Use JWT with refresh tokens for authentication
  ADR-003: Use WebSockets for real-time vital sign updates
  ADR-004: Use Redis pub/sub for alert distribution
  ADR-005: Use AES-256 encryption for PHI at rest
  ADR-006: Use OpenTelemetry for distributed tracing
  ADR-007: Use Next.js App Router with server components

Infrastructure requirements:
  Compute: 2 API servers (2 vCPU, 4GB each), 1 WebSocket server
  Database: PostgreSQL 16 (RDS, db.r6g.large, encrypted)
  Cache: Redis 7 (ElastiCache, cache.r6g.large)
  Storage: S3 for document uploads (encrypted, versioned)
  CDN: CloudFront for static assets
  Estimated monthly cost: $850-1200

Security architecture:
  Authentication: JWT + refresh tokens (ADR-002)
  Authorization: RBAC with row-level security (ADR-001)
  Encryption: AES-256 at rest, TLS 1.3 in transit (ADR-005)
  Audit: Every data access logged (HIPAA requirement)
  Secret management: AWS Secrets Manager
  OWASP Top 10: Mitigation plan for all 10 categories

Security review: PASSED (no critical findings)
FinOps estimate: $850-1200/month (within budget)

Running checker on architecture...  PASS
Running approver...                 APPROVED

Checkpoint saved: cp-20260122-002 (architecture-complete)

Architecture stage COMPLETE.
Ready for /implement
```

---

## Step 10: Begin Implementation

### Actions

```
/implement HTP-7
```

(HTP-7: "As a provider, I can log in with email and password so that I can access the dashboard")

### Factory Output

```
Starting implementation: HTP-7

Loading context...
  Module: auth-and-compliance
  Architecture: ADR-002 (JWT authentication)
  Data model: User, Role, Session
  Test plan: 8 unit tests, 3 integration tests, 1 E2E test

Creating branch: feature/HTP-7-provider-login

--- TDD Phase ---

Writing tests first...
  tests/unit/test_auth_service.py          8 tests (all RED)
  tests/integration/test_auth_api.py       3 tests (all RED)
  tests/e2e/test_login_flow.py             1 test (RED)

--- Implementation Phase ---

Implementing code...
  src/api/routes/auth.py                   Login endpoint (POST /api/auth/login)
  src/api/services/auth_service.py         Auth logic (validate credentials, issue JWT)
  src/api/repositories/user_repository.py  User data access (with RLS)
  src/api/models/user.py                   User and Session models
  src/api/middleware/auth.py               JWT validation middleware
  src/web/app/login/page.tsx               Login page component
  src/web/components/LoginForm.tsx         Login form (uses design system)
  packages/ui/src/components/Form/         Form components (shared)

Running tests...
  Unit tests:        8/8 PASSING (GREEN)
  Integration tests: 3/3 PASSING (GREEN)
  E2E tests:         1/1 PASSING (GREEN)
  Coverage:          92%

--- Governance Chain ---

Checker:
  Spec compliance:     PASS (all acceptance criteria met)
  Test existence:      PASS (12 tests)
  Coverage threshold:  PASS (92% > 80%)
  Contract compliance: PASS

Reviewer:
  Code quality:        APPROVE (clean, well-structured)
  Security:            APPROVE (bcrypt hashing, parameterized queries, JWT properly signed)
  Performance:         APPROVE (indexed queries, connection pooling)
  Standards:           APPROVE (naming conventions, file organization)

Approver:
  Governance chain:    COMPLETE
  Result:              APPROVED

Creating PR: feature/HTP-7-provider-login -> main
  PR #1 created: https://github.com/acme-health/healthtracker-pro/pull/1

Updating JIRA: HTP-7 -> Done
Updating Confluence: Auth module page updated

Checkpoint saved: cp-20260122-003 (story-HTP-7-complete)

Implementation of HTP-7 COMPLETE.
Next in queue: HTP-8 (Provider registration)
```

---

## What Happens Next

The team continues running `/implement` for each story. The factory:

1. Implements stories in module order (auth first, then patient management, then vital signs, etc.)
2. Creates a branch, writes tests, implements code, passes governance for each story
3. Creates PRs that are merged after approval
4. Updates JIRA and Confluence automatically
5. Saves checkpoints after each story
6. Captures learnings as patterns emerge

When all 43 stories are complete and all 6 module gates pass:

```
/release --version 1.0.0
```

The factory deploys to staging, runs smoke tests, deploys to production, activates monitoring, and publishes release notes.

---

## Timeline Estimate

| Stage | Duration | Output |
|---|---|---|
| Setup (Steps 1-7) | 1-2 hours | Factory initialized, integrations configured, BMAD created |
| Specification (Step 8) | 2-4 hours | 6 modules, 43 stories, all contracts defined |
| Architecture (Step 9) | 2-3 hours | Data models, ADRs, infrastructure plan, security architecture |
| Realization (Step 10+) | 40-80 hours | 43 stories implemented with TDD and governance |
| Completion | 4-8 hours | Staged deployment, monitoring, release notes |

**Total**: Approximately 50-100 hours of Claude agent time, spread across multiple sessions with full recovery support.

---

## Key Observations

1. **The factory never starts coding without a BMAD**. The business context drives everything.
2. **Every story follows TDD**. Tests are written before implementation code.
3. **Every artifact passes through the governance chain**. No exceptions.
4. **HIPAA compliance is embedded in the architecture**, not bolted on. ADRs explicitly address encryption, audit logging, and access control.
5. **Recovery checkpoints are saved after every story**. If a session ends, no work is lost.
6. **JIRA and Confluence are updated automatically**. The team always has current documentation.
7. **The design system is used from the first UI component**. No ad-hoc styling.
