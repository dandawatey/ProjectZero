# ProjectZero SaaS — JIRA Ticket Structure

**Status**: Ready for Sprint Planning  
**Date**: 2026-04-19  
**Total Tickets**: 45 (Epics + Stories + Tasks)  
**Effort**: 143 engineer-days (6.5 FTE × 22 days)

---

## Epic Hierarchy

```
SaaS-0: ProjectZero SaaS Platform (Epic)
├── SaaS-INFRA: Infrastructure & DevOps (Epic)
│   ├── SaaS-INFRA-1: AWS Multi-Region Setup
│   ├── SaaS-INFRA-2: Kubernetes + EKS Cluster
│   ├── SaaS-INFRA-3: CI/CD Pipeline (GitHub Actions)
│   ├── SaaS-INFRA-4: Monitoring & Alerting (Prometheus + Grafana)
│   ├── SaaS-INFRA-5: Database Migration (Postgres Schema)
│   └── SaaS-INFRA-6: Secrets Management (Vault)
├── SaaS-AUTH: Authentication & Authorization (Epic)
│   ├── SaaS-AUTH-1: Auth0 Integration
│   ├── SaaS-AUTH-2: Signup & Login Endpoints
│   ├── SaaS-AUTH-3: RBAC Middleware
│   ├── SaaS-AUTH-4: MFA Setup & Verification
│   ├── SaaS-AUTH-5: API Keys Generation
│   └── SaaS-AUTH-6: SSO (SAML/OIDC) — Phase 2
├── SaaS-BILLING: Billing & Subscriptions (Epic)
│   ├── SaaS-BILL-1: Stripe Integration
│   ├── SaaS-BILL-2: Subscription Management API
│   ├── SaaS-BILL-3: Usage Metering System
│   ├── SaaS-BILL-4: Invoice Management
│   ├── SaaS-BILL-5: Billing Portal UI
│   └── SaaS-BILL-6: Upgrade/Downgrade Flow
├── SaaS-ORG: Organization Management (Epic)
│   ├── SaaS-ORG-1: Org CRUD Endpoints
│   ├── SaaS-ORG-2: Workspace Management
│   ├── SaaS-ORG-3: Member Invitation & RBAC
│   ├── SaaS-ORG-4: Settings Pages (Profile, Members, Security)
│   └── SaaS-ORG-5: Tenant Isolation (RLS + Validation)
├── SaaS-AUDIT: Audit & Compliance (Epic)
│   ├── SaaS-AUDIT-1: Immutable Audit Log System
│   ├── SaaS-AUDIT-2: Audit Log Viewer & Search
│   ├── SaaS-AUDIT-3: Compliance Reports (SOC2, ISO, DPDP)
│   ├── SaaS-AUDIT-4: Compliance Dashboard
│   └── SaaS-AUDIT-5: Data Export (CSV/JSON)
├── SaaS-DASH: Dashboard & Observability (Epic)
│   ├── SaaS-DASH-1: Metrics & KPI Cards
│   ├── SaaS-DASH-2: Trend Charts (Agent Runs, Storage)
│   ├── SaaS-DASH-3: Workflow Status Table
│   ├── SaaS-DASH-4: Cost Analysis
│   └── SaaS-DASH-5: Real-time Updates (WebSocket)
├── SaaS-SEC: Security Hardening (Epic)
│   ├── SaaS-SEC-1: Threat Model & Risk Assessment
│   ├── SaaS-SEC-2: Encryption (TLS, AES-256)
│   ├── SaaS-SEC-3: Rate Limiting
│   ├── SaaS-SEC-4: OWASP ZAP Scanning
│   └── SaaS-SEC-5: Penetration Testing
├── SaaS-FE: Frontend Components (Epic)
│   ├── SaaS-FE-1: Auth Pages (Login, Signup, MFA)
│   ├── SaaS-FE-2: Onboarding Flow (4 Steps)
│   ├── SaaS-FE-3: Dashboard (Home Page)
│   ├── SaaS-FE-4: Billing Portal
│   ├── SaaS-FE-5: Settings Pages
│   └── SaaS-FE-6: Compliance Pages
└── SaaS-QA: Testing & QA (Epic)
    ├── SaaS-QA-1: Unit Tests (80% Coverage)
    ├── SaaS-QA-2: Integration Tests
    ├── SaaS-QA-3: E2E Tests (Playwright)
    ├── SaaS-QA-4: Load Testing
    └── SaaS-QA-5: Security Testing (OWASP ZAP)
```

---

## Tier 1: CRITICAL PATH (Week 1–2)

### Sprint 1: Foundation & External Integrations (May 1–7, 2026)

**Capacity**: 28 engineer-days (4 FTE × 7 days)

