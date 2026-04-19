# ProjectZero SaaS — JIRA Tickets (SPARC + ISO Audit-First Methodology)

**Version**: 1.0  
**Last Updated**: 2026-04-19  
**Compliance Framework**: ISO 27001 + SOC2 Type II + DPDP Act  
**Audit Trail**: All tickets include compliance sign-off gates and traceability matrix  

---

## SPARC Methodology Applied to JIRA

Every ticket follows **SPARC** (Specification → Pseudocode → Architecture → Refinement → Completion):

```
ISSUE TYPE HIERARCHY:
├─ EPIC (Business goal)
│  └─ STORY (User-facing feature)
│     ├─ TASK (S1: Specification)
│     ├─ TASK (S2: Pseudocode)
│     ├─ TASK (S3: Architecture)
│     ├─ TASK (S4: Refinement)
│     └─ TASK (S5: Completion)
└─ SUBTASK (Technical implementation within TASK)
```

Each STORY has 5 sequential tasks. **CANNOT** skip stages. Parent task must be "Done" before next child starts.

---

## Compliance-First Architecture

```
ISO COMPLIANCE LAYERS:
┌────────────────────────────────────────────────────┐
│ User Action                                        │
└──────────────────────┬───────────────────────────┘
                       ↓
┌────────────────────────────────────────────────────┐
│ 🔐 RBAC + AuthN (ISO 27001: A.9.2.1)              │
│    - Who is doing this?                           │
│    - Do they have permission?                     │
│    - Log: user_id + action + timestamp            │
└──────────────────────┬───────────────────────────┘
                       ↓
┌────────────────────────────────────────────────────┐
│ 🔒 Tenant Isolation (ISO 27001: A.13.1.3)         │
│    - Which org owns this data?                    │
│    - RLS query: WHERE org_id = current_org_id    │
│    - No data leakage between tenants              │
└──────────────────────┬───────────────────────────┘
                       ↓
┌────────────────────────────────────────────────────┐
│ 📊 Audit Logging (ISO 27001: A.12.4.1)            │
│    - IMMUTABLE log of ALL changes                 │
│    - What changed? (table, column, old→new)       │
│    - Who + When + Why (context)                   │
│    - Retention: 7 years (configurable by tier)    │
└──────────────────────┬───────────────────────────┘
                       ↓
┌────────────────────────────────────────────────────┐
│ 🛡️  Encryption (ISO 27001: A.10.1.1)              │
│    - In transit: TLS 1.3                          │
│    - At rest: AES-256 (PII columns)               │
│    - Key management: AWS Secrets Manager          │
└──────────────────────┬───────────────────────────┘
                       ↓
┌────────────────────────────────────────────────────┐
│ ✅ Compliance Checks (ISO + SOC2 + DPDP)          │
│    - Data retention policy applied                │
│    - PII purged per schedule                      │
│    - Audit reports generated                      │
│    - Third-party attestations current             │
└────────────────────────────────────────────────────┘
```

**Every ticket must explicitly address each layer.**

---

## EPIC 1: SaaS-ORG-1 (Organization CRUD + RBAC + RLS)

**EPIC Description**:
- Enables multi-tenant isolation at the database level
- Implements RBAC (Owner, Admin, Member, Guest)
- Enforces RLS on all tables
- Immutable audit logs for all org changes
- **Compliance**: ISO 27001 A.9 (Access Control), A.13 (Segregation)

---

### STORY: SaaS-ORG-1.0 — Organization Creation with Audit Trail

**Story Type**: Story  
**Priority**: P0  
**Assignee**: Agent: Backend Specialist  
**Sprint**: Sprint 1 (May 1–7)  
**Story Points**: 21  
**Dependencies**: NONE (foundational)  
**Blocked By**: NONE  
**Blocks**: SaaS-AUTH-2, SaaS-BILL-2, SaaS-ORG-2  

**Description**:
As an admin user, I want to create an organization and automatically become Owner, so that I can manage team access and billing.

