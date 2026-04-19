# ProjectZero SaaS Architecture Design

**Status**: Design for Review (Path B)  
**Date**: 2026-04-19  
**Audience**: Product leadership, engineering leads, stakeholders

---

## 1. Product Vision

**ProjectZero as SaaS**: Governed AI-powered product development platform for enterprises and teams.

**Positioning**: Multi-tenant, modular platform that enables organizations to build, govern, and scale AI-driven products with automated testing, compliance, and deployment gates.

**Value Props**:
- Autonomous agent-driven development (RED → GREEN → REFACTOR → Commit in single workflow)
- Enterprise governance built-in (RBAC, audit logs, compliance frameworks)
- Multi-tenant isolation (data + compute)
- Temporal-backed orchestration for long-running workflows
- Persistent AI brain (memories, decisions, patterns) across teams + products

---

## 2. Tier Strategy

### Tier 1: Starter (Self-Serve)
- Single tenant (personal/small team)
- Up to 5 users
- 1 product repo
- Basic agent workflows (Maker only, no Checker gate)
- Community support
- $0–$99/month

### Tier 2: Professional (SMB)
- Multi-tenant (3–50 users per org)
- Up to 10 product repos
- Full MCRA workflow (Maker → Checker → Reviewer → Approver)
- 80% coverage enforcement, lint/type gates
- Email support
- RBAC (3 roles: Admin, Engineer, Reviewer)
- Basic audit logs
- $499/month

### Tier 3: Enterprise (B2B)
- Multi-tenant (unlimited users)
- Unlimited repos
- Full MCRA + custom approval workflows
- SSO (SAML/OIDC)
- Advanced RBAC (custom roles)
- Compliance dashboards (SOC2, ISO27001, DPDP)
- Geo-redundancy + DR
- Dedicated support + SLA
- Custom integrations (JIRA, GitHub, Slack)
- $4,999+/month (custom)

---

## 3. Key Features by Tier

| Feature | Starter | Professional | Enterprise |
|---------|---------|--------------|-----------|
| Tenant Isolation | Single | Multi | Multi (Geo) |
| Users | 5 | 50 | Unlimited |
| Repos | 1 | 10 | Unlimited |
| Agent Workflows | Maker (auto) | MCRA (4-gate) | MCRA + Custom |
| Coverage Gate | No | 80% min | 80% + Custom % |
| Audit Logs | 30 days | 1 year | 7 years |
| SSO | No | No | Yes |
| RBAC | Basic (3) | Basic (3) | Advanced (Custom) |
| Compliance | None | Basic | SOC2/ISO/DPDP |
| Support | Community | Email | Dedicated SLA |
| SLA | Best effort | 99.5% | 99.99% |

---

## 4. System Architecture

### Current Stack (Inherited)
```
┌─────────────────────┐
│   React UI          │ (Control Tower + Dashboard)
│ (React + TypeScript)│
└──────────┬──────────┘
           │ HTTPS
           ▼
┌─────────────────────┐
│   FastAPI Backend   │ (REST API + GraphQL)
│ (Python + Pydantic) │
└──────────┬──────────┘
           │
     ┌─────┴─────┬──────────┐
     ▼           ▼          ▼
  ┌────────┐ ┌────────┐ ┌────────────┐
  │Postgres│ │ Brain  │ │ Temporal   │
  │(State) │ │(Memory)│ │ (Workflow) │
  └────────┘ └────────┘ └─────┬──────┘
                               │
                               ▼
                        ┌──────────────┐
                        │ Claude Agents│
                        └──────────────┘
```

