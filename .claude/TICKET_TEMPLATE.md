# Ticket Template — ProjectZero SaaS MVP

Every ticket MUST include all sections below. Copy this template for new tickets.

---

## Header

**Ticket ID**: PRJ0-XXX  
**Title**: [Short, imperative verb] [feature/module]  
**Priority**: P0|P1|P2  
**Status**: PENDING|IN_PROGRESS|BLOCKED|COMPLETED  
**Story Points**: N  
**Assigned To**: [Agent Name or Team]  

---

## 1. CONTEXT

### Business Value
_Why does this ticket exist? What problem does it solve?_

Example:
```
Users need a way to authenticate. Without login/signup, users can't create accounts 
or access the product. This is the foundation for all other features.
```

### Success Criteria
_How do we know this ticket succeeded?_
- Users can sign up with email/password
- Users can log in + receive JWT
- Failed login shows appropriate error
- Session lasts 15 minutes (access token)

### Dependencies
_What blocks this ticket? What does it block?_
- **Blocks**: SaaS-FE-1 (Auth Pages), SaaS-ORG-2 (User Settings)
- **Blocked By**: SaaS-ORG-1 (User model must exist)

### References
- **JIRA**: [Link to JIRA ticket if exists]
- **Confluence**: [Link to design doc if exists]
- **ADRs**: [Architecture Decision Records]
- **Related Tickets**: SaaS-ORG-1, SaaS-AUTH-3, SaaS-SEC-1

---

## 2. SPECIFICATION (What are we building?)

### Acceptance Criteria
Each criterion must be testable and include expected behavior.

✅ Acceptance Criteria:
- [ ] POST /api/v1/auth/register accepts email + password
- [ ] Password hashing uses bcrypt (min 12 rounds)
- [ ] JWT issued on successful login (15min expiry)
- [ ] Refresh token stored in DB (7-day expiry)
- [ ] Rate limiting: max 5 failed attempts per 15min per IP
- [ ] 401 on invalid credentials (no user enumeration)
- [ ] All endpoints require HTTPS in production
- [ ] All tests pass (80%+ coverage)

### User Stories
```
AS A: New user
I WANT TO: Sign up with email and password
SO THAT: I can access my organization dashboard

GIVEN: User is on signup page
WHEN: User enters valid email + strong password
THEN: Account created, JWT issued, redirected to onboarding
AND: Confirmation email sent (async)
```

---

## 3. PSEUDOCODE (How will we build it?)

### High-Level Algorithm
```
REGISTER(email, password):
  1. Validate email format (EmailStr Pydantic)
  2. Validate password strength (min 12 chars, uppercase, number, symbol)
  3. Check email not already registered (query User table)
  4. Hash password with bcrypt (12 rounds)
  5. Create User row (email, hashed_password, created_at)
  6. Issue JWT token (sub=user_id, exp=now+15min)
  7. Create RefreshToken row (token_hash, expires_at=now+7days)
  8. Return { access_token, refresh_token, user: { id, email } }
  9. On error: return 400/409 with safe error message

LOGIN(email, password):
  1. Query User by email
  2. If not found: return 401 "Invalid credentials"
  3. Compare password with bcrypt.verify(password, hashed_password)
  4. If mismatch: increment failed_attempts counter
  5. If failed_attempts >= 5 in last 15min: return 429 (rate limit)
  6. If match: Reset failed_attempts counter
  7. Issue new JWT + RefreshToken
  8. Return response (same as REGISTER)
```

### Component Architecture
```
Request
  ↓
FastAPI Route (auth.py)
  ↓
Pydantic Schema Validation (schemas.py)
  ↓
Auth Service (services/auth.py)
  ↓
Database (SQLAlchemy ORM)
  ├─ User model (email, hashed_password, created_at)
  └─ RefreshToken model (token_hash, expires_at, revoked)
```

---

## 4. ARCHITECTURE (Design decisions)

### Tech Stack for This Ticket
- **Backend**: FastAPI + SQLAlchemy
- **Auth**: JWT (python-jose) + bcrypt + passlib
- **Database**: PostgreSQL (User, RefreshToken tables)
- **Testing**: pytest + pytest-asyncio
- **Validation**: Pydantic (EmailStr, Field constraints)

### API Contract

**POST /api/v1/auth/register**
```
Request:
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}

Response (201):
{
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "token_type": "bearer",
  "expires_in": 900,  // seconds
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "created_at": "2026-04-19T12:00:00Z"
  }
}

Error Responses:
400: { "detail": "Invalid email format" }
409: { "detail": "Email already registered" }
422: { "detail": "Password too weak" }
```

### Security Decisions
- ✅ Never return password hash in responses
- ✅ Rate limit by IP address (5 attempts/15min)
- ✅ Do NOT leak whether email exists (401 for both invalid email + wrong password)
- ✅ Use bcrypt minimum 12 rounds (cost factor)
- ✅ JWT signed with HS256 + strong secret key
- ✅ Refresh tokens stored as salted hash, not plaintext

### Data Model
```sql
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email VARCHAR(255) UNIQUE NOT NULL,
  hashed_password VARCHAR(255) NOT NULL,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE refresh_tokens (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  token_hash VARCHAR(64) NOT NULL UNIQUE,  -- SHA256 hex digest
  expires_at TIMESTAMP NOT NULL,
  revoked BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT NOW()
);
```

