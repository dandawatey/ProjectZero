# Enterprise Multi-Tenant/Multi-DB/Multi-Geo Gaps — Tickets PRJ0-98 through PRJ0-109

Meta-ticket tracks all 12 gaps required to transform ProjectZeroFactory from startup-grade to enterprise-grade.

---

## PRJ0-98: Tenant Isolation Framework (RLS + Audit Logs)

**Priority**: P0 (CRITICAL)  
**Status**: To Do  
**Story Points**: 21  
**Epic**: Enterprise Multi-Tenancy  
**Assigned**: Architect, Backend Engineer  

### Description
Implement row-level security (RLS) in Postgres and tenant context injection throughout API. Every request routes tenant_id via JWT claims → middleware → query filters. Audit logger records all data access: who, what, when, where, which-tenant, from-which-IP.

### Acceptance Criteria
- [ ] Postgres RLS policies enforce per-tenant row access (SELECT/INSERT/UPDATE/DELETE)
- [ ] Middleware injects `tenant_id` from JWT claims into request context
- [ ] All queries auto-filtered by `tenant_id` (no manual filters required)
- [ ] Audit log table (immutable, append-only) records: user_id, tenant_id, action, resource, timestamp, IP, user_agent
- [ ] Audit logs queryable via REST API (paginated, with filters)
- [ ] TDD: 80%+ coverage. Integration tests verify RLS blocks cross-tenant access
- [ ] Linting + type checks pass
- [ ] Commit message references PRJ0-98

### SPARC Phases

**Specification**: Write spec doc: tenant isolation model, RLS enforcement, audit log schema, cross-tenant test strategy

**Pseudocode**: Design middleware logic (extract tenant_id from JWT → set context), RLS policy pseudo-SQL, audit log write logic

**Architecture**: Finalize RLS policies per table, audit log indexes, middleware placement, error handling

**Refinement**: Implement RLS + middleware + audit logger (TDD: write tests, implement, refactor)

**Completion**: PR review, security review, audit log verification, merge, deploy

### Definition of Done
Tests pass, coverage ≥80%, linting/types clean, matches acceptance criteria, security sign-off, committed with ticket ref.

---

## PRJ0-99: Multi-DB Routing & Sharding Strategy

**Priority**: P0 (CRITICAL)  
**Status**: To Do  
**Story Points**: 21  
**Epic**: Enterprise Multi-Tenancy  
**Assigned**: Architect, Data Engineer  

### Description
Design and implement shard key selection (tenant_id), connection routing logic, and regional database endpoints. Supports single DB with schema-based sharding (initial) or separate DB per tenant (future). Includes connection pooling (PgBouncer config), write routing to primary, read routing to replicas.

### Acceptance Criteria
- [ ] Shard key defined: `tenant_id` (no cross-tenant queries)
- [ ] DB routing layer abstracts shard selection (can swap schema → DB routing later)
- [ ] PgBouncer config for connection pooling documented
- [ ] Regional endpoints configured (US DB, EU DB, APAC DB in separate regions)
- [ ] Data residency enforced: EU tenants → EU DB only
- [ ] Read replicas support (replica lag ≤5s tested)
- [ ] Migration strategy documented (how to shard existing single DB)
- [ ] TDD: routing unit tests + integration tests (3+ shards, verify isolation)
- [ ] Linting + type checks pass
- [ ] Commit message references PRJ0-99

### SPARC Phases

**Specification**: Write spec: shard key rationale, partition strategy, data residency rules, migration plan, cross-shard query handling

**Pseudocode**: Design tenant → shard mapping algorithm, connection pooling logic, failover detection

**Architecture**: Finalize shard count, PgBouncer config, read replica strategy, cross-shard query prevention

**Refinement**: Implement sharding layer (routing, pooling, replication), TDD for cross-shard isolation

**Completion**: PR review, data residency audit, integration test sign-off, merge, deploy

### Definition of Done
Tests pass, coverage ≥80%, linting/types clean, data residency verified, matches acceptance criteria, committed with ticket ref.

---

## PRJ0-100: Encryption + Secrets Management

**Priority**: P0 (CRITICAL)  
**Status**: To Do  
**Story Points**: 18  
**Epic**: Enterprise Security  
**Assigned**: Security Reviewer, Backend Engineer  