### New SaaS Additions
```
┌────────────────────────────────┐
│  Stripe Billing Engine         │ (Subscriptions + Invoicing)
└────────────────────────────────┘
           │
           ▼
┌────────────────────────────────┐
│  Postgres (Extended Schema)    │
│  - billing_subscriptions       │
│  - billing_usage               │
│  - org_quotas                  │
│  - audit_logs (7-year)         │
│  - compliance_reports          │
│  - audit_trail (immutable)     │
└────────────────────────────────┘

┌────────────────────────────────┐
│  Redis Cache Layer             │ (Rate limiting, session cache)
└────────────────────────────────┘

┌────────────────────────────────┐
│  Auth Layer (Auth0/Keycloak)   │
│  - SSO (SAML/OIDC)             │
│  - MFA                         │
│  - Session mgmt                │
└────────────────────────────────┘

┌────────────────────────────────┐
│  Analytics Pipeline            │ (Event streaming → Data warehouse)
│  (Kafka/Firehose → BigQuery)   │
└────────────────────────────────┘
```

---

## 5. Data Model Changes

### New Tables (Postgres)

**Organizations** (Tenant root)
```sql
CREATE TABLE organizations (
  id UUID PRIMARY KEY,
  name VARCHAR(255),
  tier VARCHAR(50), -- starter, professional, enterprise
  created_at TIMESTAMP,
  updated_at TIMESTAMP,
  billing_contact_email VARCHAR(255),
  region VARCHAR(50) -- us-east-1, eu-west-1, ap-south-1
);
```

**Billing Subscriptions**
```sql
CREATE TABLE billing_subscriptions (
  id UUID PRIMARY KEY,
  org_id UUID REFERENCES organizations(id),
  stripe_subscription_id VARCHAR(255),
  tier VARCHAR(50),
  status VARCHAR(50), -- active, past_due, canceled, paused
  current_period_start DATE,
  current_period_end DATE,
  created_at TIMESTAMP,
  updated_at TIMESTAMP,
  UNIQUE(org_id)
);
```

**Audit Logs** (Immutable, tenant-scoped)
```sql
CREATE TABLE audit_logs (
  id BIGSERIAL PRIMARY KEY,
  org_id UUID REFERENCES organizations(id),
  actor_id UUID REFERENCES users(id),
  resource_type VARCHAR(100),
  resource_id UUID,
  action VARCHAR(100), -- CREATE, UPDATE, DELETE, APPROVE
  changes JSONB,
  ip_address INET,
  user_agent TEXT,
  created_at TIMESTAMP,
  INDEX audit_logs_org_created (org_id, created_at DESC)
) PARTITION BY RANGE (created_at);
```

**Usage Tracking** (For metering)
```sql
CREATE TABLE billing_usage (
  id UUID PRIMARY KEY,
  org_id UUID REFERENCES organizations(id),
  metric_name VARCHAR(100), -- agents_runs, tickets_created, repos
  value NUMERIC,
  period_start DATE,
  period_end DATE,
  created_at TIMESTAMP
);
```

**Compliance Reports** (Audit-ready)
```sql
CREATE TABLE compliance_reports (
  id UUID PRIMARY KEY,
  org_id UUID REFERENCES organizations(id),
  framework VARCHAR(50), -- soc2, iso27001, dpdp
  generated_at TIMESTAMP,
  signed_by UUID REFERENCES users(id),
  report_json JSONB,
  archived BOOLEAN DEFAULT FALSE
);
```

---

## 6. API Design (SaaS Endpoints)

### Organization Management
```
POST   /api/v1/organizations              Create org
GET    /api/v1/organizations              List orgs (current user)
GET    /api/v1/organizations/{org_id}     Get org
PATCH  /api/v1/organizations/{org_id}     Update org
DELETE /api/v1/organizations/{org_id}     Delete org (Enterprise only)
```

### Billing & Subscriptions
```
GET    /api/v1/billing/subscription       Current subscription
POST   /api/v1/billing/upgrade            Upgrade tier
POST   /api/v1/billing/cancel             Cancel subscription
GET    /api/v1/billing/invoices           List invoices
GET    /api/v1/billing/usage              Current month usage
```

### User & Access Control
```
POST   /api/v1/organizations/{org_id}/members              Invite user
GET    /api/v1/organizations/{org_id}/members              List members
PATCH  /api/v1/organizations/{org_id}/members/{user_id}    Update role
DELETE /api/v1/organizations/{org_id}/members/{user_id}    Remove member
```