#### SaaS-INFRA-1: AWS Multi-Region Setup
- **Type**: Epic
- **Points**: 13
- **Priority**: P0
- **Owner**: DevOps
- **Due**: May 3
- **Subtasks**:
  - [ ] SaaS-INFRA-1.1: Set up primary region (us-east-1) - VPC, subnets, security groups
  - [ ] SaaS-INFRA-1.2: Set up secondary region (eu-west-1) - replicate VPC config
  - [ ] SaaS-INFRA-1.3: RDS Postgres primary (us-east-1) + replica (eu-west-1)
  - [ ] SaaS-INFRA-1.4: ElastiCache Redis cluster (primary region, replication)
  - [ ] SaaS-INFRA-1.5: Route53 DNS with failover routing
  - [ ] SaaS-INFRA-1.6: S3 bucket setup with cross-region replication (backups)
  - [ ] SaaS-INFRA-1.7: Test failover (kill primary, verify secondary takes over)
- **Definition of Done**:
  - [ ] Both regions up and running
  - [ ] Failover tested + documented
  - [ ] RPO = 5 min, RTO = 15 min verified
  - [ ] Cost estimate provided
  - [ ] Runbook for manual failover created
- **Blocked By**: None
- **Blocks**: SaaS-INFRA-2, SaaS-INFRA-3, all deployments

#### SaaS-INFRA-5: Postgres Schema Migration
- **Type**: Epic
- **Points**: 13
- **Priority**: P0
- **Owner**: Backend + DevOps
- **Due**: May 5
- **Subtasks**:
  - [ ] SaaS-INFRA-5.1: Design new schema (orgs, billing, audit, users_orgs)
  - [ ] SaaS-INFRA-5.2: Alembic migration script (staging test)
  - [ ] SaaS-INFRA-5.3: Enable RLS on all tables (org_id-based filtering)
  - [ ] SaaS-INFRA-5.4: Audit log partitioning (monthly)
  - [ ] SaaS-INFRA-5.5: Test migration (staging DB, verify zero data loss)
  - [ ] SaaS-INFRA-5.6: Rollback strategy + testing
  - [ ] SaaS-INFRA-5.7: Production migration (blue-green or rolling)
- **Definition of Done**:
  - [ ] Schema migrated on staging
  - [ ] Zero data loss verified
  - [ ] RLS tests pass (user X cannot read org Y data)
  - [ ] Rollback tested
  - [ ] Production migration runbook written
- **Blocked By**: None
- **Blocks**: All data-dependent work

#### SaaS-AUTH-1: Auth0 Integration
- **Type**: Story
- **Points**: 8
- **Priority**: P0
- **Owner**: Backend
- **Due**: May 4
- **Subtasks**:
  - [ ] SaaS-AUTH-1.1: Create Auth0 tenant + application
  - [ ] SaaS-AUTH-1.2: Configure email/password + social login (Google, GitHub)
  - [ ] SaaS-AUTH-1.3: Set up Rules (auto-sync user.email → Postgres)
  - [ ] SaaS-AUTH-1.4: Test login flow (end-to-end)
  - [ ] SaaS-AUTH-1.5: Token validation endpoint (verify JWT + extract org_id)
  - [ ] SaaS-AUTH-1.6: Handle token refresh + expiry
  - [ ] SaaS-AUTH-1.7: Configure SAML/OIDC templates (for Phase 2)
- **Definition of Done**:
  - [ ] Auth0 tenant configured
  - [ ] Email/password login works
  - [ ] Social login tested
  - [ ] Token validation working
  - [ ] Rules syncing users to DB
- **Blocked By**: None
- **Blocks**: SaaS-AUTH-2, SaaS-FE-1

#### SaaS-BILL-1: Stripe Integration
- **Type**: Story
- **Points**: 13
- **Priority**: P0
- **Owner**: Backend
- **Due**: May 5
- **Subtasks**:
  - [ ] SaaS-BILL-1.1: Create Stripe account + sandbox mode
  - [ ] SaaS-BILL-1.2: Define products (Starter, Professional, Enterprise)
  - [ ] SaaS-BILL-1.3: Define pricing tiers
  - [ ] SaaS-BILL-1.4: Set up webhook endpoints (payment_succeeded, subscription.updated)
  - [ ] SaaS-BILL-1.5: Implement Stripe API client (Python SDK)
  - [ ] SaaS-BILL-1.6: Test checkout flow (end-to-end in sandbox)
  - [ ] SaaS-BILL-1.7: Implement webhook handler + event logging
  - [ ] SaaS-BILL-1.8: Set up webhook retry logic + event deduplication
- **Definition of Done**:
  - [ ] Stripe products + prices created
  - [ ] Checkout flow works in sandbox
  - [ ] Webhooks receiving events
  - [ ] Event logging + retry logic tested
  - [ ] Production readiness checklist completed