### Description
Implement field-level encryption (PII, passwords, API keys), encryption key rotation, and HSM/KMS integration. Sensitive fields encrypted at rest using pgcrypto. TDE (transparent data encryption) enabled on all DBs. Secrets stored in AWS KMS / Google Cloud KMS, rotated every 90 days. Encryption keys never logged or cached insecurely.

### Acceptance Criteria
- [ ] PII fields (email, phone, SSN) encrypted via pgcrypto in Postgres
- [ ] API key encryption implemented (hash for index, encrypted full key stored)
- [ ] Password hashing uses Argon2 (never plaintext)
- [ ] HSM/KMS integration configured (AWS KMS selected for US, Google KMS for EU)
- [ ] Key rotation strategy defined and tested (90-day rotation)
- [ ] TDE enabled on all Postgres instances
- [ ] Encryption keys never appear in logs (sanitizer function for logging)
- [ ] Backup encryption enabled (encrypted backups only)
- [ ] TDD: 80%+ coverage. Tests verify encrypted fields cannot be queried unencrypted
- [ ] Security review pass (Security Reviewer sign-off)
- [ ] Linting + type checks pass
- [ ] Commit message references PRJ0-100

### SPARC Phases

**Specification**: Write spec: field encryption map, key rotation schedule, HSM/KMS selection, backup encryption, secret storage, log sanitization rules

**Pseudocode**: Design encryption/decryption middleware, key rotation worker, log sanitizer regex patterns

**Architecture**: Finalize HSM/KMS vendor, key hierarchy, encryption algorithm (AES-256), Argon2 config

**Refinement**: Implement field-level encryption (TDD: encrypt/decrypt tests), key rotation worker, backup encryption, log sanitizer

**Completion**: PR review, security review, encryption verification test, merge, deploy

### Definition of Done
Tests pass, coverage ≥80%, security review approved, linting/types clean, matches acceptance criteria, committed with ticket ref.

---

## PRJ0-101: Compliance Scaffolding (ISO 27001, SOC2, HIPAA, DPDP)

**Priority**: P1 (HIGH)  
**Status**: To Do  
**Story Points**: 13  
**Epic**: Enterprise Compliance  
**Assigned**: ISO Documentation Agent, Approver  

### Description
Generate compliance documentation framework: ISO 27001 Statement of Applicability (SoA), SOC2 Trust Service Criteria mapping, HIPAA Business Associate Agreement (BAA) checklist, HITECH Security Rule checklist. Link each requirement to implementation tickets. Auto-generate audit readiness report (pct compliant per control).

### Acceptance Criteria
- [ ] ISO 27001 Annex A (14 controls) mapped to factory components
- [ ] Statement of Applicability (SoA) document generated with control status
- [ ] SOC2 Trust Service Criteria (CC, PT, OE sections) mapped to controls
- [ ] HIPAA Security Rule (Admin, Physical, Technical) checklist with remediation links
- [ ] HITECH Breach Notification Rule checklist
- [ ] **DPDP Act (India) compliance checklist**: Consent, consent manager, data subject rights, purpose limitation, storage limitation, cross-border transfer rules
- [ ] DPDP consent management: opt-in consent required before data processing
- [ ] DPDP right-to-access: user can request personal data copy
- [ ] DPDP right-to-deletion: user can request all data deleted (except legal hold)
- [ ] DPDP data retention: delete data after purpose fulfilled + consent withdrawn
- [ ] DPDP cross-border transfer: India → overseas requires explicit consent + prescribed countries only
- [ ] Each control linked to 1+ implementation tickets (e.g., Encryption → PRJ0-100)
- [ ] Audit readiness dashboard shows pct compliant per category
- [ ] Confluence pages auto-generated and updated daily
- [ ] Gap remediation backlog prioritized by risk
- [ ] Commit message references PRJ0-101

### SPARC Phases

**Specification**: Write spec: ISO 27001 control map, SOC2 criteria alignment, HIPAA requirements, DPDP Act requirements (consent, rights, transfers), gap remediation approach

**Pseudocode**: Design consent manager (opt-in logic), data subject rights fulfillment (export, delete), cross-border transfer check

**Architecture**: Finalize control mapping, consent DB schema, audit readiness dashboard architecture

**Refinement**: Implement consent manager, rights fulfillment API, Confluence automation, gap backlog generation

**Completion**: PR review, Approver sign-off, readiness audit, merge, deploy