### Audit & Compliance
```
GET    /api/v1/organizations/{org_id}/audit-logs          List audit logs (paginated)
POST   /api/v1/organizations/{org_id}/compliance/report   Generate SOC2/ISO report
GET    /api/v1/organizations/{org_id}/compliance/status   Compliance checklist
```

### Workspace Management (Per-Org)
```
POST   /api/v1/organizations/{org_id}/workspaces           Create workspace (repo)
GET    /api/v1/organizations/{org_id}/workspaces           List workspaces
DELETE /api/v1/organizations/{org_id}/workspaces/{ws_id}   Delete workspace
```

---

## 7. Frontend Architecture (SaaS UI)

### New Pages

**Dashboard** (`/dashboard`)
- Org overview: users, repos, active workflows, storage usage
- Quick stats: agents runs MTD, coverage trend, failed gates
- Billing summary: current tier, next billing date, usage vs quota

**Billing Portal** (`/billing`)
- Current subscription details
- Usage metrics (agents runs, repos created, users invited)
- Upgrade/downgrade tier workflow
- Payment method management (Stripe integration)
- Invoice history + download

**Settings** (`/settings`)
- Organization profile (name, region, billing contact)
- Members management (invite, role assign, remove)
- SSO/OIDC configuration (Enterprise only)
- Custom webhooks (GitHub, JIRA, Slack)
- API keys for programmatic access

**Compliance & Audit** (`/compliance`)
- Audit log viewer (filters by action, actor, resource)
- Compliance dashboard (SOC2/ISO/DPDP checklist + status)
- Report generator + archive
- Data export (for auditors)

**Agent Control Panel** (Org-level) (`/agents`)
- Agent fleet health (11-agent team for P0 ticket)
- Workflow status (Maker → Checker → Reviewer → Approver)
- Cost per ticket (time × agent cost model)
- Logs + error replay

---

## 8. Auth & Security

### Identity Layer
- **Starter/Professional**: Auth0 + email/password
- **Enterprise**: Auth0 + SAML/OIDC SSO

### Authorization (RBAC)
```
Starter:
  - Owner (org admin)
  - Member (read-only)

Professional:
  - Owner (org admin, billing)
  - Engineer (create/edit tickets, invoke agents)
  - Reviewer (approve gates)

Enterprise:
  - Custom roles (define permissions per resource)
  - Attribute-based access (team-scoped access)
```

### Tenant Isolation
- Row-level security (RLS) on Postgres
- org_id on all tables (foreign key constraint)
- Redis namespacing by org_id
- Temporal namespace isolation (one namespace per org)
- Audit trail immutable (prevent backfill)

### Encryption
- TLS 1.3 in transit
- AES-256 at rest (customer data)
- Customer-managed keys (CMK) for Enterprise
- Secrets stored in HashiCorp Vault

---

## 9. Billing & Usage Metering

### Pricing Model (Per-Org)

**Starter**: Flat $0–$99/month
- Up to 5 users
- 1 repo
- No additional metering

**Professional**: $499/month + overage
- 50 users included
- 10 repos included
- Overages: $50/extra user/month, $100/extra repo/month
- Agent runs: 1000 runs/month included, then $0.10/run

**Enterprise**: Custom (volume discount)
- Unlimited users/repos
- Agent runs metered at $0.05/run
- Data storage: first 1TB included, then $0.10/GB/month

### Metering Events
- `agent_run_complete` → increment billing_usage
- `user_invited` → track active users
- `repo_created` → track repos
- `storage_used` → track data volume

---

## 10. Deployment & Scaling

### Multi-Region Strategy

**Starter/Professional**:
- Single region (us-east-1)
- RTO 4h, RPO 1h (backup to S3)

**Enterprise**:
- Multi-region (us-east-1 primary, eu-west-1 secondary, ap-south-1 optional)
- Active-active failover (DNS routing)
- RTO 15m, RPO 5m (continuous replication)
- Geo-distributed Postgres replicas
- Geo-distributed Redis (cache invalidation)

### Scaling Patterns

