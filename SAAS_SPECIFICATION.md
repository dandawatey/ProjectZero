# ProjectZero SaaS Specification

**Status**: Specification Stage (Stage 1)  
**Date**: 2026-04-19  
**Author**: Product Team  
**Version**: 1.0

---

## BMAD Framework

### Business
- **Problem**: Teams lack governance + compliance for AI-driven product development. Existing tools (GitHub, JIRA, CI/CD) are scattered. Compliance (SOC2, ISO, DPDP) requires manual audits.
- **Value Prop**: ProjectZero SaaS automates governed development: AI agents build features, gates enforce 80% coverage + lint + types + OWASP, audit logs capture everything, compliance dashboards satisfy auditors.
- **Success Metrics**: 
  - 50 paying customers by Month 6, 500 by Month 12
  - $25K MRR by Month 6, $250K by Month 12
  - NPS >40 (Month 6), >50 (Month 12)
  - <5% churn (Month 6), <3% (Month 12)
- **Stakeholders**: Product team (PMs, engineers), Finance (billing), Legal (compliance), Sales (GTM)

### Market
- **Target Users**: 
  - **Primary**: Mid-market engineering teams (20–50 engineers) building AI products
  - **Secondary**: Enterprises needing compliance-first product development
  - **Tertiary**: Agencies building custom products for clients
- **Competitive Landscape**: 
  - GitHub Copilot + Actions (workflow automation, no governance)
  - Vercel AI + v0 (frontend generation, limited backend)
  - LinearB (engineering metrics, no development)
  - **Our edge**: End-to-end governed development with compliance baked in
- **Market Size**: $5B TAM (product dev tooling), $500M SAM (compliance + governance), $50M SOM (Year 1 target)
- **Positioning**: "Governed AI-driven product development for compliance-first organizations"

### Architecture
- **Tech Stack**: 
  - Frontend: React 18 + TypeScript + TailwindCSS
  - Backend: FastAPI + Python 3.11 + Pydantic
  - Database: PostgreSQL 15 (multi-region replicas)
  - Cache: Redis Cluster
  - Orchestration: Temporal Workflows
  - Auth: Auth0 (SSO + MFA)
  - Billing: Stripe (subscriptions + metering)
  - Analytics: Kafka → BigQuery
  - Infrastructure: Kubernetes on AWS (EKS)
- **Data Architecture**: Multi-tenant via RLS + org_id partitioning, geo-distributed replicas
- **API Design**: REST + GraphQL, OpenAPI 3.0 spec, webhook support
- **Scalability**: Horizontal scaling (K8s), DB sharding by org_id (Enterprise), read replicas per region
- **Security**: TLS 1.3, AES-256 at rest, RBAC, immutable audit logs, RLS for tenant isolation
- **Compliance**: SOC2 Type II (audit-ready), ISO27001 (infra controls), DPDP (data privacy)

### Delivery
- **Timeline**: 
  - Phase 1 (Beta): Weeks 1–4 (Starter + Professional tiers)
  - Phase 2 (GA): Weeks 5–8 (Production hardening, bug fixes)
  - Phase 3 (Enterprise): Weeks 9–16 (SSO, advanced RBAC, compliance dashboards)
- **Milestones**:
  - Week 1: Stripe integration, org/user schema, billing endpoints
  - Week 2: Auth0 integration, RBAC middleware, frontend dashboard
  - Week 3: Audit log system, compliance report generator
  - Week 4: QA, load testing, GA readiness
- **Team**: 7 FTE (2 backend, 2 frontend, 1 DevOps, 1 PM, 1 compliance/security)
- **Dependencies**: 
  - Stripe sandbox setup (Week 1)
  - Auth0 configuration (Week 1)
  - AWS multi-region setup (Week 1)
  - External SOC2 audit (Month 3)

---

## Feature Specifications

### Epic 1: Organization & Tenant Management
**Description**: Multi-org support with billing/usage tracking per tenant.

**User Stories**:

**SaaS-1**: User can sign up and create organization
- **Acceptance Criteria**:
  - Sign-up form (email/password) or sign-in via Google/GitHub
  - Creates organization + assigns creator as Owner
  - Redirect to onboarding flow
  - Audit log: `organization.created`
- **Story Points**: 5
- **Priority**: P0
- **Depends On**: None
- **Blocks**: SaaS-2, SaaS-4

**SaaS-2**: Organization admin can invite team members
- **Acceptance Criteria**:
  - Invite form: email, role selector (Engineer/Reviewer/Owner)
  - Sends invite email with link + expiry (7 days)
  - Invitee clicks link, sets password, joins org
  - Members table shows: email, role, joined date, last active
  - Audit log: `member.invited`, `member.joined`