### Definition of Done
All frameworks mapped, consent manager live, readiness dashboard ≥80% compliant, Approver signed off, committed with ticket ref.

---

## PRJ0-102: Multi-Geography & Regional Failover

**Priority**: P1 (HIGH)  
**Status**: To Do  
**Story Points**: 21  
**Epic**: Enterprise Reliability  
**Assigned**: Architect, DevOps Engineer  

### Description
Deploy app + DB + cache to 3 regions (US-East, EU-West, APAC-Singapore). Global load balancer routes requests by geo IP. DNS failover to standby region on primary outage. Regional RTO ≤5min, RPO ≤1min. Latency test verifies <200ms p99 per region.

### Acceptance Criteria
- [ ] K8s clusters deployed to 3 regions (US, EU, APAC)
- [ ] Global load balancer (Route53 or Cloudflare) routes by geo IP
- [ ] DNS failover policy defined: if primary region unavailable, traffic → secondary (tested)
- [ ] Postgres multi-master or primary-replica setup per region (write to local, read from replica)
- [ ] Redis cache deployed per region (avoid cross-region cache hits)
- [ ] RTO ≤5min tested (failover drill)
- [ ] RPO ≤1min tested (point-in-time recovery)
- [ ] Latency test: p99 <200ms per region (synthetic checks every 5min)
- [ ] Failover runbook documented (manual + auto failover steps)
- [ ] TDD: integration tests verify region isolation, failover success
- [ ] Linting + type checks pass
- [ ] Commit message references PRJ0-102

### SPARC Phases

**Specification**: Write spec: 3-region architecture, global load balancer config, failover policy, RTO/RPO targets, latency SLA

**Pseudocode**: Design geo-routing logic (IP → region), DNS failover decision tree, replica sync algorithm

**Architecture**: Finalize load balancer (Route53 vs Cloudflare), DB replication strategy (primary-replica per region), cache regionalization

**Refinement**: Implement load balancer config, DNS failover, replica sync, latency monitoring, failover runbook

**Completion**: PR review, failover drill, latency verification, merge, deploy

### Definition of Done
3 regions live, RTO ≤5min verified, RPO ≤1min verified, latency <200ms p99 verified, runbook complete, committed with ticket ref.

---

## PRJ0-103: Audit & Immutable Logs (Append-Only, Signed)

**Priority**: P1 (HIGH)  
**Status**: To Do  
**Story Points**: 13  
**Epic**: Enterprise Compliance  
**Assigned**: QA Engineer, Backend Engineer  

### Description
Create immutable audit log table (no DELETE/TRUNCATE). Log integrity verified via HMAC signatures. All audit events include: who (user_id), what (action), when (timestamp), where (resource), why (reason), which-region. Logs queryable but not modifiable. Log retention: 7 years per HIPAA.

### Acceptance Criteria
- [ ] Audit log table schema: id, user_id, action, resource_id, resource_type, reason, timestamp, ip_address, user_agent, region, hmac_signature
- [ ] RLS policy on audit logs: users can only see logs for their tenant
- [ ] HMAC signature on every log entry (proves integrity, detects tampering)
- [ ] DELETE and TRUNCATE revoked from all roles except super-admin (super-admin requires explicit approval)
- [ ] Log archival: cold storage after 30 days, immutable lock enabled
- [ ] Log retention policy enforced: 7 years for regulated tenants, 1 year for others
- [ ] Queryable API: filter by user_id, action, resource, date range (no limit on read)
- [ ] Log integrity check endpoint: verify N% of logs haven't been tampered (HMAC validation)
- [ ] TDD: 80%+ coverage. Tests verify logs cannot be deleted/modified, signatures are valid
- [ ] Integration test: audit log created for every sensitive action (login, data access, config change)
- [ ] Linting + type checks pass
- [ ] Commit message references PRJ0-103

### SPARC Phases

**Specification**: Write spec: audit log schema, immutability rules, HMAC signing, retention policy, queryable API design

**Pseudocode**: Design HMAC signing logic, log archival worker, integrity check algorithm, RLS policy for logs

**Architecture**: Finalize log table schema (indexes on user_id, action, timestamp), archival strategy (S3 + immutable lock)

**Refinement**: Implement audit logging (TDD: log creation, integrity check tests), archival worker, queryable API