**Database**: PostgreSQL with read replicas per region
**Cache**: Redis cluster (sharded by org_id)
**Temporal**: Dedicated namespace per org (Enterprise) or shared with rate limiting (Starter/Prof)
**API**: Horizontal scaling (Kubernetes or ECS)
**Agents**: Dedicated worker pool per org (Enterprise) or shared pool (Starter/Prof)

### Monitoring & Observability
- Prometheus + Grafana (metrics)
- ELK Stack (logs + audit trails)
- Jaeger (distributed tracing)
- Sentry (error tracking)
- CloudWatch alarms (AWS native)

---

## 11. Go-to-Market Roadmap

### Phase 1: Beta Launch (Week 1–4)
- **Target**: 10 professional orgs
- **Features**: Full Starter + Professional tiers, billing integration (Stripe test)
- **Work**: 4–5 sprint iterations (~4 weeks)

### Phase 2: GA Launch (Week 5–8)
- **Target**: 50 paying customers
- **Features**: Starter GA, Professional GA, enterprise landing page
- **Work**: Bug fixes, security audit, compliance docs

### Phase 3: Enterprise Tier (Week 9–16)
- **Target**: 3–5 enterprise contracts
- **Features**: SSO, advanced RBAC, compliance dashboards, dedicated support
- **Work**: ~8 weeks (concurrent with Phase 2 customer success)

---

## 12. Success Metrics

| Metric | Target (Month 6) | Target (Month 12) |
|--------|------------------|-------------------|
| Signups | 500 | 5,000 |
| Paying Customers | 50 | 500 |
| MRR | $25K | $250K |
| Churn Rate | <5% | <3% |
| NPS | >40 | >50 |
| Uptime SLA | 99.5% | 99.95% |

---

## 13. Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Competitive pressure (GitHub Copilot, Vercel AI) | High | Focus on governance + compliance niche |
| Customer acquisition cost | Medium | Freemium model (Starter) → viral loop |
| Churn (low product-market fit) | High | Early customer research + NPS tracking |
| Compliance audit failure (SOC2) | Critical | Hire compliance officer, external audit Q2 |
| Data breach | Critical | Penetration testing, bug bounty program |
| Postgres scaling bottleneck | Medium | Sharding by org_id, read replicas, Citus extension |

---

## 14. Team & Capacity

### Required for SaaS Build

| Role | Count | Effort |
|------|-------|--------|
| Backend Engineer (Python/FastAPI) | 2 | Design API, billing, auth |
| Frontend Engineer (React/TS) | 2 | UI for dashboard, billing portal, settings |
| DevOps/SRE | 1 | Kubernetes, multi-region, monitoring |
| Product Manager | 1 | Roadmap, prioritization, GTM |
| Compliance/Security | 1 | SOC2, ISO, DPDP, OWASP ZAP |

**Total**: 7 FTE, ~4–6 month timeline to GA

---

## 15. Dependencies & Blockers

- **Stripe Integration**: Must start Week 1 (takes 2–3 weeks sandbox → production)
- **Auth0/Keycloak Setup**: Configure SSO templates (1 week)
- **Postgres Schema Migration**: Extend schema without downtime (1–2 weeks, careful rollout)
- **Compliance Audit**: External SOC2 audit (2–3 months, start Month 3)
- **GitHub/JIRA Webhooks**: Two-way sync (already partially done, needs SaaS multitenancy)

---

## 16. Next Steps (Post-Review)

If approved:
1. **Week 1**: Run `/spec` → generate JIRA tickets for each feature (SaaS-1 through SaaS-50)
2. **Week 2**: Run `/arch` → detailed ADRs, API specs, data model ER diagrams
3. **Week 3+**: Run `/implement` → TDD cycle, 80% coverage, quality gates

**Questions for Review**:
- Tier pricing: competitive? Revenue model viable?
- Multi-region strategy: necessary or MVP is single-region?
- Timeline: 4–6 months realistic given team size?
- Feature priority: which features critical for beta?
- Compliance: SOC2 or skip for beta?

---

**Document Version**: 1.0  
**Last Updated**: 2026-04-19  
**Author**: Claude (Architecture Design)  
**Status**: Awaiting Review