- **Blocked By**: SaaS-INFRA-5 (schema for subscriptions table)
- **Blocks**: SaaS-BILL-2, SaaS-BILL-5

#### SaaS-INFRA-6: FastAPI Backend Scaffold
- **Type**: Story
- **Points**: 8
- **Priority**: P0
- **Owner**: Backend
- **Due**: May 3
- **Subtasks**:
  - [ ] SaaS-INFRA-6.1: Initialize FastAPI project (Pydantic models, app structure)
  - [ ] SaaS-INFRA-6.2: Database connection pool (sqlalchemy + asyncio)
  - [ ] SaaS-INFRA-6.3: Alembic for migrations
  - [ ] SaaS-INFRA-6.4: Base exception handling + error responses
  - [ ] SaaS-INFRA-6.5: CORS + security headers
  - [ ] SaaS-INFRA-6.6: Logging setup (structured logging, request/response)
  - [ ] SaaS-INFRA-6.7: Auth middleware (JWT validation, org_id context)
  - [ ] SaaS-INFRA-6.8: HealthCheck endpoint (/health, /ready)
- **Definition of Done**:
  - [ ] FastAPI server starts + health checks pass
  - [ ] Auth middleware working
  - [ ] Logging structured + searchable
  - [ ] Error handling consistent
  - [ ] Ready for endpoint implementation
- **Blocked By**: SaaS-INFRA-5
- **Blocks**: All API endpoints

---

### Sprint 2: Core APIs & Frontend Foundation (May 8–14, 2026)

**Capacity**: 28 engineer-days (4 FTE × 7 days)

#### SaaS-AUTH-2: Signup & Login Endpoints
- **Type**: Story
- **Points**: 8
- **Priority**: P0
- **Owner**: Backend + Frontend
- **Due**: May 10
- **Subtasks**:
  - [ ] SaaS-AUTH-2.1 (Backend): POST /api/v1/auth/signup (email, org name, password)
  - [ ] SaaS-AUTH-2.2 (Backend): POST /api/v1/auth/login (email, password)
  - [ ] SaaS-AUTH-2.3 (Backend): POST /api/v1/auth/logout
  - [ ] SaaS-AUTH-2.4 (Backend): POST /api/v1/auth/refresh-token
  - [ ] SaaS-AUTH-2.5 (Backend): POST /api/v1/auth/forgot-password
  - [ ] SaaS-AUTH-2.6 (Backend): POST /api/v1/auth/reset-password (token-based)
  - [ ] SaaS-AUTH-2.7 (Frontend): Login form + error handling
  - [ ] SaaS-AUTH-2.8 (Frontend): Signup form (email, org name, password confirmation)
  - [ ] SaaS-AUTH-2.9 (Frontend): Forgot password flow
- **Definition of Done**:
  - [ ] Backend endpoints tested (unit + integration)
  - [ ] Frontend forms work (validation, error messages)
  - [ ] Auth tokens issued + stored securely
  - [ ] Password reset email sent
  - [ ] E2E test: signup → login → redirect to dashboard
- **Blocked By**: SaaS-AUTH-1, SaaS-INFRA-6
- **Blocks**: SaaS-FE-1, SaaS-FE-2

#### SaaS-ORG-1: Org CRUD Endpoints
- **Type**: Story
- **Points**: 8
- **Priority**: P0
- **Owner**: Backend
- **Due**: May 10
- **Subtasks**:
  - [ ] SaaS-ORG-1.1: POST /api/v1/organizations (create org, set creator as Owner)
  - [ ] SaaS-ORG-1.2: GET /api/v1/organizations (list orgs for user)
  - [ ] SaaS-ORG-1.3: GET /api/v1/organizations/{org_id}
  - [ ] SaaS-ORG-1.4: PATCH /api/v1/organizations/{org_id} (update name, region, billing contact)
  - [ ] SaaS-ORG-1.5: DELETE /api/v1/organizations/{org_id} (soft delete, audit log)
  - [ ] SaaS-ORG-1.6: Org isolation tests (RLS + query filtering)
  - [ ] SaaS-ORG-1.7: Audit logging for all CRUD operations
- **Definition of Done**:
  - [ ] All endpoints tested (happy path + edge cases)
  - [ ] RLS working (user X can only read own org)
  - [ ] Audit logs created for all actions
  - [ ] Pagination implemented (for list endpoint)
- **Blocked By**: SaaS-INFRA-5, SaaS-INFRA-6
- **Blocks**: SaaS-ORG-2, SaaS-ORG-3, SaaS-BILL-2