**Acceptance Criteria**:
- [ ] POST /api/v1/organizations creates org with unique slug
- [ ] Creator becomes Owner (role = 'owner')
- [ ] Org has default RBAC roles: Owner, Admin, Member, Guest
- [ ] ALL data created has `org_id` FK to organizations table
- [ ] Immutable audit log entry: "Org created by user_id X at timestamp Y"
- [ ] RLS policy: SELECT organizations only WHERE org_id IN (user's orgs)
- [ ] Response includes org_id, slug, created_at, creator_user_id
- [ ] HTTP 201 + Location header
- [ ] Test coverage ≥ 85%
- [ ] **ISO 27001 A.9.2.1**: Role assignment logged + signed off

---

### SPARC Task 1: Specification

**Task Type**: Task  
**Status**: To Do  
**Subtasks**: (none for spec)

**Specification Document** (Markdown in Jira Description):

```
## S1: SPECIFICATION

### Business Requirement
Enable multi-tenant SaaS. Users must be members of exactly one org initially,
but expandable to multiple orgs later. Roles determine permissions.

### User Story
"As Sarah (startup founder), I want to create an org called 'Acme AI'
so that I can invite my team and manage billing."

### Acceptance Criteria
1. POST /organizations with {name, slug, plan_tier}
2. Creator auto-assigned Owner role
3. Org record created in `organizations` table
4. User-org membership created in `user_organizations` table
5. Default 4 roles created: Owner, Admin, Member, Guest
6. Audit log entry: {action: 'org_created', org_id: X, user_id: Y, timestamp: Z}
7. RLS: User sees only their own org's data
8. Response: {org_id, slug, created_at, plan_tier, owner_id}
9. HTTP 201

### Data Model Changes
```
CREATE TABLE organizations (
  id UUID PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  slug VARCHAR(255) UNIQUE NOT NULL,
  plan_tier VARCHAR(50) -- 'starter', 'professional', 'enterprise'
  created_by_user_id UUID NOT NULL REFERENCES users(id),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE user_organizations (
  id UUID PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES users(id),
  org_id UUID NOT NULL REFERENCES organizations(id),
  role VARCHAR(50) NOT NULL -- 'owner', 'admin', 'member', 'guest'
  invited_at TIMESTAMP,
  joined_at TIMESTAMP,
  UNIQUE(user_id, org_id)
);

CREATE TABLE org_roles (
  id UUID PRIMARY KEY,
  org_id UUID NOT NULL REFERENCES organizations(id),
  role_name VARCHAR(50),
  permissions JSONB, -- {can_create_agent, can_invite, etc}
  created_at TIMESTAMP
);

CREATE TABLE audit_logs (
  id UUID PRIMARY KEY,
  org_id UUID NOT NULL REFERENCES organizations(id),
  user_id UUID NOT NULL REFERENCES users(id),
  action VARCHAR(100),
  table_name VARCHAR(100),
  record_id UUID,
  old_values JSONB,
  new_values JSONB,
  change_reason TEXT,
  created_at TIMESTAMP NOT NULL,
  PARTITION BY RANGE (created_at) -- 30/365/2555 days by tier
);
```

### API Contract (OpenAPI)
```yaml
POST /api/v1/organizations:
  requestBody:
    required: true
    content:
      application/json:
        schema:
          type: object
          required: [name, slug]
          properties:
            name:
              type: string
              minLength: 1
              maxLength: 255
            slug:
              type: string
              pattern: '^[a-z0-9-]{3,50}$'
            plan_tier:
              type: string
              enum: [starter, professional, enterprise]
              default: starter
  responses:
    '201':
      description: Organization created
      content:
        application/json:
          schema:
            type: object
            properties:
              org_id:
                type: string
                format: uuid
              name:
                type: string
              slug:
                type: string
              plan_tier:
                type: string
              owner_id:
                type: string
                format: uuid
              created_at:
                type: string
                format: date-time
    '400':
      description: Invalid input (slug already exists, invalid pattern)
    '409':
      description: Slug conflict
```

### Compliance Mapping
| ISO Control | Requirement | Implementation |
|-------------|-------------|-----------------|
| A.9.2.1 | User role assignment | RBAC roles in org_roles table |
| A.13.1.3 | Segregation of duties | Separate org_id per tenant |
| A.12.4.1 | Audit logging | audit_logs table, immutable |
| A.10.1.1 | Encryption of PII | slug + name encrypted at rest |

### Risk Assessment
| Risk | Severity | Mitigation |
|------|----------|-----------|
| Slug collision | MEDIUM | UNIQUE constraint + 409 response |
| Orphaned user-org rows | LOW | FK constraint + cascade delete tests |
| Audit log injection | HIGH | Prepared statements + parameterized queries |
| Privilege escalation | HIGH | RBAC verified before every mutation |

### Questions for Clarification
- [ ] Can user create multiple orgs? (Yes, later; assume 1 org initially)
- [ ] Slug case-sensitive? (No, normalize to lowercase)
- [ ] Max org name length? (255 chars)
- [ ] Audit log retention? (30 days free tier, 1yr pro, 7yr enterprise)
```

**Exit Criteria**: Specification reviewed + approved by [Product PM, Security Officer, Compliance Officer]  
**Sign-Off Required**: 
- [ ] Product Manager: Acceptance criteria clear
- [ ] Security Officer: Risk assessment addressed
- [ ] Compliance Officer: ISO mapping complete
- [ ] Tech Lead: Architecture feasible

---

### SPARC Task 2: Pseudocode

**Task Type**: Task  
**Status**: Blocked (waits for Task 1 Done)

**Pseudocode** (Algorithm Design):

```python
# S2: PSEUDOCODE - Organization Creation Logic

async def create_organization(request: CreateOrgRequest, current_user: User) -> OrgResponse:
    """
    High-level algorithm before actual implementation.
    Documents control flow, error handling, compliance checks.
    """
    
    # Input Validation (OWASP A01)
    validate_slug_format(request.slug)  # pattern: [a-z0-9-]{3,50}
    validate_org_name_length(request.name)  # 1-255 chars
    
    # Authorization Check (ISO A.9.2.1)
    if not current_user.authenticated:
        raise Unauthorized("User must be logged in")
    
    # Idempotency Check (prevent duplicate submissions)
    if slug_exists(request.slug):
        raise Conflict("Slug already exists")
    
    # BEGIN TRANSACTION
    db.begin_transaction()
    
    try:
        # 1. Create Org Record
        org = Organization(
            id=generate_uuid(),
            name=request.name,
            slug=request.slug.lower(),  # Normalize
            plan_tier=request.plan_tier or 'starter',
            created_by_user_id=current_user.id,
            created_at=now(),
            updated_at=now()
        )
        db.insert(org)
        
        # 2. Assign Creator as Owner (RBAC)
        user_org = UserOrganization(
            id=generate_uuid(),
            user_id=current_user.id,
            org_id=org.id,
            role='owner',  # Hardcoded for creator
            joined_at=now()
        )
        db.insert(user_org)
        
        # 3. Create Default Roles (Owner, Admin, Member, Guest)
        default_roles = [
            {role: 'owner', permissions: {can_create_agent, can_invite, can_delete_org, ...}},
            {role: 'admin', permissions: {can_create_agent, can_invite, ...}},
            {role: 'member', permissions: {can_create_agent, ...}},
            {role: 'guest', permissions: {can_view_only, ...}}
        ]
        for role_def in default_roles:
            role = OrgRole(
                id=generate_uuid(),
                org_id=org.id,
                role_name=role_def.role,
                permissions=role_def.permissions,
                created_at=now()
            )
            db.insert(role)
        
        # 4. IMMUTABLE AUDIT LOG (ISO A.12.4.1)
        audit_log = AuditLog(
            id=generate_uuid(),
            org_id=org.id,
            user_id=current_user.id,
            action='org_created',
            table_name='organizations',
            record_id=org.id,
            old_values=None,  # No old values for CREATE
            new_values={
                'id': org.id,
                'name': org.name,
                'slug': org.slug,
                'plan_tier': org.plan_tier,
                'created_by_user_id': org.created_by_user_id
            },
            change_reason='User self-created organization',
            created_at=now()
        )
        db.insert(audit_log)
        
        # 5. Commit Transaction
        db.commit()
        
        # 6. Response
        return OrgResponse(
            org_id=org.id,
            name=org.name,
            slug=org.slug,
            plan_tier=org.plan_tier,
            owner_id=current_user.id,
            created_at=org.created_at
        ), 201  # HTTP 201 Created
        
    except Exception as e:
        db.rollback()
        # Log error (internal, don't expose details)
        log_error(f"Org creation failed: {e}")
        raise InternalServerError("Failed to create organization")

# Error Handling (ISO A.12.3)
@app.exception_handler(Conflict)
def handle_slug_conflict(exc):
    # Log for audit trail
    audit_log_error('org_creation_failed', reason='slug_conflict')
    return JSONResponse(
        status_code=409,
        content={'error': 'Organization slug already exists'}
    )
```

**Exit Criteria**: Pseudocode reviewed + approved by Tech Lead  
**Sign-Off Required**:
- [ ] Tech Lead: Logic sound
- [ ] Security: No vulnerabilities in error handling
- [ ] QA Lead: Edge cases covered

---

### SPARC Task 3: Architecture

**Task Type**: Task  
**Status**: Blocked (waits for Task 2 Done)

**Architecture Design**:

```
ARCHITECTURE: Org Creation Endpoint

LAYERS:

┌─────────────────────────────────────────────────────┐
│ HTTP Layer (FastAPI)                                │
│ POST /api/v1/organizations                          │
│ Headers: Authorization: Bearer {JWT}                │
└────────────────┬────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────────────┐
│ Request Validation Layer                            │
│ • Pydantic model: CreateOrgRequest                  │
│ • Zod schema validation (frontend)                  │
│ • Rate limiting: 10 requests/min per user           │
└────────────────┬────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────────────┐
│ Auth & RBAC Layer (ISO A.9.2.1)                    │
│ • Extract user_id from JWT token                   │
│ • Verify token signature (HS256)                   │
│ • Check token not expired                          │
│ • Verify user is not guest (guests can't create)   │
└────────────────┬────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────────────┐
│ Business Logic Layer                                │
│ • Check slug uniqueness (conflicts = 409)          │
│ • Create org record                                │
│ • Assign creator as Owner                          │
│ • Create default roles                             │
│ • Generate audit log entry                         │
└────────────────┬────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────────────┐
│ Data Access Layer (SQLAlchemy ORM)                  │
│ • INSERT INTO organizations (...)                  │
│ • INSERT INTO user_organizations (...)             │
│ • INSERT INTO org_roles (...)                      │
│ • INSERT INTO audit_logs (...) [IMMUTABLE]         │
│ • Transaction: Begin → Commit/Rollback             │
└────────────────┬────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────────────┐
│ Database Layer (Postgres 15)                        │
│ • RLS Policy: Enable for all tables                │
│ • Encryption: AES-256 for sensitive columns        │
│ • Partitioning: audit_logs by created_at           │
│ • Foreign Keys: Cascade delete tests               │
└────────────────┬────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────────────┐
│ Response Layer                                      │
│ • HTTP 201 Created                                 │
│ • Location: /api/v1/organizations/{org_id}         │
│ • Body: OrgResponse JSON                           │
│ • Headers: X-Request-ID (for tracing)              │
└─────────────────────────────────────────────────────┘


FILE STRUCTURE (Backend):

platform/backend/app/
├── models/
│   ├── organizations.py
│   │   ├── Organization (SQLAlchemy model)
│   │   ├── UserOrganization
│   │   ├── OrgRole
│   │   └── AuditLog
│   └── schemas.py
│       ├── CreateOrgRequest (Pydantic)
│       ├── OrgResponse
│       └── AuditLogEntry
├── routes/
│   └── organizations.py
│       └── @router.post("/organizations")
├── dependencies/
│   └── auth.py
│       └── get_current_user (JWT verification)
├── services/
│   └── org_service.py
│       ├── create_organization()
│       ├── validate_slug()
│       └── create_audit_log()
├── middleware/
│   └── rls_middleware.py
│       └── RLSMiddleware (sets org_id context)
└── main.py
    └── app.include_router(org_routes)


DATABASE SCHEMA:

organizations:
  ├─ id (UUID, PK)
  ├─ name (VARCHAR, indexed)
  ├─ slug (VARCHAR, UNIQUE, indexed)
  ├─ plan_tier (VARCHAR)
  ├─ created_by_user_id (FK users.id)
  ├─ created_at (TIMESTAMP)
  └─ updated_at (TIMESTAMP)

user_organizations:
  ├─ id (UUID, PK)
  ├─ user_id (FK users.id)
  ├─ org_id (FK organizations.id)
  ├─ role (VARCHAR)
  ├─ invited_at (TIMESTAMP)
  └─ joined_at (TIMESTAMP)
  └─ RLS: (user_id, org_id) visible only to members

org_roles:
  ├─ id (UUID, PK)
  ├─ org_id (FK organizations.id)
  ├─ role_name (VARCHAR)
  ├─ permissions (JSONB)
  └─ created_at (TIMESTAMP)

audit_logs:
  ├─ id (UUID, PK)
  ├─ org_id (FK organizations.id)
  ├─ user_id (FK users.id)
  ├─ action (VARCHAR)
  ├─ table_name (VARCHAR)
  ├─ record_id (UUID)
  ├─ old_values (JSONB)
  ├─ new_values (JSONB)
  ├─ change_reason (TEXT)
  └─ created_at (TIMESTAMP, PARTITIONED)
  └─ IMMUTABLE: No UPDATE, only INSERT


DEPLOYMENT TOPOLOGY:

┌──────────────────────────────────┐
│ AWS ALB (TLS 1.3)                │
└────────────┬─────────────────────┘
             ↓
┌──────────────────────────────────┐
│ EKS Pod (FastAPI)                │
│ ├─ 3 replicas (HA)               │
│ ├─ Health checks: /health        │
│ ├─ Graceful shutdown: 30s        │
│ └─ Resource limits: 512MB RAM    │
└────────────┬─────────────────────┘
             ↓
┌──────────────────────────────────┐
│ Postgres 15 (us-east-1)          │
│ ├─ Primary + 2 replicas          │
│ ├─ Automatic failover            │
│ ├─ Encrypted at rest (AES-256)   │
│ └─ Daily backups (7-day retention)
└──────────────────────────────────┘
```

**Exit Criteria**: Architecture approved by Solution Architect + Security Officer  
**Sign-Off Required**:
- [ ] Solution Architect: Design sound
- [ ] Security Officer: Encryption + RLS correct
- [ ] DevOps: Deployment feasible
- [ ] Compliance: Audit trail immutable

---

### SPARC Task 4: Refinement

**Task Type**: Task  
**Status**: Blocked (waits for Task 3 Done)

**Subtasks** (Implementation + Testing + Code Review):

#### 4a. Backend Implementation (Subtask)
- [ ] Create `models/organizations.py` (SQLAlchemy models)
- [ ] Create `schemas.py` (Pydantic models)
- [ ] Create `services/org_service.py` (business logic)
- [ ] Create `routes/organizations.py` (FastAPI endpoint)
- [ ] Add RLS policy to all org tables
- [ ] Add database migration (Alembic)
- [ ] **Compliance**: Ensure audit_log INSERT-only, no UPDATE

#### 4b. Unit Tests (Subtask)
- [ ] Test: Valid org creation → 201 + org_id
- [ ] Test: Duplicate slug → 409 Conflict
- [ ] Test: Unauthenticated request → 401
- [ ] Test: Creator assigned Owner role
- [ ] Test: Audit log entry created
- [ ] Test: RLS prevents cross-org data leakage
- [ ] Test: Invalid slug pattern → 400
- [ ] Coverage target: ≥85%
- [ ] Run: `pytest tests/test_organizations.py`

#### 4c. Integration Tests (Subtask)
- [ ] Spin up test DB (Docker postgres:15)
- [ ] Create org via POST /organizations
- [ ] Verify org in organizations table
- [ ] Verify user_organization row created
- [ ] Verify 4 roles created
- [ ] Verify audit_log entry immutable (SELECT only)
- [ ] Test: Query org with RLS → only creator sees it
- [ ] Test: Other user queries org → 403

#### 4d. Code Review (Subtask)
- [ ] Peer review (Security-focused)
  - [ ] No SQL injection (prepared statements)
  - [ ] No privilege escalation
  - [ ] No secrets in code/logs
  - [ ] Error messages non-revealing
- [ ] Tech lead review (Architecture)
- [ ] Compliance officer review (Audit trail)

#### 4e. Staging Deployment (Subtask)
- [ ] Deploy to staging environment
- [ ] Run smoke tests
- [ ] Manual QA: Try creating org, verify RLS
- [ ] Performance: Measure p99 latency (<100ms target)

**Exit Criteria**: All subtasks done, tests green, coverage ≥85%

---

### SPARC Task 5: Completion

**Task Type**: Task  
**Status**: Blocked (waits for Task 4 Done)

**Release Checklist**:

- [ ] All code committed + pushed
- [ ] PR created + linked to JIRA
- [ ] All GitHub checks passing:
  - [ ] Linting (ruff, pyright)
  - [ ] Tests (pytest, 85% coverage)
  - [ ] Type checking (mypy, 0 errors)
  - [ ] Security scan (no CVEs)
- [ ] Code reviewed by 2 engineers
- [ ] Compliance officer sign-off
- [ ] PR merged to main
- [ ] Tag created: `v0.1.0-SaaS-ORG-1`
- [ ] CHANGELOG.md updated
- [ ] Deployed to production
- [ ] Monitoring alerts enabled
- [ ] Release notes published
- [ ] Customer notification sent (if applicable)
- [ ] Audit trail verified (immutable log exists)
- [ ] **ISO Attestation**: Document signed for audit

**Compliance Sign-Off Template**:

```
=== COMPLIANCE CERTIFICATION ===
Product: ProjectZero SaaS
Feature: Organization CRUD (SaaS-ORG-1)
Version: v0.1.0
Date: [Release Date]

✅ ISO 27001 Controls Implemented:
  [X] A.9.2.1  — RBAC (Owner/Admin/Member/Guest roles)
  [X] A.13.1.3 — Segregation (org_id RLS)
  [X] A.12.4.1 — Audit Logging (immutable audit_logs table)
  [X] A.10.1.1 — Encryption (AES-256 at rest, TLS in transit)

✅ SOC2 Type II Controls:
  [X] CC6.2 — Change management (Git tags, code review)
  [X] CC7.2 — User access restrictions (RBAC)
  [X] CC9.2 — System monitoring (CloudWatch alarms)

✅ DPDP Act Compliance:
  [X] Data minimization (collect only name, email, slug)
  [X] Retention policy (7 years for Enterprise tier)
  [X] User consent logged

Signed:
  Officer: [Compliance Officer Name]
  Title: Chief Compliance Officer
  Date: [Date]
  Digital Signature: [Signature]
  
Audit File Path: s3://compliance-audit/SaaS-ORG-1-v0.1.0-audit.pdf
```

**Exit Criteria**: Production deployed + compliance signed off

---

## EPIC 2: SaaS-AUTH-2 (JWT Auth + Login/Signup/Logout + Refresh)

### STORY: SaaS-AUTH-2.0 — Authentication with TDD + Immutable Audit Trail

**Story Type**: Story  
**Priority**: P0  
**Assignee**: Agent: Auth Specialist  
**Sprint**: Sprint 1 (May 1–7)  
**Story Points**: 21  
**Dependencies**: SaaS-ORG-1 (org_id context required)  
**Blocked By**: SaaS-ORG-1  
**Blocks**: SaaS-FE-1, SaaS-BILL-2  

**Description**:
As a new user, I want to sign up with email + password and receive a JWT token, so that I can authenticate subsequent requests and maintain a secure session.

**Acceptance Criteria**:
- [ ] POST /api/v1/auth/signup with {email, password, full_name}
- [ ] Password hashed (bcrypt, 12 rounds)
- [ ] JWT issued (HS256, 1-hour expiry)
- [ ] Refresh token stored (secure httpOnly cookie, 7-day expiry)
- [ ] User record created with org_id assigned
- [ ] Immutable audit log: "user_signup user_id X org_id Y"
- [ ] RLS: User sees only their own org
- [ ] **ISO 27001 A.9.2.5**: Password policy enforced (12+ chars, mixed case, numbers)
- [ ] **ISO 27001 A.10.2.2**: TLS 1.3 enforced on all endpoints
- [ ] Coverage: ≥85%
- [ ] Tokens tested for expiry, refresh, revocation

---

### SPARC Task Structure (Same as Above)

#### S1: Specification
- Define signup/login/refresh flow
- Security requirements (bcrypt, JWT, TLS)
- Error cases (weak password, invalid email, MFA)
- Compliance mapping: A.9.2.5, A.10.2.2, A.14.2.1

#### S2: Pseudocode
- Algorithm: hash password, generate JWT, store refresh token
- Error handling: rate limiting (10 auth attempts/min)
- Audit logging: every auth event
- Token validation: signature, expiry, revocation

#### S3: Architecture
- Endpoint: POST /auth/signup, POST /auth/login, POST /auth/refresh
- Middleware: JWT validation on protected routes
- Database: users, refresh_tokens tables
- Encryption: Passwords hashed, tokens signed

#### S4: Refinement
- Backend implementation (FastAPI + bcrypt + PyJWT)
- Unit tests (valid/invalid credentials, weak passwords, token expiry)
- Integration tests (full signup → login flow)
- Code review (security-focused, no token leaks)
- Staging deployment

#### S5: Completion
- Production deployment
- Compliance sign-off (TLS, password policy, audit trail)
- Monitor for failed auth attempts (abuse detection)
- Alert on suspicious activity (too many failed logins)

---

## EPIC 3: SaaS-BILL-2 (Stripe Integration + Subscription CRUD + Webhook Handler)

### STORY: SaaS-BILL-2.0 — Stripe Checkout + Subscription Management

**Story Type**: Story  
**Priority**: P0  
**Assignee**: Agent: Billing Specialist  
**Sprint**: Sprint 1 (May 1–7)  
**Story Points**: 21  
**Dependencies**: SaaS-ORG-1, SaaS-AUTH-2  
**Blocked By**: SaaS-ORG-1, SaaS-AUTH-2  
**Blocks**: SaaS-BILL-3 (Invoice retrieval), SaaS-FE-2 (Onboarding)  

**Description**:
As an org admin, I want to upgrade from Starter to Professional tier and pay via Stripe, so that I can unlock premium features and manage billing.

**Acceptance Criteria**:
- [ ] POST /api/v1/billing/checkout creates Stripe checkout session
- [ ] Checkout includes org_id, plan_tier, annual/monthly option
- [ ] Stripe Webhook (POST /webhooks/stripe) handles payment success
- [ ] On success: subscription created, org plan_tier updated, audit log entry
- [ ] On failure: webhook logs error, alerts ops team, auto-retry (exponential backoff)
- [ ] Subscription CRUD: GET /billing/subscription, POST /billing/subscription/cancel
- [ ] **ISO 27001 A.8.3.1**: PCI-DSS compliance (use Stripe, never store card data locally)
- [ ] **ISO 27001 A.12.4.1**: Audit log tracks all billing events (checkout, payment, cancellation)
- [ ] Coverage: ≥85%
- [ ] Webhook signature verification (Stripe secret key)

---

### SPARC Tasks (S1–S5 same structure)

#### S1: Specification
- Stripe integration requirements
- Webhook signature validation
- Billing events (checkout_created, payment_succeeded, subscription_canceled)
- Audit trail for PCI-DSS compliance

#### S2: Pseudocode
- Algorithm: Create Stripe session → redirect to Stripe → webhook receives success
- Store subscription in billing_subscriptions table
- Update org.plan_tier
- Audit log entry with webhook_event_id for traceability

#### S3: Architecture
- Stripe client library (stripe-python)
- Webhook endpoint: /webhooks/stripe (public, no auth)
- Rate limiting: 100 requests/min per IP
- Error handling: Failed webhooks stored in dead-letter queue for replay

#### S4: Refinement
- Backend: Stripe client setup, webhook handler
- Unit tests: Stripe mock, session creation, webhook signature
- Integration tests: Mock Stripe, full flow checkout → webhook → subscription
- Security review: No card data leaked, webhook signatures correct

#### S5: Completion
- Production deployment (configure Stripe webhook endpoint)
- Compliance sign-off (PCI-DSS via Stripe)
- Monitor webhook failures (CloudWatch alarms)
- Test webhook replay for idempotency

---

## Compliance Matrix: All Tickets

```
ISO 27001 Controls Addressed by Feature:

Control              | SaaS-ORG-1 | SaaS-AUTH-2 | SaaS-BILL-2
─────────────────────┼────────────┼─────────────┼────────────
A.9 Access Control   |     ✅     |      ✅     |     ✅
  A.9.2.1 RBAC       |     ✅     |      ✅     |     ✅
  A.9.2.5 Pwd Policy |            |      ✅     |
A.10 Cryptography    |     ✅     |      ✅     |     ✅
  A.10.1.1 Encrypt   |     ✅     |      ✅     |     ✅
  A.10.2.2 TLS       |            |      ✅     |
A.12 Operations      |     ✅     |      ✅     |     ✅
  A.12.4.1 Audit Log |     ✅     |      ✅     |     ✅
  A.12.3.1 Incident  |            |             |     ✅
A.13 Segregation     |     ✅     |      ✅     |     ✅
  A.13.1.3 RLS       |     ✅     |      ✅     |     ✅
A.14 Supplier        |            |             |     ✅
  A.14.2.1 PCI-DSS   |            |             |     ✅

SOC2 Controls:
CC6 Change Mgmt      |     ✅     |      ✅     |     ✅
CC7 User Access      |     ✅     |      ✅     |     ✅
CC9 System Mon       |     ✅     |      ✅     |     ✅
```

---

## Enforcement Mechanisms

### Definition of Done (Per Ticket)

Every ticket MUST satisfy:

```
BEFORE MERGE:
[ ] All acceptance criteria met (manual verification)
[ ] All tests passing (automated in CI/CD)
[ ] Code coverage ≥85% (enforced by Codecov)
[ ] Zero type errors (mypy --strict)
[ ] Zero lint errors (ruff --strict)
[ ] Secrets scan passed (no API keys exposed)
[ ] Security review passed (OWASP Top 10 checked)
[ ] Compliance review passed (ISO controls mapped)
[ ] Code review: 2+ approvals (Maker-Checker)
[ ] Git commit references JIRA ticket
[ ] CHANGELOG.md updated
[ ] Database migration tested (rollback tested)
[ ] Monitoring/alerts configured
[ ] Audit trail verified (immutable, tested)

COMPLIANCE SIGN-OFF:
[ ] Security Officer: "No vulnerabilities"
[ ] Compliance Officer: "ISO controls satisfied"
[ ] Architect: "Design approved"
[ ] Tech Lead: "Code quality acceptable"

RELEASE:
[ ] Deployed to staging (pass smoke tests)
[ ] Deployed to production (canary → full rollout)
[ ] Monitoring shows healthy metrics
[ ] No incidents in first hour post-deploy
```

### CI/CD Pipeline (Github Actions)

Every PR must pass:

```yaml
name: SPARC-Compliant CI/CD

on: [pull_request, push]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
      - run: pip install ruff pyright
      - run: ruff check --strict .
      - run: pyright --outputstyle=json

  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: test
    steps:
      - uses: actions/checkout@v3
      - run: pytest --cov=app --cov-report=term --cov-report=xml
      - run: coverage report | grep -E "TOTAL.*8[5-9]%|TOTAL.*9[0-9]%"

  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: pip install bandit
      - run: bandit -r app/ -f json

  compliance:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: |
          # Verify JIRA ticket referenced in commit
          git log --oneline -1 | grep -E "SaaS-[A-Z]+-[0-9]+"
      - run: |
          # Verify audit trail comments in code
          grep -r "# ISO 27001:" app/ || true
      - run: |
          # Verify no secrets leaked
          git diff HEAD~1 | grep -E "PRIVATE_KEY|API_KEY|SECRET" && exit 1 || true
```

---

## Memory & Audit Trail

Every ticket execution recorded:

```
.claude/execution.log (Append-only):

[2026-05-01T09:00:00Z] TICKET SaaS-ORG-1.0 - SPEC
  Agent: Backend Specialist
  Duration: 2h 15m
  Signature: SHA256(spec_doc)

[2026-05-01T11:15:00Z] TICKET SaaS-ORG-1.0 - SPEC APPROVED
  Officer: Security Officer
  Officer: Compliance Officer
  
[2026-05-01T11:30:00Z] TICKET SaaS-ORG-1.0 - PSEUDOCODE
  ...
  
[2026-05-02T08:00:00Z] TICKET SaaS-ORG-1.0 - ARCHITECTURE APPROVED
  Officer: Solution Architect
  Officer: DevOps Lead
  
[2026-05-02T10:00:00Z] TICKET SaaS-ORG-1.0 - REFINEMENT (Impl)
  Agent: Backend Specialist
  Duration: 1d 6h
  Files Created: 8
  Tests Created: 24
  Coverage: 87%
  
[2026-05-03T10:00:00Z] TICKET SaaS-ORG-1.0 - CODE REVIEW APPROVED
  Reviewer 1: @engineer-1
  Reviewer 2: @engineer-2
  Security Review: @security-officer
  
[2026-05-03T14:00:00Z] TICKET SaaS-ORG-1.0 - COMPLETION
  Git Tag: v0.1.0-SaaS-ORG-1
  Commit: abc123def456...
  Deployed: production
  Compliance Signed: 2026-05-03T14:30:00Z
```

---

## Audit First Principles

### 1. Immutable Audit Logs
Every change to production data is logged:
- WHO (user_id)
- WHAT (table, column, old→new value)
- WHEN (timestamp)
- WHY (change_reason, JIRA ticket)
- HOW (API endpoint, Git commit)

### 2. Compliance by Design
Every ticket explicitly addresses ISO/SOC2/DPDP requirements.

### 3. Traceability
Every feature traces back to JIRA ticket → Git commit → audit log → compliance sign-off.

### 4. Immutable History
Git history + JIRA history + audit logs = complete record for regulators.

### 5. Separation of Concerns
- Code author ≠ Code reviewer
- Code reviewer ≠ Approver
- Approver ≠ Deployer
- Deployer ≠ Auditor

---

## Next Steps

1. **Create JIRA Epic** for each domain (ORG, AUTH, BILL, DASH, etc.)
2. **Create JIRA Story** (SaaS-ORG-1.0) with 5 SPARC tasks
3. **Populate Task 1 (Specification)** with full spec doc
4. **Require sign-off** before Task 2 starts
5. **Chain tasks** so Task N+1 blocked until Task N = Done
6. **Automate JIRA → Git** (branch, PR, compliance gates)
7. **Record audit trail** (.claude/execution.log) for regulators

**Status**: Ready for implementation via agent workers (SaaS-SPARC-AGENT-1)