- **Story Points**: 8
- **Priority**: P0
- **Depends On**: SaaS-1
- **Blocks**: SaaS-5

**SaaS-3**: Org admin can manage team members (update role, remove)
- **Acceptance Criteria**:
  - Role selector: change Engineer → Reviewer (or vice versa)
  - Remove member (soft delete + audit log, data persists)
  - Cannot remove self
  - Audit log: `member.role_updated`, `member.removed`
- **Story Points**: 5
- **Priority**: P0
- **Depends On**: SaaS-2
- **Blocks**: None

**SaaS-4**: Organizations can have multiple workspaces (repos)
- **Acceptance Criteria**:
  - "New workspace" button → name, description, region (optional)
  - Creates workspace + GitHub repo link (optional)
  - Workspace list shows: name, repos count, last active
  - Quota enforcement: Starter 1, Professional 10, Enterprise unlimited
  - Audit log: `workspace.created`
- **Story Points**: 8
- **Priority**: P0
- **Depends On**: SaaS-1
- **Blocks**: SaaS-15

---

### Epic 2: Billing & Subscription Management
**Description**: Stripe integration for tier management, invoicing, usage tracking.

**User Stories**:

**SaaS-5**: Billing admin can select and upgrade subscription tier
- **Acceptance Criteria**:
  - Pricing page: show Starter/Professional/Enterprise tiers with features table
  - "Upgrade" button → Stripe hosted checkout (test mode in beta)
  - Checkout captures: payment method, billing address
  - Webhook: `invoice.payment_succeeded` → create invoice record, update tier
  - Email: confirmation + invoice PDF
  - Audit log: `subscription.created` or `subscription.upgraded`
- **Story Points**: 13
- **Priority**: P0
- **Depends On**: SaaS-1
- **Blocks**: SaaS-6, SaaS-7

**SaaS-6**: Billing admin can cancel subscription
- **Acceptance Criteria**:
  - "Cancel subscription" button → confirmation dialog
  - Cancels Stripe subscription (end of current period or immediate)
  - Updates org.tier = "starter" (free)
  - Email: cancellation confirmation
  - Audit log: `subscription.canceled`
- **Story Points**: 5
- **Priority**: P1
- **Depends On**: SaaS-5
- **Blocks**: None

**SaaS-7**: System tracks org usage (agents runs, repos, users) for metering
- **Acceptance Criteria**:
  - Cron job: hourly aggregation of usage metrics
  - Tracks: agent_runs, repos_created, users_invited, storage_gb
  - Stores in billing_usage table with period (month)
  - API endpoint: `/api/v1/billing/usage` returns current month + breakdown
  - Dashboard widget: "Usage vs quota" with visual indicators (green/yellow/red)
  - Audit log: `usage.recorded`
- **Story Points**: 8
- **Priority**: P0
- **Depends On**: SaaS-5
- **Blocks**: SaaS-8

**SaaS-8**: Billing admin can view invoices and download PDFs
- **Acceptance Criteria**:
  - Invoice list page: date, amount, status (paid/unpaid), actions (download PDF)
  - PDF includes: invoice number, items (base + overage), dates, payment method
  - Stripe webhook: auto-sync invoices to invoices table
  - Email: monthly invoice PDF sent to billing contact
  - Audit log: `invoice.viewed`, `invoice.downloaded`
- **Story Points**: 8
- **Priority**: P1
- **Depends On**: SaaS-5
- **Blocks**: None

---

### Epic 3: Auth & Access Control
**Description**: RBAC, SSO (Enterprise), MFA, API key management.

**User Stories**:

**SaaS-9**: System enforces RBAC based on tier
- **Acceptance Criteria**:
  - Starter: Owner only
  - Professional: Owner, Engineer, Reviewer (3 roles, fixed permissions)
  - Enterprise: Custom roles (via admin panel, roadmap Phase 4)
  - Middleware checks: `user.role` + `org.tier` → grant access
  - API: `/api/v1/organizations/{org_id}/roles` lists available roles
  - Audit log: `rbac.enforced` (on access check + denial)
- **Story Points**: 13
- **Priority**: P0
- **Depends On**: SaaS-1, SaaS-3
- **Blocks**: SaaS-10, SaaS-11