---

## 5. REFINEMENT (How do we test & iterate?)

### TDD Cycle

**Phase 1: RED** (Write failing tests)
```python
def test_register_creates_user():
    response = client.post("/auth/register", json={
        "email": "newuser@example.com",
        "password": "SecurePassword123!"
    })
    assert response.status_code == 201
    assert response.json()["access_token"]
    assert response.json()["user"]["email"] == "newuser@example.com"
```

**Phase 2: GREEN** (Implement to make test pass)
- Create auth schemas
- Create User + RefreshToken models
- Implement register endpoint
- Run tests → should pass

**Phase 3: REFACTOR** (Clean up, optimize)
- Extract password validation to utility
- Add rate limiting middleware
- Add comprehensive error handling
- Add logging

### Test Cases
- ✅ Register with valid email + password → 201
- ✅ Register with existing email → 409 Conflict
- ✅ Register with weak password → 422 Unprocessable Entity
- ✅ Register with invalid email → 400 Bad Request
- ✅ Login with correct credentials → 200 + JWT
- ✅ Login with wrong password → 401
- ✅ Login with non-existent email → 401 (same message as wrong password)
- ✅ Rate limiting after 5 failed attempts → 429
- ✅ Refresh token exchange → 200 + new access token
- ✅ Revoked refresh token → 401

### Coverage Target
**Minimum 80% code coverage** for:
- auth.py (routes)
- schemas.py (validation)
- services/auth.py (business logic)
- models/user.py (User + RefreshToken)

---

## 6. COMPLETION (Verification & Merge)

### Definition of Done
A ticket is DONE when ALL of the following are true:

- [ ] Code is written and committed
- [ ] All tests pass (RED → GREEN → REFACTOR complete)
- [ ] Coverage >= 80% (pytest-cov report)
- [ ] Zero lint errors (ruff check)
- [ ] Zero type errors (mypy strict)
- [ ] All acceptance criteria met (manual verification)
- [ ] Commit message includes ticket ID (e.g., "SaaS-AUTH-2: ...")
- [ ] Code review approved (2 eyes minimum)
- [ ] Merged to main branch
- [ ] Worktree deleted

### Quality Gate Checklist
```bash
# Before marking DONE, run:
pytest tests/test_auth.py --cov=app.api.routes.auth --cov-report=term
pytest tests/test_auth.py --cov=app.schemas.auth --cov-report=term
pytest tests/test_auth.py --cov=app.services.auth --cov-report=term

ruff check app/api/routes/auth.py app/schemas/auth.py app/services/auth.py
mypy --strict app/api/routes/auth.py
```

### Merge Protocol
1. All tests GREEN ✓
2. Coverage 80%+ ✓
3. Code review approved ✓
4. Commit message includes ticket: `git log --grep="PRJ0-XX"` ✓
5. Branch pushed: `git push origin auth-endpoints-prj0-XX` ✓
6. Create PR (auto-link to JIRA if integration enabled)
7. Merge to main: `git merge --ff-only auth-endpoints-prj0-XX`
8. Delete worktree: `git worktree remove platform/auth-endpoints`
9. Update ticket status: COMPLETED
10. Update execution.log with completion timestamp

### Sign-Off
- **Maker**: Developer who implemented (Agent)
- **Checker**: Automated tests (pytest)
- **Reviewer**: Code review (manual or automated)
- **Approver**: Project lead or CTO (sign-off)

---

## 7. NOTES & CONSTRAINTS

### Assumptions
- PostgreSQL is running (not SQLite for production)
- Email is unique identifier (normalization handled at schema)
- 15-minute access token lifetime is acceptable
- Bcrypt cost=12 is sufficient (adjust if performance issues)

### Known Limitations
- ⏳ Email verification not in MVP (noted for future)
- ⏳ Password reset flow not in this ticket (separate SaaS-AUTH-3)
- ⏳ OAuth integration (Google, GitHub) not in this ticket (separate SaaS-AUTH-4)

### Potential Risks
- **Risk**: Bcrypt 72-byte password limit (very long passwords truncated)
  - **Mitigation**: Document in API / frontend validation
- **Risk**: Rate limiting by IP (VPN users share IP)
  - **Mitigation**: Consider additional signals (User-Agent, email domain)
  - **For MVP**: Accept limitation, document for future
- **Risk**: JWT secret key rotation
  - **Mitigation**: Document process for ops team

---

## 8. REFERENCES

| Type | Link | Notes |
|------|------|-------|
| JIRA | [SaaS-AUTH-2](https://jira.example.com/browse/PRJ0-49) | Main ticket tracker |
| Confluence | [Auth Design Doc](https://confluence.example.com/pages/auth-design) | Architecture + threat model |
| ADR | [JWT vs Session Tokens](https://github.com/project/adr/001-auth-strategy.md) | Why we chose JWT |
| Related | SaaS-ORG-1 | User model foundation |
| Related | SaaS-FE-1 | Login/signup UI |

---

## Example: Completed Ticket (SaaS-BILL-2)

See `.claude/worktree-logs/billing-api-prj0-51.log` for a completed ticket with:
- 7 passing tests
- Stripe integration
- Webhook handler
- Ready for merge ✓