#### SaaS-BILL-2: Subscription Management API
- **Type**: Story
- **Points**: 8
- **Priority**: P0
- **Owner**: Backend
- **Due**: May 12
- **Subtasks**:
  - [ ] SaaS-BILL-2.1: GET /api/v1/billing/subscription (current tier + period)
  - [ ] SaaS-BILL-2.2: POST /api/v1/billing/checkout (create Stripe session)
  - [ ] SaaS-BILL-2.3: POST /api/v1/billing/upgrade (change tier)
  - [ ] SaaS-BILL-2.4: POST /api/v1/billing/cancel (end subscription)
  - [ ] SaaS-BILL-2.5: GET /api/v1/billing/invoices (list invoices, paginated)
  - [ ] SaaS-BILL-2.6: GET /api/v1/billing/usage (current month usage vs quota)
  - [ ] SaaS-BILL-2.7: Webhook handler (Stripe events → update DB)
  - [ ] SaaS-BILL-2.8: Tests (mock Stripe API, webhook handling)
- **Definition of Done**:
  - [ ] All endpoints tested
  - [ ] Stripe webhooks handled + idempotent
  - [ ] Subscription status accurate
  - [ ] Usage metering working
  - [ ] E2E: upgrade subscription → verify in DB
- **Blocked By**: SaaS-BILL-1, SaaS-ORG-1
- **Blocks**: SaaS-BILL-5, SaaS-BILL-6

#### SaaS-AUTH-3: RBAC Middleware
- **Type**: Story
- **Points**: 8
- **Priority**: P0
- **Owner**: Backend
- **Due**: May 10
- **Subtasks**:
  - [ ] SaaS-AUTH-3.1: Define role permissions matrix (Owner, Engineer, Reviewer)
  - [ ] SaaS-AUTH-3.2: Implement @require_role() decorator
  - [ ] SaaS-AUTH-3.3: Implement @require_tier() decorator (Starter, Professional, Enterprise)
  - [ ] SaaS-AUTH-3.4: Implement quota enforcement (repos, users, etc.)
  - [ ] SaaS-AUTH-3.5: Test RBAC (user with wrong role denied access)
  - [ ] SaaS-AUTH-3.6: Test tier-based access (SSO only for Enterprise, etc.)
  - [ ] SaaS-AUTH-3.7: Audit logging for access denials
- **Definition of Done**:
  - [ ] Decorators working on all endpoints
  - [ ] Roles enforced correctly
  - [ ] Tiers enforced correctly
  - [ ] Access denials logged
  - [ ] Unit tests for all role combinations
- **Blocked By**: SaaS-AUTH-1, SaaS-ORG-1
- **Blocks**: All authenticated endpoints

#### SaaS-AUDIT-1: Immutable Audit Log System
- **Type**: Story
- **Points**: 13
- **Priority**: P0
- **Owner**: Backend
- **Due**: May 12
- **Subtasks**:
  - [ ] SaaS-AUDIT-1.1: Design audit log schema (id, org_id, actor_id, resource, action, changes, timestamp, IP, user_agent)
  - [ ] SaaS-AUDIT-1.2: Create Postgres table (IMMUTABLE: no UPDATE/DELETE)
  - [ ] SaaS-AUDIT-1.3: Implement audit logging middleware (auto-log all CRUD)
  - [ ] SaaS-AUDIT-1.4: Implement time-range partitioning (monthly)
  - [ ] SaaS-AUDIT-1.5: Test immutability (verify DELETE/UPDATE fail)
  - [ ] SaaS-AUDIT-1.6: Implement retention policy (30d/1y/7y based on tier)
  - [ ] SaaS-AUDIT-1.7: Test retention (old records deleted on schedule)
  - [ ] SaaS-AUDIT-1.8: Encryption for sensitive data in log (email, diffs)
- **Definition of Done**:
  - [ ] Audit table created + partitioned
  - [ ] Immutability working (constraints + tests)
  - [ ] Logging working (events captured automatically)
  - [ ] Retention policy tested
  - [ ] Performance acceptable (query on 7y of logs < 1s)
- **Blocked By**: SaaS-INFRA-5
- **Blocks**: SaaS-AUDIT-2, SaaS-AUDIT-3

#### SaaS-FE-1: Auth Pages (Login, Signup, MFA)
- **Type**: Story
- **Points**: 13
- **Priority**: P0
- **Owner**: Frontend
- **Due**: May 12
- **Subtasks**:
  - [ ] SaaS-FE-1.1: Create login page (email, password, forgot password link, OAuth buttons)
  - [ ] SaaS-FE-1.2: Create signup page (email, org name, password, terms checkbox)
  - [ ] SaaS-FE-1.3: Create forgot password page (email input, reset link)
  - [ ] SaaS-FE-1.4: Create MFA setup page (QR code, backup codes)
  - [ ] SaaS-FE-1.5: Create MFA verify page (TOTP prompt)
  - [ ] SaaS-FE-1.6: Form validation (Zod schema)
  - [ ] SaaS-FE-1.7: Error handling (display backend errors)
  - [ ] SaaS-FE-1.8: Link to backend auth endpoints
  - [ ] SaaS-FE-1.9: Store JWT token in secure storage (HttpOnly cookie preferred)
  - [ ] SaaS-FE-1.10: E2E tests (Playwright)