**SaaS-10**: Users can enable MFA (TOTP)
- **Acceptance Criteria**:
  - Settings page: "Enable 2FA" → QR code + backup codes
  - User scans with Authenticator app (Google/Authy/Microsoft)
  - Verify: user enters 6-digit code
  - Next login: prompt for TOTP code after password
  - Backup codes: 10 one-time use codes (download/print)
  - Audit log: `mfa.enabled`, `mfa.disabled`, `mfa.used`
- **Story Points**: 8
- **Priority**: P1
- **Depends On**: SaaS-1
- **Blocks**: None

**SaaS-11**: Enterprise orgs can enable SSO (SAML/OIDC)
- **Acceptance Criteria**:
  - Admin panel: "SSO configuration" → upload SAML metadata or enter OIDC endpoints
  - Maps SAML attributes to user.email, user.name, user.role (optional)
  - Login page: "Sign in with SSO" button (if configured)
  - Just-in-time provisioning: new users auto-created on first SSO login
  - Audit log: `sso.configured`, `sso.login`, `user.auto_provisioned`
  - Tier enforcement: Professional+ only
- **Story Points**: 13
- **Priority**: P2 (Phase 3)
- **Depends On**: SaaS-9
- **Blocks**: None

**SaaS-12**: Developers can create and manage API keys
- **Acceptance Criteria**:
  - Settings page: "API Keys" section
  - "Generate key" → creates key, shows once (copy/download)
  - Key has scopes: agent_read, agent_write, workflow_read, audit_read
  - Key has expiry: 1 year (configurable)
  - List keys: name, scopes, created date, last used, expiry
  - Revoke key: delete immediately
  - Audit log: `api_key.created`, `api_key.revoked`, `api_key.used`
- **Story Points**: 8
- **Priority**: P2
- **Depends On**: SaaS-1
- **Blocks**: None

---

### Epic 4: Dashboard & Observability
**Description**: Real-time dashboard showing org health, agent runs, workflows, metrics.

**User Stories**:

**SaaS-13**: Dashboard shows org metrics (agents runs, repos, users, storage)
- **Acceptance Criteria**:
  - Cards: "Total agents runs" (MTD), "Active repos", "Team members", "Storage used"
  - Trend chart: agents runs last 7 days (line graph)
  - Quota indicator: "5/10 repos used" (progress bar, color coding)
  - Drill-down: click card → detailed view (list of runs, repos, members)
  - Real-time updates: WebSocket or 30s poll
  - Audit log: `dashboard.viewed`
- **Story Points**: 13
- **Priority**: P0
- **Depends On**: SaaS-7
- **Blocks**: None

**SaaS-14**: Dashboard shows recent agent workflows (Maker → Checker → Reviewer → Approver)
- **Acceptance Criteria**:
  - Table: workflow ID, ticket, status (in-progress/completed/failed), duration, last 48h
  - Status badge: Maker ✅ → Checker 🔄 → Reviewer ⏳ → Approver ⏹️
  - Click row → workflow detail page (gates, errors, logs)
  - Filter: status, date range, agent type
  - Real-time updates: WebSocket
  - Audit log: `workflow.viewed`
- **Story Points**: 13
- **Priority**: P1
- **Depends On**: Enterprise framework (PRJ0-98..111)
- **Blocks**: None

**SaaS-15**: Admin can access detailed audit logs with search/filter
- **Acceptance Criteria**:
  - Audit page: table of all events (immutable, append-only)
  - Columns: timestamp, actor (email), resource (org/user/workspace/subscription), action, changes (JSON diff)
  - Filters: action type, actor, resource, date range
  - Search: full-text search on actor email + resource name
  - Export: CSV/JSON for compliance audits
  - Retention: 30d (Starter), 1y (Professional), 7y (Enterprise)
  - Pagination: 100 rows/page
  - Audit log: `audit_log.viewed`, `audit_log.exported`
- **Story Points**: 13
- **Priority**: P0
- **Depends On**: SaaS-1
- **Blocks**: SaaS-19

**SaaS-16**: Dashboard shows cost per ticket (agent hours × rate)
- **Acceptance Criteria**:
  - Card: "Avg cost per ticket" (last 30 days)
  - Formula: (agent_hours × $50/hr) ÷ completed_tickets
  - Breakdown chart: cost by agent type (Maker, Checker, Reviewer, Approver)
  - Trend: cost over time (last 90 days)
  - Benchmark: compare to industry average (optional)
  - Audit log: `cost_analysis.viewed`
- **Story Points**: 8
- **Priority**: P2
- **Depends On**: SaaS-7, SaaS-14
- **Blocks**: None

---

### Epic 5: Compliance & Audit
**Description**: Compliance dashboards, report generation, framework checklists (SOC2, ISO, DPDP).