**Completion**: PR review, integrity verification, archive test, merge, deploy

### Definition of Done
Logs immutable, HMAC signatures verified, archives created, RLS enforced, retention policy active, committed with ticket ref.

---

## PRJ0-104: RBAC & Fine-Grained Permission Engine

**Priority**: P2 (MEDIUM)  
**Status**: To Do  
**Story Points**: 18  
**Epic**: Enterprise Governance  
**Assigned**: Architect, Backend Engineer  

### Description
Implement RBAC with permission matrix. Roles: Super-Admin, Tenant-Admin, Compliance-Officer, Data-Analyst, Viewer. Permissions cached (avoid per-request DB queries). Supports delegation (User A approves User B's elevated access). LDAP/AD integration for enterprise SSO.

### Acceptance Criteria
- [ ] RBAC schema: roles, permissions, role_permissions, user_roles tables
- [ ] Roles defined: Super-Admin (all), Tenant-Admin (tenant scope), Compliance-Officer (audit + reports), Data-Analyst (data access), Viewer (read-only)
- [ ] Permission matrix: 50+ permissions (create, read, update, delete, export, audit, approve, configure, etc.)
- [ ] Permission cache (Redis): invalidate on role/permission change
- [ ] Delegation pattern: User A can request elevated permission, Tenant-Admin approves, logged in audit trail
- [ ] LDAP/AD integration: sync groups → roles, auto-provision on first login
- [ ] Multi-level approval: permission requests require 2+ approvers for sensitive permissions
- [ ] TDD: 80%+ coverage. Tests verify unauthorized access blocked, cached permissions expire correctly
- [ ] Integration test: end-to-end delegation workflow (request → approve → grant → revoke)
- [ ] Linting + type checks pass
- [ ] Commit message references PRJ0-104

### SPARC Phases

**Specification**: Write spec: RBAC role hierarchy, permission matrix (50+ perms), delegation workflow, LDAP/AD integration, caching strategy

**Pseudocode**: Design permission check middleware, delegation approval workflow, LDAP sync, cache invalidation

**Architecture**: Finalize role/permission schema, delegation approval flow, permission cache (Redis) TTL

**Refinement**: Implement RBAC (TDD: permission check tests), delegation workflow, LDAP sync, cache layer

**Completion**: PR review, RBAC audit, LDAP test, merge, deploy

### Definition of Done
Tests pass, coverage ≥80%, permissions cached, delegation workflow live, LDAP syncing, committed with ticket ref.

---

## PRJ0-105: Data Backup & Disaster Recovery

**Priority**: P2 (MEDIUM)  
**Status**: To Do  
**Story Points**: 16  
**Epic**: Enterprise Reliability  
**Assigned**: DevOps Engineer, SRE Engineer  

### Description
Automated daily backups to 3 regions (redundancy). Point-in-time recovery (PITR) tested weekly. Failover runbook executable in <5min. Backup encryption enabled. RTO/RPO SLAs verified in chaos tests.

### Acceptance Criteria
- [ ] Automated daily backups: full + incremental (WAL archiving)
- [ ] Backup locations: primary region + 2 standby regions (replicated)
- [ ] Backup encryption: enabled, keys in KMS
- [ ] PITR available: restore to any point in last 7 days
- [ ] PITR test: weekly automated test restores random snapshot, verifies data integrity
- [ ] Failover runbook: step-by-step manual failover (if auto-failover fails)
- [ ] RTO ≤5min: measured from incident detection to service restored
- [ ] RPO ≤1min: max data loss 1 minute
- [ ] Chaos test: monthly kill primary DB instance, measure failover time
- [ ] Backup size tracking: daily report of backup storage cost
- [ ] TDD: integration tests verify PITR restores all tables, no data loss
- [ ] Linting + type checks pass
- [ ] Commit message references PRJ0-105

### SPARC Phases

**Specification**: Write spec: backup strategy (full + incremental WAL), 3-region replication, PITR window, RTO/RPO targets, chaos test plan

**Pseudocode**: Design backup worker (schedule, replicate), PITR restore logic, chaos test trigger

**Architecture**: Finalize backup schedule (daily full, hourly incremental), replication targets (3 regions), cold storage lifecycle

**Refinement**: Implement automated backups (TDD: backup creation, PITR test), chaos framework, RTO/RPO validation

**Completion**: PR review, PITR verification, chaos test, merge, deploy

### Definition of Done
Backups automated, PITR weekly-tested, RTO ≤5min verified, RPO ≤1min verified, chaos test passing, committed with ticket ref.

---

## PRJ0-106: Observability & SLO Enforcement

**Priority**: P2 (MEDIUM)  
**Status**: To Do  
**Story Points**: 16  
**Epic**: Enterprise Operations  
**Assigned**: SRE Engineer, DevOps Engineer  

### Description
Define SLOs per region: 99.9% uptime, <200ms p95 latency, <1% error rate. Metrics collected per tenant (usage, cost, performance). Error budget tracking: when error budget exhausted, halt deployments. Auto-generated runbooks from architecture. Alert routing by region + on-call escalation.

### Acceptance Criteria
- [ ] SLOs defined: 99.9% availability (1 month), <200ms p95 latency, <1% error rate
- [ ] Metrics collected: requests/min, latency (p50/p95/p99), error rate, database query time, cache hit rate
- [ ] Per-tenant metrics: tenant-scoped usage, storage consumption, API call count, cost attribution
- [ ] Error budget calculated: (1 - SLO) * total time = allowed downtime/errors
- [ ] Error budget tracking: real-time dashboard shows remaining budget
- [ ] Deployment gate: if error budget < 10%, block non-critical deployments
- [ ] Alert routing: incidents by region, escalate to on-call after 15min
- [ ] Alert suppression: deduplicate alerts within 5min window
- [ ] Runbook generation: auto-generate runbooks from service architecture
- [ ] SLO dashboard: per-region, per-service, historical trends
- [ ] TDD: tests verify metrics are collected, error budget calculations correct
- [ ] Linting + type checks pass
- [ ] Commit message references PRJ0-106

### SPARC Phases

**Specification**: Write spec: SLO targets (99.9% uptime, <200ms p95, <1% error), metrics list, error budget policy, alert routing

**Pseudocode**: Design metric collection (per-tenant, per-region), error budget calculation, deployment gate logic, alert routing

**Architecture**: Finalize metrics backend (Prometheus/Datadog), SLO dashboard schema, alert suppression rules

**Refinement**: Implement metric collection (TDD: metric validation), error budget tracking, deployment gate integration, alert system

**Completion**: PR review, SLO verification, dashboard test, merge, deploy

### Definition of Done
SLOs live, metrics collected, error budget tracking active, deployment gate integrated, alerts configured, committed with ticket ref.

---

## PRJ0-107: Cost Tracking & Chargeback

**Priority**: P2 (MEDIUM)  
**Status**: To Do  
**Story Points**: 13  
**Epic**: Enterprise Operations  
**Assigned**: FinOps Analyst, DevOps Engineer  

### Description
Track infrastructure cost per tenant: compute, storage, API calls, data transfer. Generate monthly cost report. Alert on cost anomalies (>20% month-over-month increase). Implement quotas: storage cap (e.g., 100GB per tenant), API rate limit (e.g., 10K req/min).

### Acceptance Criteria
- [ ] Cost tracking: daily aggregation of cloud spend by tenant
- [ ] Cost categories: compute (K8s), storage (Postgres, S3), API (data transfer), cache (Redis)
- [ ] Per-tenant cost attribution: allocate shared infra costs proportionally
- [ ] Cost report: monthly per-tenant report with breakdown by category
- [ ] Cost anomaly detection: alert if tenant spend >20% vs. previous month
- [ ] Quotas enforced: storage cap, API rate limit, concurrent connection limit
- [ ] Quota enforcement: return 429 (Too Many Requests) when quota exceeded
- [ ] Chargeback: cost data exported to billing system (Stripe/Zuora integration)
- [ ] Cost optimization recommendations: identify unused resources, suggest right-sizing
- [ ] TDD: tests verify cost calculations, quota enforcement works correctly
- [ ] Linting + type checks pass
- [ ] Commit message references PRJ0-107

### SPARC Phases

**Specification**: Write spec: cost categories (compute, storage, API), per-tenant attribution logic, quota policy, chargeback API design

**Pseudocode**: Design cost aggregation job (daily), quota enforcement middleware, anomaly detection algorithm, chargeback export

**Architecture**: Finalize cost DB schema, quota storage, anomaly detection logic (20% threshold), billing system integration

**Refinement**: Implement cost tracking (TDD: cost aggregation tests), quota enforcement, anomaly detection, chargeback export

**Completion**: PR review, cost attribution audit, quota test, merge, deploy

### Definition of Done
Cost tracked daily, quotas enforced, reports generated monthly, anomaly detection active, chargeback export working, committed with ticket ref.

---

## PRJ0-108: Networking & DDoS Protection

**Priority**: P2 (MEDIUM)  
**Status**: To Do  
**Story Points**: 13  
**Epic**: Enterprise Security  
**Assigned**: DevOps Engineer, Security Reviewer  

### Description
Deploy VPC/network isolation per region. Enable WAF (Web Application Firewall) rules: OWASP top 10, rate limiting, bot detection. DDoS mitigation via Cloudflare or AWS Shield Advanced. Private API endpoints for internal-only services. mTLS between services.

### Acceptance Criteria
- [ ] VPC isolation: regional VPC, no traffic between regions except via API gateway
- [ ] WAF rules deployed: OWASP core rules, rate limit 10K req/min per IP
- [ ] Bot detection: identify and block bot traffic (User-Agent, behavior analysis)
- [ ] DDoS mitigation: Cloudflare or AWS Shield Advanced enabled
- [ ] DDoS testing: simulate attack, verify mitigation (traffic dropped, app available)
- [ ] Private endpoints: internal services (admin API, analytics) not exposed to public internet
- [ ] mTLS between services: all inter-service calls authenticated via client certs
- [ ] Egress filtering: outbound traffic restricted to approved destinations
- [ ] Security group rules: least privilege (deny all, allow specific ports)
- [ ] WAF logging: all blocked requests logged to audit trail
- [ ] TDD: integration tests verify unauthorized access blocked, legitimate traffic allowed
- [ ] Linting + type checks pass
- [ ] Commit message references PRJ0-108

### SPARC Phases

**Specification**: Write spec: VPC architecture (per-region), WAF rules (OWASP), DDoS mitigation (Cloudflare vs AWS Shield), mTLS strategy, egress filtering policy

**Pseudocode**: Design WAF rule logic, DDoS detection/mitigation algorithm, mTLS cert issuance flow, egress policy matcher

**Architecture**: Finalize WAF rule set (OWASP core), DDoS vendor (Cloudflare vs AWS), mTLS cert infrastructure, security group rules

**Refinement**: Implement WAF rules (TDD: attack blocking tests), DDoS setup, mTLS infrastructure, egress filtering

**Completion**: PR review, DDoS simulation, network audit, merge, deploy

### Definition of Done
WAF deployed, DDoS tested (attack blocked), mTLS live, network isolation verified, egress rules enforced, committed with ticket ref.

---

## PRJ0-109: Compliance Testing Automation

**Priority**: P3 (LOW)  
**Status**: To Do  
**Story Points**: 13  
**Epic**: Enterprise Quality  
**Assigned**: QA Engineer, Security Reviewer, Compliance-Test-Engineer (NEW)  

### Description
Automated compliance test suite: HIPAA password complexity, MFA enforcement, data residency (verify EU data not in US DB), OWASP ZAP security scan, penetration test framework. Tests run on every deploy, block merge if compliance tests fail.

### Acceptance Criteria
- [ ] HIPAA compliance tests: minimum 12-char password, 1+ uppercase, 1+ number, 1+ special char
- [ ] HIPAA MFA enforcement: all users with data access require MFA
- [ ] HIPAA audit log requirements: all data access logged with user, time, resource, IP
- [ ] Data residency test: verify tenant in EU region has no data in US DB (query production)
- [ ] GDPR Right-to-Delete test: verify all tenant data deleted from all regions
- [ ] OWASP ZAP security scan: run on every preview deployment, flag HIGH/CRITICAL vulnerabilities
- [ ] SQL injection test: verify parameterized queries, no string interpolation
- [ ] XSS test: verify input sanitization, CSP headers set correctly
- [ ] CSRF test: verify token validation on state-changing requests
- [ ] Authentication test: verify session expiration, token rotation, logout effectiveness
- [ ] Penetration test framework: automated pentest on staging, report filed as issues
- [ ] Compliance test gate: /check command fails if any compliance tests fail
- [ ] TDD: test coverage 80%+, all test cases documented
- [ ] Linting + type checks pass
- [ ] Commit message references PRJ0-109

### SPARC Phases

**Specification**: Write spec: HIPAA test cases, GDPR test cases, data residency test, OWASP ZAP integration, penetration test framework, compliance test gate

**Pseudocode**: Design HIPAA password strength check, MFA enforcement test, data residency query, OWASP ZAP parser, pentest trigger

**Architecture**: Finalize test framework (pytest), OWASP ZAP config, penetration test vendor, /check gate integration

**Refinement**: Implement compliance tests (TDD: test cases for each standard), OWASP ZAP integration, pentest framework, gate integration

**Completion**: PR review, compliance test execution, gate test, merge, deploy

### Definition of Done
All compliance tests automated, /check gate integrated, tests passing ≥80% coverage, OWASP ZAP scanning, committed with ticket ref.

---

## PRJ0-110: DPDP Act Compliance (India Data Protection)

**Priority**: P1 (HIGH - India operations)  
**Status**: To Do  
**Story Points**: 13  
**Epic**: Enterprise Compliance  
**Assigned**: ISO Documentation Agent, Approver, Backend Engineer  

### Description
Implement DPDP Act (India's data protection law) compliance: consent management, data subject rights (access, deletion, portability), data retention limits, cross-border transfer rules. Required for any India-based tenant or processing Indian citizen data.

### Acceptance Criteria
- [ ] DPDP Act requirements documented: purpose limitation, consent, data subject rights, retention, cross-border transfers
- [ ] Consent manager: opt-in consent required before ANY data processing
- [ ] Consent audit trail: every consent recorded with timestamp, purpose, version accepted
- [ ] Right to access: user can request personal data copy (export)
- [ ] Right to deletion: user can request all data deleted (except legal hold)
- [ ] Right to portability: data exported in machine-readable format
- [ ] Data retention policy: delete data after purpose fulfilled OR consent withdrawn
- [ ] Cross-border transfer rules: India → overseas requires explicit consent + transfer authority list (EU, US, etc.)
- [ ] Child data protection: no processing of data from <18 without parental consent
- [ ] Data processor agreements: third-party data processors (AWS, etc.) have Data Processing Agreements (DPAs)
- [ ] Privacy policy updated: legal review required (not auto-compliant)
- [ ] Data residency option: India-based tenants can choose India-only storage (separate DB)
- [ ] TDD: 80%+ coverage. Tests verify consent blocking, right-to-delete working, cross-border transfers verified
- [ ] Confluence documentation: auto-generate DPDP compliance report
- [ ] Commit message references PRJ0-110

### SPARC Phases

**Specification**: Write spec: DPDP Act requirements (8 principles), consent flow, rights fulfillment, retention rules, cross-border checks

**Pseudocode**: Design consent manager (opt-in logic), rights request workflow (export/delete), cross-border transfer validation, retention worker

**Architecture**: Finalize consent DB schema, privacy policy versioning, DPA management, cross-border transfer whitelist

**Refinement**: Implement consent manager (TDD: consent blocking tests), rights fulfillment API, retention worker, cross-border validation

**Completion**: PR review, legal review, compliance audit, merge, deploy

### Definition of Done
Consent manager live, rights endpoints working, retention policy active, cross-border transfers validated, legal sign-off, committed with ticket ref.

---

## Ticket Dependencies

```
PRJ0-98 (Tenant Isolation)
PRJ0-99 (Multi-DB Routing)
PRJ0-100 (Encryption)
    ↓ (all P0 complete)
PRJ0-101 (Compliance Scaffolding)
PRJ0-102 (Multi-Geography)
PRJ0-103 (Audit Logs)
    ↓ (all P1 complete)
PRJ0-104 (RBAC)
PRJ0-105 (Backup + DR)
PRJ0-106 (Observability)
PRJ0-107 (Cost Tracking)
PRJ0-108 (Networking)
PRJ0-109 (Compliance Testing)
```

P0 → P1 → P2 → P3 (sequential by priority).

---

**Meta-Epic**: Enterprise Multi-Tenant, Multi-DB, Multi-Geography, ISO-Compliant SaaS Platform

**Total Story Points**: 191 (P0: 60, P1: 60, P2: 71) — includes PRJ0-110 DPDP Act

**Expected Timeline**: P0 (6 weeks) + P1 (5 weeks) + P2 (6 weeks) = 17 weeks