- **Definition of Done**:
  - [ ] Pages render correctly
  - [ ] Forms validate
  - [ ] API integration working
  - [ ] Errors displayed
  - [ ] E2E signup → login flow works
  - [ ] Mobile responsive
- **Blocked By**: SaaS-AUTH-2
- **Blocks**: SaaS-FE-2

#### SaaS-FE-2: Onboarding Flow (4 Steps)
- **Type**: Story
- **Points**: 13
- **Priority**: P0
- **Owner**: Frontend
- **Due**: May 14
- **Subtasks**:
  - [ ] SaaS-FE-2.1: Step 1 - Welcome (logo, value props, next button)
  - [ ] SaaS-FE-2.2: Step 2 - Invite Team (email input, role selector, add/remove members)
  - [ ] SaaS-FE-2.3: Step 3 - Choose Plan (pricing cards, feature comparison)
  - [ ] SaaS-FE-2.4: Step 4 - Complete (thank you, redirect to dashboard)
  - [ ] SaaS-FE-2.5: Progress indicator (1/4 → 2/4 → 3/4 → 4/4)
  - [ ] SaaS-FE-2.6: API integration (invite members, select plan, create subscription)
  - [ ] SaaS-FE-2.7: Error handling (show errors from API)
  - [ ] SaaS-FE-2.8: Multi-step state management (preserve data if go back)
  - [ ] SaaS-FE-2.9: E2E tests (full onboarding flow)
- **Definition of Done**:
  - [ ] 4 steps working
  - [ ] Progress indicator working
  - [ ] State preserved on back navigation
  - [ ] API integration working
  - [ ] E2E onboarding test passes
  - [ ] Mobile responsive
- **Blocked By**: SaaS-FE-1, SaaS-ORG-1, SaaS-BILL-2
- **Blocks**: SaaS-FE-3

---

## Tier 2: CORE FEATURES (Week 3–4)

### Sprint 3: Dashboard & Settings (May 15–21, 2026)

**Capacity**: 28 engineer-days (4 FTE × 7 days)

#### SaaS-DASH-1: Metrics & KPI Cards
- **Type**: Story
- **Points**: 8
- **Priority**: P0
- **Owner**: Frontend + Backend
- **Due**: May 17
- **Subtasks**:
  - [ ] Backend: GET /api/v1/dashboard/metrics (agents_runs_mtd, repos_count, users_count, storage_gb)
  - [ ] Frontend: Create MetricsCard component (4x cards)
  - [ ] Frontend: API integration + loading states
  - [ ] Frontend: Real-time updates (refresh every 30s or WebSocket)
  - [ ] Tests: Unit (component), Integration (API), E2E (dashboard loads)
- **Definition of Done**:
  - [ ] Metrics display correctly
  - [ ] Real-time updates working
  - [ ] Loading states working
  - [ ] Tests passing
  - [ ] Mobile responsive

#### SaaS-DASH-2: Trend Charts
- **Type**: Story
- **Points**: 8
- **Priority**: P0
- **Owner**: Frontend + Backend
- **Due**: May 18
- **Subtasks**:
  - [ ] Backend: GET /api/v1/dashboard/trends (agents_runs by day, last 30 days)
  - [ ] Frontend: Create TrendChart component (Recharts)
  - [ ] Frontend: API integration + loading states
  - [ ] Tests: Unit (chart rendering), Integration (API)
- **Definition of Done**:
  - [ ] Chart renders correctly
  - [ ] Data loads from API
  - [ ] Responsive to window resize