**User Stories**:

**SaaS-17**: Compliance admin can generate SOC2 Type II compliance report
- **Acceptance Criteria**:
  - Compliance page: "Generate SOC2 report" button
  - Report includes:
    - Audit log summary (events last 30d, user actions)
    - Access control matrix (who has what role)
    - Change log (all infrastructure changes)
    - Incident log (if any security events)
    - Data encryption status
  - PDF export + archive (store in compliance_reports table)
  - Signed by: org admin (digital signature or attestation)
  - Email: send to compliance officer
  - Audit log: `compliance_report.generated` + `compliance_report.exported`
- **Story Points**: 13
- **Priority**: P1
- **Depends On**: SaaS-15
- **Blocks**: None

**SaaS-18**: Compliance dashboard shows framework checklists (SOC2, ISO, DPDP)
- **Acceptance Criteria**:
  - Dashboard: tabs for SOC2, ISO27001, DPDP Act (India)
  - Each framework shows checklist: item, status (✅/⚠️/❌), evidence (audit log count, config check)
  - SOC2 items: "Audit logging enabled", "MFA enforced", "Data encrypted", "Access controls", "Incident response plan"
  - ISO items: "Asset inventory", "Access control", "Cryptography", "Vendor management", "Incident management"
  - DPDP items: "Consent mechanism", "Data subject rights", "Data minimization", "Breach notification", "DPA execution"
  - Auto-checks: system scans config + audit logs, sets status
  - Manual items: marked for review (admin checklist)
  - Status summary: "SOC2: 4/5 ready (80%)"
  - Audit log: `compliance_checklist.viewed`
- **Story Points**: 13
- **Priority**: P2 (Phase 3)
- **Depends On**: SaaS-15
- **Blocks**: None

**SaaS-19**: System logs all audit events immutably (append-only)
- **Acceptance Criteria**:
  - Audit log schema: id (auto-increment), org_id, actor_id, action, resource, changes (JSON), timestamp, IP, user_agent
  - Events logged: user.invited, user.removed, subscription.upgraded, workspace.created, api_key.created, approval.granted
  - Immutable: no UPDATE/DELETE allowed (only INSERT)
  - Partitioned by month (time-range partitioning) for performance
  - Indexed: org_id, actor_id, created_at, action
  - Retention policy: 30d (Starter), 1y (Professional), 7y (Enterprise) via scheduled cleanup
  - Encryption: sensitive data (email, changes) encrypted at rest
  - Audit log: (this IS the audit log system)
- **Story Points**: 13
- **Priority**: P0
- **Depends On**: SaaS-1
- **Blocks**: SaaS-15, SaaS-17

---

### Epic 6: Settings & Configuration
**Description**: Organization profile, member management, webhook integrations, API config.

**User Stories**:

**SaaS-20**: Org admin can update organization profile
- **Acceptance Criteria**:
  - Settings page: name, description, billing contact email, region (us-east-1/eu-west-1/ap-south-1)
  - Region selection: affects data residency (Postgres replica location)
  - Logo upload: display on dashboard + workspace list
  - Contact info: used for billing emails + support tickets
  - Audit log: `org.updated` (with diff of changes)
- **Story Points**: 5
- **Priority**: P1
- **Depends On**: SaaS-1
- **Blocks**: None

**SaaS-21**: Org admin can configure GitHub/JIRA webhooks
- **Acceptance Criteria**:
  - Settings → "Integrations" tab
  - GitHub: input repo URL + auth token (GitHub App) → enable auto-sync of PRs to workspace
  - JIRA: input Jira URL + API token → enable ticket creation from agent workflows
  - Test button: verify connection (logs to audit trail)
  - Webhook events: PR opened/closed → sync to workspace, ticket created → trigger agent
  - Status: last webhook received, next scheduled sync
  - Audit log: `integration.configured`, `integration.tested`, `webhook.received`
- **Story Points**: 13
- **Priority**: P2
- **Depends On**: SaaS-1
- **Blocks**: None

**SaaS-22**: Org can customize MCRA approval workflows (Enterprise)
- **Acceptance Criteria**:
  - Workflow builder: drag-drop gates (Maker → Checker → Reviewer → Approver → Custom)
  - Customizations: add approval step (e.g., "Security Review" before Approver)
  - Gate rules: e.g., "Security Review requires CISO approval if changes in /security/"
  - Assignees: per gate, assign to role or specific user
  - Triggers: auto-route by ticket type (P0 always → Approver, P3 → Reviewer only)
  - Test: dry-run workflow with mock ticket
  - Audit log: `workflow_config.updated`
- **Story Points**: 21
- **Priority**: P3 (Phase 4)
- **Depends On**: SaaS-9
- **Blocks**: None

---

## Backlog Prioritization

### P0 (Critical for Beta, Weeks 1–2)
1. SaaS-1: Sign-up + org creation
2. SaaS-5: Stripe integration + tier upgrade
3. SaaS-7: Usage metering
4. SaaS-19: Immutable audit logs
5. SaaS-15: Audit log viewer
6. SaaS-9: RBAC enforcement
7. SaaS-4: Workspaces
8. SaaS-2: Invite members
9. SaaS-13: Dashboard metrics
10. SaaS-14: Workflow status dashboard

**Effort**: 70 story points (~3 weeks, 2 backend + 2 frontend)

### P1 (Important for GA, Weeks 3–4)
1. SaaS-3: Manage members
2. SaaS-6: Cancel subscription
3. SaaS-8: Invoices + PDFs
4. SaaS-17: SOC2 report generation
5. SaaS-20: Org profile settings

**Effort**: 36 story points (~1.5 weeks)

### P2 (Phase 2, Weeks 5–8)
1. SaaS-10: MFA
2. SaaS-12: API keys
3. SaaS-18: Compliance checklists
4. SaaS-16: Cost per ticket
5. SaaS-21: GitHub/JIRA webhooks
6. SaaS-11: SSO (SAML/OIDC)

**Effort**: 65 story points (~3 weeks)

### P3 (Phase 4, Roadmap)
1. SaaS-22: Custom workflows

**Effort**: 21 story points

---

## JIRA Tickets

### P0 Tickets

**SaaS-1: User Sign-up & Organization Creation**
- Epic: Organization Management
- Points: 5
- Priority: P0
- Assignee: Backend + Frontend
- Acceptance Criteria:
  - [x] Sign-up form: email, password, org name
  - [x] Creates user + organization
  - [x] Sets creator as Owner role
  - [x] Redirect to onboarding
  - [x] Audit log entry
- Testing: Unit (auth), integration (Postgres), E2E (sign-up flow)
- Dependencies: None

**SaaS-5: Stripe Billing Integration**
- Epic: Billing
- Points: 13
- Priority: P0
- Assignee: Backend (1) + Frontend (1)
- Acceptance Criteria:
  - [x] Stripe account (sandbox mode)
  - [x] Pricing page (Starter/Professional/Enterprise)
  - [x] Checkout integration (Stripe hosted)
  - [x] Webhook handling (payment_succeeded)
  - [x] Update org.tier + subscription table
  - [x] Invoice PDF generation
  - [x] Confirmation email
- Testing: Unit (Stripe API mock), integration (Stripe test mode), E2E (checkout flow)
- Dependencies: SaaS-1

*... (Continue for all 10 P0 tickets)*

---

## Definition of Done

All tickets must satisfy:
- [ ] Code written (TDD: test first)
- [ ] Tests pass (unit + integration + E2E)
- [ ] Coverage ≥ 80%
- [ ] Linting passes (ruff, pyright zero errors)
- [ ] Commit references ticket ID
- [ ] Audit log entries created (if applicable)
- [ ] Documentation updated (API docs, user guide)
- [ ] Manual QA passed (business logic validation)

---

## Validation Gates

**Step 7: Checker** validates:
- [ ] All P0 stories written with acceptance criteria
- [ ] Story points realistic (compare to velocity)
- [ ] No ambiguous stories (acceptance criteria are SMART)
- [ ] Dependencies correctly identified (no circular)
- [ ] Backlog prioritized (P0 → P1 → P2 → P3)

**Step 8: Reviewer** checks:
- [ ] Alignment with BMAD
- [ ] No scope creep (features match budget)
- [ ] Timeline realistic (Weeks 1–4 for P0 feasible?)
- [ ] Risks identified (Stripe integration timing, compliance audit)

**Step 9: Approver** (user) confirms:
- [ ] Specification complete
- [ ] Backlog approved
- [ ] Ready to proceed to /arch stage

---

## Next Steps

1. **Checker Review**: Validate all stories, points, criteria
2. **Reviewer Review**: Align with business goals, timeline
3. **Approver Approval** (user): Confirm ready for /arch
4. **Proceed to `/arch`**: Detailed design, ADRs, API specs, ER diagrams

---

**Document Version**: 1.0  
**Created**: 2026-04-19  
**Status**: Awaiting Checker + Reviewer validation