#### SaaS-DASH-3: Workflow Status Table
- **Type**: Story
- **Points**: 13
- **Priority**: P0
- **Owner**: Frontend + Backend
- **Due**: May 19
- **Subtasks**:
  - [ ] Backend: GET /api/v1/workflows (org's workflows, paginated, last 48h)
  - [ ] Frontend: Create WorkflowStatusTable (TanStack Table)
  - [ ] Frontend: Sortable columns (date, status, duration)
  - [ ] Frontend: Click row → detail modal
  - [ ] Frontend: Status badge (Maker ✅, Checker 🔄, Reviewer ⏳, Approver ⏹️)
  - [ ] Tests: E2E (click workflow → modal)
- **Definition of Done**:
  - [ ] Table renders correctly
  - [ ] Sorting works
  - [ ] Pagination works
  - [ ] Click → detail modal
  - [ ] Tests passing

#### SaaS-ORG-3: Member Invitation & RBAC
- **Type**: Story
- **Points**: 13
- **Priority**: P0
- **Owner**: Backend + Frontend
- **Due**: May 20
- **Subtasks**:
  - [ ] Backend: POST /api/v1/organizations/{org_id}/members (invite)
  - [ ] Backend: GET /api/v1/organizations/{org_id}/members (list)
  - [ ] Backend: PATCH /api/v1/organizations/{org_id}/members/{user_id} (update role)
  - [ ] Backend: DELETE /api/v1/organizations/{org_id}/members/{user_id} (remove)
  - [ ] Backend: Email sending (invite link + expiry)
  - [ ] Frontend: Members table (email, role, joined date, actions)
  - [ ] Frontend: Invite form (email input, role selector)
  - [ ] Frontend: Role selector (dropdown)
  - [ ] Frontend: Confirm dialog before remove
  - [ ] Tests: RBAC enforcement, email sending, E2E invite flow
- **Definition of Done**:
  - [ ] Invite email sent
  - [ ] Role changes working
  - [ ] Remove working (soft delete)
  - [ ] RBAC enforced (only Owner can manage members)
  - [ ] E2E: invite → email → join org

#### SaaS-ORG-4: Settings Pages (Profile, Members, Security)
- **Type**: Story
- **Points**: 13
- **Priority**: P0
- **Owner**: Frontend + Backend
- **Due**: May 21
- **Subtasks**:
  - [ ] Backend: PATCH /api/v1/organizations/{org_id} (update profile)
  - [ ] Frontend: ProfilePage (name, description, logo, region)
  - [ ] Frontend: MembersPage (table + invite form)
  - [ ] Frontend: SecurityPage (MFA, API keys, password change)
  - [ ] Frontend: Settings sidebar nav (4 items)
  - [ ] Frontend: Form validation + error handling
  - [ ] Tests: Form submission, API integration
- **Definition of Done**:
  - [ ] All settings pages render
  - [ ] Forms work + validate
  - [ ] API integration working
  - [ ] Changes persist in DB
  - [ ] Mobile responsive

#### SaaS-BILL-5: Billing Portal UI
- **Type**: Story
- **Points**: 13
- **Priority**: P0
- **Owner**: Frontend + Backend
- **Due**: May 21
- **Subtasks**:
  - [ ] Frontend: BillingPage (current subscription, usage, recent invoices)
  - [ ] Frontend: SubscriptionCard (tier, period, usage bars)
  - [ ] Frontend: InvoiceTable (list, download button)
  - [ ] Frontend: Upgrade/Downgrade buttons → pricing page
  - [ ] Frontend: Cancel subscription button → confirm dialog
  - [ ] Backend: GET /api/v1/billing/subscription + invoices
  - [ ] Backend: PDF generation for invoices (if not already in Stripe)
  - [ ] Frontend: Integration + loading states
  - [ ] Tests: E2E billing flow
- **Definition of Done**:
  - [ ] Billing page renders correctly
  - [ ] Usage displays accurately
  - [ ] Invoices downloadable
  - [ ] Upgrade/downgrade buttons work
  - [ ] Mobile responsive

#### SaaS-AUDIT-2: Audit Log Viewer & Search
- **Type**: Story
- **Points**: 13
- **Priority**: P0
- **Owner**: Frontend + Backend
- **Due**: May 21
- **Subtasks**:
  - [ ] Backend: GET /api/v1/audit-logs (filters: action, actor, resource, date range)
  - [ ] Backend: Full-text search on actor email
  - [ ] Backend: Pagination (100 rows/page)
  - [ ] Frontend: AuditLogsPage (table + filters)
  - [ ] Frontend: Filter bar (dropdown selectors)
  - [ ] Frontend: Search input
  - [ ] Frontend: CSV export button
  - [ ] Tests: Filter logic, search, pagination
- **Definition of Done**:
  - [ ] Audit logs display correctly
  - [ ] Filters work
  - [ ] Search works
  - [ ] Export to CSV works
  - [ ] Performance acceptable (1K+ rows)
  - [ ] Mobile responsive (scrollable table)

---

### Sprint 4: Infrastructure & Compliance (May 22–28, 2026)

**Capacity**: 28 engineer-days (4 FTE × 7 days)

#### SaaS-INFRA-2: Kubernetes + EKS Cluster
- **Type**: Epic
- **Points**: 13
- **Priority**: P0
- **Owner**: DevOps
- **Due**: May 24
- **Subtasks**:
  - [ ] Create EKS clusters (primary us-east-1, secondary eu-west-1)
  - [ ] Create node groups (auto-scaling, instance types)
  - [ ] Setup networking (VPC, subnets, security groups)
  - [ ] Install ingress controller (NGINX)
  - [ ] Install cert-manager (SSL/TLS)
  - [ ] Test pod deployment + service discovery
  - [ ] Setup persistent volumes (for logs, etc.)
- **Definition of Done**:
  - [ ] Clusters running
  - [ ] Nodes healthy
  - [ ] Networking working
  - [ ] Sample app deployed + accessible
  - [ ] Cost estimate provided

#### SaaS-INFRA-3: CI/CD Pipeline
- **Type**: Epic
- **Points**: 13
- **Priority**: P0
- **Owner**: DevOps
- **Due**: May 26
- **Subtasks**:
  - [ ] Create GitHub Actions workflow
  - [ ] Lint stage (ruff, pyright)
  - [ ] Test stage (pytest, coverage ≥80%)
  - [ ] Build stage (Docker image)
  - [ ] Push to ECR (AWS container registry)
  - [ ] Deploy to staging EKS
  - [ ] Manual approval gate before production
  - [ ] Deploy to production EKS
  - [ ] Rollback mechanism (git revert)
- **Definition of Done**:
  - [ ] Workflow runs on every push
  - [ ] Tests must pass before merge
  - [ ] Linting must pass
  - [ ] Coverage must be ≥80%
  - [ ] Staging deployment automatic
  - [ ] Production deployment requires approval

#### SaaS-INFRA-4: Monitoring & Alerting
- **Type**: Epic
- **Points**: 13
- **Priority**: P0
- **Owner**: DevOps
- **Due**: May 27
- **Subtasks**:
  - [ ] Install Prometheus (metrics collection)
  - [ ] Install Grafana (dashboards)
  - [ ] Create dashboards (API latency, error rates, DB queries)
  - [ ] Set up alerting rules (Slack integration)
  - [ ] Alerts: 5xx errors, latency > 1s, DB pool exhaustion
  - [ ] Install ELK stack (logs)
  - [ ] Test alert firing (simulate error)
- **Definition of Done**:
  - [ ] Dashboards show real metrics
  - [ ] Alerts configured + tested
  - [ ] Logs searchable in ELK
  - [ ] Runbook for common alerts created

#### SaaS-SEC-1: Threat Model & Risk Assessment
- **Type**: Story
- **Points**: 8
- **Priority**: P0
- **Owner**: Security
- **Due**: May 23
- **Subtasks**:
  - [ ] Apply STRIDE model (Spoofing, Tampering, Repudiation, Info Disclosure, Denial of Service, Elevation of Privilege)
  - [ ] Identify assets (orgs, users, billing data, audit logs)
  - [ ] Identify threats per asset
  - [ ] Assess impact + likelihood (H/M/L)
  - [ ] Propose mitigations
  - [ ] Document risk register
- **Definition of Done**:
  - [ ] Risk register created
  - [ ] Threats documented
  - [ ] Mitigations proposed
  - [ ] Risk scores assigned

#### SaaS-SEC-2: Encryption (TLS, AES-256)
- **Type**: Story
- **Points**: 8
- **Priority**: P0
- **Owner**: Security + Backend
- **Due**: May 25
- **Subtasks**:
  - [ ] Enable TLS 1.3 (API, DB connections, all traffic)
  - [ ] Generate certificates (AWS ACM or Let's Encrypt)
  - [ ] Configure encryption at rest (Postgres, S3)
  - [ ] Implement column-level encryption (sensitive data: email diffs in audit logs)
  - [ ] Secrets management (use Vault or AWS Secrets Manager)
  - [ ] Test encryption (verify data encrypted on disk)
- **Definition of Done**:
  - [ ] All traffic encrypted (TLS 1.3)
  - [ ] At-rest encryption enabled
  - [ ] Secrets not in git
  - [ ] Key rotation policy documented
  - [ ] Tests passing

#### SaaS-SEC-3: Rate Limiting
- **Type**: Story
- **Points**: 5
- **Priority**: P1
- **Owner**: Backend
- **Due**: May 26
- **Subtasks**:
  - [ ] Implement Redis-backed rate limiter
  - [ ] Limits per org (e.g., 1000 API calls/hour)
  - [ ] Limits per endpoint (auth: 10 attempts/5min)
  - [ ] Return 429 (Too Many Requests) when limit exceeded
  - [ ] Tests: verify limit enforcement
- **Definition of Done**:
  - [ ] Rate limiter working
  - [ ] Limits enforced correctly
  - [ ] Tests passing
  - [ ] Handles distributed requests (Redis)

#### SaaS-AUDIT-3: Compliance Reports (SOC2, ISO, DPDP)
- **Type**: Story
- **Points**: 13
- **Priority**: P1
- **Owner**: Backend + Compliance
- **Due**: May 28
- **Subtasks**:
  - [ ] POST /api/v1/compliance/report (generate report)
  - [ ] Report includes: audit log summary, access matrix, change log, incident log
  - [ ] PDF export (signed by admin)
  - [ ] Store in compliance_reports table
  - [ ] Email PDF to compliance officer
  - [ ] SOC2-specific: evidence from audit logs + config checks
  - [ ] ISO-specific: asset inventory, access controls
  - [ ] DPDP-specific: consent mechanism, breach notification
- **Definition of Done**:
  - [ ] Report generates successfully
  - [ ] PDF looks professional
  - [ ] All required sections included
  - [ ] Data accurate (from audit logs + config)

---

## Tier 3: Testing & Polish (Week 5, Beyond)

### Sprint 5: QA & Load Testing (May 29 – June 4, 2026)

#### SaaS-QA-1: Unit Tests (80% Coverage)
- **Type**: Epic
- **Points**: 21
- **Priority**: P0
- **Owner**: Backend + Frontend
- **Due**: May 31
- **Subtasks**:
  - [ ] Backend: Unit tests for all services (auth, billing, org, audit)
  - [ ] Backend: Pytest fixtures (mock DB, Stripe API, Auth0)
  - [ ] Backend: Coverage report (must be ≥80%)
  - [ ] Frontend: Unit tests for all components (forms, tables, modals)
  - [ ] Frontend: Vitest + React Testing Library
  - [ ] Frontend: Coverage report (≥80%)

#### SaaS-QA-2: Integration Tests
- **Type**: Epic
- **Points**: 13
- **Priority**: P0
- **Owner**: Backend + Frontend
- **Due**: June 2
- **Subtasks**:
  - [ ] Backend: Integration tests (auth flow, subscription upgrade, audit logging)
  - [ ] Backend: Test with real Postgres (testcontainers)
  - [ ] Frontend: Integration tests (API calls, state updates)

#### SaaS-QA-3: E2E Tests (Playwright)
- **Type**: Epic
- **Points**: 21
- **Priority**: P0
- **Owner**: QA
- **Due**: June 4
- **Subtasks**:
  - [ ] Full signup → login → onboarding → dashboard flow
  - [ ] Upgrade subscription → Stripe checkout
  - [ ] Invite team member → email → join org
  - [ ] Audit logs → export CSV
  - [ ] Settings → update profile
  - [ ] All tests must pass in staging environment

#### SaaS-QA-4: Load Testing
- **Type**: Story
- **Points**: 8
- **Priority**: P1
- **Owner**: DevOps + Backend
- **Due**: June 4
- **Subtasks**:
  - [ ] Create load test scenario (1000 concurrent users)
  - [ ] Run against staging
  - [ ] Monitor API latency, DB queries, error rates
  - [ ] Identify bottlenecks
  - [ ] Tune if needed (caching, DB indexes, etc.)

---

## Summary by Sprint

| Sprint | Dates | FTE | Effort | Focus | Status |
|--------|-------|-----|--------|-------|--------|
| **Sprint 1** | May 1–7 | 4 | 28 days | AWS, Postgres, Auth0, Stripe, FastAPI | 🔴 CRITICAL |
| **Sprint 2** | May 8–14 | 4 | 28 days | Auth endpoints, Org APIs, Billing, Frontend auth/onboarding | 🔴 CRITICAL |
| **Sprint 3** | May 15–21 | 4 | 28 days | Dashboard, Settings, Billing UI, Audit logs | 🟠 HIGH |
| **Sprint 4** | May 22–28 | 4 | 28 days | Kubernetes, CI/CD, Monitoring, Security | 🟠 HIGH |
| **Sprint 5** | May 29–Jun 4 | 4 | 28 days | Unit/Integration/E2E tests, Load testing, QA | 🟠 HIGH |
| **TOTAL** | 5 weeks | — | 140 days | All P0 + P1 work | — |

---

## Ticket Status Template

**Status Workflow**: To Do → In Progress → Testing → Done

**Ticket Template**:
```
Title: [TICKET-ID] Feature Name
Type: Story | Epic | Task
Points: 5 | 8 | 13 | 21
Priority: P0 | P1 | P2 | P3
Sprint: Sprint 1 | Sprint 2 | ...
Status: To Do | In Progress | Testing | Done
Owner: @engineer-name
Due: YYYY-MM-DD

Description: What needs to be built

Acceptance Criteria:
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

Subtasks:
- [ ] Task 1
- [ ] Task 2
- [ ] Task 3

Definition of Done:
- [ ] Code written (TDD)
- [ ] Tests pass (unit + integration + E2E)
- [ ] Coverage ≥ 80%
- [ ] Linting passes (ruff, pyright)
- [ ] Commit references ticket ID
- [ ] Reviewed + approved
- [ ] Deployed to staging
```

---

**Document Version**: 1.0  
**Created**: 2026-04-19  
**Status**: Ready for Sprint Planning + Implementation
