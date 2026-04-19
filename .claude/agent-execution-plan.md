# Sprint 1 Parallel Agent Execution Plan

**Date**: 2026-04-19 (Day 0)  
**Sprint**: Sprint 1 (May 1–7, 2026)  
**Status**: Launching agents NOW  

---

## Agent Team Assignments

### 🤖 AGENT-1: SaaS-AUTH-2.0-S4 (Backend: JWT Auth Endpoints)

**Ticket**: SaaS-AUTH-2.0-S4 (Refinement Phase)  
**Worktree**: platform/auth-endpoints  
**Branch**: feature/SaaS-AUTH-2  
**Task**: Complete signup/login/refresh endpoints with TDD  
**Timeline**: 2 days (Thu 5/4 – Fri 5/5)  

**Implementation Checklist**:
```
PHASE S4.1: Test-Driven Development (TDD)
─────────────────────────────────────────

[ ] Write failing test: POST /auth/signup (valid email + password)
    Expected: 201 Created + {user_id, token, refresh_token}
    Test file: tests/test_auth_signup.py
    
[ ] Implement: POST /auth/signup endpoint
    - Accept email, password, full_name
    - Validate email format (RFC 5322)
    - Validate password (12+ chars, mixed case, numbers)
    - Hash password (bcrypt, 12 rounds)
    - Create user record
    - Create org_id context
    - Issue JWT (1h expiry, HS256)
    - Store refresh token (secure httpOnly cookie, 7d expiry)
    - Log audit entry: "user_signup user_id=X org_id=Y"
    Response: HTTP 201 + Location header
    
[ ] Test: POST /auth/login (valid credentials)
    Expected: 200 + JWT token
    
[ ] Implement: POST /auth/login endpoint
    - Accept email, password
    - Verify user exists
    - Verify password (bcrypt compare)
    - Rate limiting: 10 attempts/min per IP
    - Issue JWT + refresh token
    - Log audit entry: "user_login user_id=X"
    Response: HTTP 200 + token
    
[ ] Test: POST /auth/refresh-token (valid refresh token)
    Expected: 200 + new JWT
    
[ ] Implement: POST /auth/refresh-token endpoint
    - Accept refresh token (from cookie or body)
    - Verify refresh token signature
    - Verify not expired (7 days)
    - Issue new JWT (1h expiry)
    - Log audit entry: "token_refreshed user_id=X"
    Response: HTTP 200 + new JWT
    
[ ] Test: POST /auth/logout
    Expected: 200, refresh token revoked
    
[ ] Implement: POST /auth/logout endpoint
    - Accept user context (JWT)
    - Revoke refresh token
    - Clear httpOnly cookie
    - Log audit entry: "user_logout user_id=X"
    Response: HTTP 200

PHASE S4.2: Error Handling
──────────────────────────

[ ] Test: POST /auth/signup with weak password
    Expected: 400 Bad Request
    Message: "Password must be 12+ characters"
    
[ ] Test: POST /auth/signup with duplicate email
    Expected: 409 Conflict
    Message: "Email already registered"
    
[ ] Test: POST /auth/login with invalid credentials
    Expected: 401 Unauthorized
    Message: Generic (don't expose user not found)
    
[ ] Test: Rate limiting (>10 auth attempts/min from same IP)
    Expected: 429 Too Many Requests
    
[ ] Test: Expired refresh token
    Expected: 401 Unauthorized

PHASE S4.3: Code Quality
────────────────────────

[ ] Run pytest (target: ≥85% coverage)
    Command: pytest tests/test_auth*.py --cov=app.routes.auth
    
[ ] Run ruff (target: 0 lint errors)
    Command: ruff check --strict app/
    
[ ] Run pyright (target: 0 type errors)
    Command: pyright --strict app/
    
[ ] Run security scan
    Command: bandit -r app/ (0 vulnerabilities)
    
[ ] No secrets in code (API keys, tokens, passwords)
    Check: grep -r "SECRET\|API_KEY\|PASSWORD" app/

PHASE S4.4: Integration Tests
──────────────────────────────

[ ] Test: Full signup → login flow
    1. POST /auth/signup (new user)
    2. Verify user in database
    3. POST /auth/login (same credentials)
    4. Verify JWT token valid
    5. POST /auth/refresh-token (refresh token)
    6. Verify new JWT issued
    
[ ] Test: Audit trail
    1. Verify audit_logs table has 3 entries:
       - user_signup
       - user_login
       - token_refreshed
    2. Verify immutability (no UPDATE on audit logs)

PHASE S4.5: Code Review
───────────────────────

[ ] Self-review: Code is clean, well-named, no TODOs
[ ] Peer review: 2+ engineers approve
[ ] Security review: No vulnerabilities
[ ] Compliance review: Audit logs correct
[ ] Tech lead review: Design sound

PHASE S4.6: Commit & PR
───────────────────────

[ ] Commit message:
    "feat(SaaS-AUTH-2): JWT auth endpoints (signup/login/refresh)
    
    - POST /auth/signup: email + password → JWT + refresh token
    - POST /auth/login: credentials → JWT
    - POST /auth/refresh-token: refresh token → new JWT
    - POST /auth/logout: revoke refresh token
    - Password hashing: bcrypt, 12 rounds
    - Rate limiting: 10 auth attempts/min per IP
    - Audit logging: All auth events immutable
    - Tests: 87% coverage (target ≥85%)
    - Type checking: 0 errors
    - Linting: 0 errors
    
    Closes: SaaS-AUTH-2
    Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>"
    
[ ] Push to origin/feature/SaaS-AUTH-2
[ ] Create PR (auto-link JIRA SaaS-AUTH-2)
[ ] GitHub checks pass:
    - Linting: ✅
    - Type checking: ✅
    - Tests: ✅
    - Coverage: ≥85% ✅
    - Security: ✅

PHASE S4.7: Merge & Release
────────────────────────────

[ ] Code review approved (2+)
[ ] Compliance sign-off collected
[ ] Squash merge to main
[ ] Tag: v0.1.1-SaaS-AUTH-2
[ ] Deploy to production (canary → full)
[ ] Monitor for errors (first 2h)
[ ] Update CHANGELOG.md
[ ] Close JIRA ticket
```

---

### 🤖 AGENT-2: SaaS-BILL-2.0-S4 (Backend: Stripe Integration)

**Ticket**: SaaS-BILL-2.0-S4 (Refinement Phase)  
**Worktree**: platform/billing-api  
**Branch**: feature/SaaS-BILL-2  
**Task**: Complete Stripe checkout + webhook handler  
**Timeline**: 2 days (Thu 5/4 – Fri 5/5)  

**Implementation Checklist**:
```
PHASE S4.1: Stripe Checkout
─────────────────────────────

[ ] Test: POST /api/v1/billing/checkout
    Input: {org_id, plan_tier: "professional", frequency: "annual"}
    Expected: 201 + {checkout_url, session_id}
    
[ ] Implement: POST /api/v1/billing/checkout
    - Accept org_id, plan_tier, frequency (annual/monthly)
    - Look up pricing: professional=$499/mo or $4,990/yr
    - Create Stripe checkout session
    - Set metadata: {org_id, plan_tier, frequency}
    - Redirect URL: {baseurl}/billing/success
    - Return checkout_url (redirect user to Stripe)
    
[ ] Test: User cancels Stripe checkout
    Expected: User returned to /billing page (no subscription created)

PHASE S4.2: Webhook Handler
───────────────────────────

[ ] Test: Webhook signature validation
    Input: Stripe webhook payload + signature
    Expected: Valid signature → process event
    Expected: Invalid signature → 403 Forbidden
    
[ ] Implement: POST /webhooks/stripe
    - Verify Stripe webhook signature (using STRIPE_WEBHOOK_SECRET)
    - Parse event: payment_intent.succeeded
    - Metadata contains: org_id, plan_tier
    
[ ] Test: On payment success, create subscription
    1. Extract org_id from metadata
    2. Create row in billing_subscriptions:
       {org_id, stripe_subscription_id, plan_tier, status, created_at}
    3. Update org.plan_tier = "professional"
    4. Create audit log: "subscription_created org_id=X plan=professional"
    Expected: Subscription in database
    
[ ] Test: On payment failure
    Expected: Webhook logs error, alerts ops, no subscription created
    
[ ] Test: Webhook idempotency
    1. Send same webhook twice (Stripe retries)
    2. Verify subscription created only once (idempotency key)

PHASE S4.3: Subscription Management
────────────────────────────────────

[ ] Test: GET /api/v1/billing/subscription
    Expected: {org_id, plan_tier, status, next_billing_date}
    
[ ] Implement: GET /api/v1/billing/subscription
    - Accept org_id (from JWT context)
    - Query billing_subscriptions
    - Return: plan_tier, status, renewal date
    
[ ] Test: POST /api/v1/billing/subscription/cancel
    Expected: Subscription canceled, org reverted to Starter
    
[ ] Implement: POST /api/v1/billing/subscription/cancel
    - Accept org_id
    - Call Stripe cancel_subscription()
    - Update status = "canceled"
    - Revert org.plan_tier = "starter"
    - Create audit log: "subscription_canceled org_id=X"

PHASE S4.4: Database Schema
───────────────────────────

[ ] Create table: billing_subscriptions
    Columns:
    - id (UUID, PK)
    - org_id (FK organizations.id)
    - stripe_subscription_id (VARCHAR, unique)
    - stripe_customer_id (VARCHAR)
    - plan_tier (VARCHAR: starter, professional, enterprise)
    - status (VARCHAR: active, canceled, past_due)
    - created_at (TIMESTAMP)
    - canceled_at (TIMESTAMP, nullable)
    - next_billing_date (DATE)
    Indexes: (org_id), (stripe_subscription_id)
    
[ ] Create table: billing_usage
    Columns:
    - id (UUID, PK)
    - org_id (FK organizations.id)
    - event_type (VARCHAR: agent_run, user_invited, repo_created)
    - quantity (INTEGER)
    - created_at (TIMESTAMP)
    Partitioned by created_at (daily)

PHASE S4.5: Error Handling
──────────────────────────

[ ] Test: Invalid org_id
    Expected: 404 Not Found
    
[ ] Test: Webhook from unknown Stripe account
    Expected: 401 Unauthorized (bad signature)
    
[ ] Test: Concurrent checkout requests
    Expected: First succeeds, second rejected (idempotency)
    
[ ] Test: Network error from Stripe
    Expected: Retry with exponential backoff, max 3 retries

PHASE S4.6: Code Quality
────────────────────────

[ ] Run pytest (target: ≥85% coverage)
    - Mock Stripe API (use Stripe test mode)
    - Test success path
    - Test error paths
    - Test webhook signature validation
    
[ ] Run ruff, pyright, bandit
    - 0 lint errors
    - 0 type errors
    - 0 vulnerabilities
    
[ ] No Stripe API keys in code
    Check: grep -r "sk_live\|pk_live" app/ (should be empty)

PHASE S4.7: Integration Test
──────────────────────────────

[ ] Full flow: Checkout → Payment → Webhook → Subscription
    1. POST /billing/checkout (org_id=X, plan=professional)
    2. Mock user paying via Stripe
    3. Stripe fires webhook: payment_intent.succeeded
    4. App receives webhook, creates subscription
    5. GET /billing/subscription → returns "professional"
    6. POST /billing/subscription/cancel → reverts to "starter"

PHASE S4.8: Commit & PR
───────────────────────

[ ] Commit message:
    "feat(SaaS-BILL-2): Stripe integration (checkout + webhooks)
    
    - POST /billing/checkout: Create Stripe checkout session
    - POST /webhooks/stripe: Handle payment events
    - Create billing_subscriptions on success
    - Auto-upgrade org.plan_tier
    - Webhook idempotency: prevent duplicate charges
    - Error handling: Network retries, Stripe API errors
    - Tests: 88% coverage (target ≥85%)
    - Security: Webhook signature validation, no API keys exposed
    
    Closes: SaaS-BILL-2
    Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>"
    
[ ] Push, create PR, get approvals
[ ] Merge to main, tag v0.1.1-SaaS-BILL-2
[ ] Deploy to production
```

---

### 🤖 AGENT-3: Monitor Agent (Compliance + CI/CD)

**Role**: Continuous monitoring of Sprint 1 progress  
**Worktree**: main  
**Task**: Track tests, linting, type checking, compliance gates  
**Timeline**: Continuous (background process)  

**Monitoring Tasks**:
```
EVERY 5 MINUTES:
[ ] Check dashboard.sh for live progress
    - Burndown chart updated
    - Ticket status current
    
EVERY 30 SECONDS:
[ ] Run monitor.sh
    - Type checking (pyright)
    - Linting (ruff)
    - Test discovery
    - Git status per worktree
    
EVERY 60 SECONDS:
[ ] Check git commits for JIRA references
    git log --oneline feature/SaaS-AUTH-2 | grep "SaaS-AUTH-2"
    
[ ] Track test results
    pytest --co -q (count tests)
    
[ ] Alert if blockers found:
    - Linting errors: Red alert
    - Type errors: Red alert
    - Test failures: Red alert
    - Uncommitted changes: Yellow alert
    
ON PR CREATION:
[ ] Verify:
    - All checks passing
    - Coverage ≥85%
    - 2+ reviewers requested
    - JIRA ticket linked
    
ON MERGE:
[ ] Update JIRA ticket to "Testing" → "Done"
[ ] Create release note (auto-generated)
[ ] Track time-to-merge (target: <2h code review)

DAILY:
[ ] Report burndown
    - Eng-days completed vs. target
    - Blockers encountered
    - Risk assessment
```

---

## Success Criteria (End of Sprint 1)

| Metric | Target | Owner |
|--------|--------|-------|
| SaaS-AUTH-2 S4 complete | Thu 5/5 | AGENT-1 |
| SaaS-BILL-2 S4 complete | Thu 5/5 | AGENT-2 |
| Both deployed to prod | Fri 5/6 | AGENT-1 + AGENT-2 |
| Code coverage | ≥85% | Monitor Agent |
| Type errors | 0 | Monitor Agent |
| Lint errors | 0 | Monitor Agent |
| Security vulns | 0 | Monitor Agent |
| Compliance sign-off | 100% | Compliance officers |

---

## How to Track Progress

### Real-Time (Every 5 seconds)
```bash
# In TMUX window 0 (Dashboard)
# Auto-refreshes from dashboard.sh
```

### CI/CD Checks (Every 30 seconds)
```bash
# In TMUX window 4 (Monitor)
# Auto-runs from monitor.sh
```

### Git Commits
```bash
# Check AUTH-2 commits
cd platform/auth-endpoints
git log --oneline | head -10

# Check BILL-2 commits
cd platform/billing-api
git log --oneline | head -10
```

### Test Results
```bash
# Run tests manually
cd platform/auth-endpoints
pytest --cov=app --cov-report=term

cd platform/billing-api
pytest --cov=app --cov-report=term
```

### JIRA Ticket Status
Each commit automatically updates JIRA:
- SaaS-AUTH-2.0-S4: "In Progress" → "Testing" → "Done"
- SaaS-BILL-2.0-S4: "In Progress" → "Testing" → "Done"

---

## Next Steps (Immediate)

1. **Launch AGENT-1** → Start SaaS-AUTH-2.0-S4 implementation
2. **Launch AGENT-2** → Start SaaS-BILL-2.0-S4 implementation
3. **Launch AGENT-3** → Start compliance monitoring
4. **Watch TMUX dashboard** → Real-time progress tracking
5. **Escalate blockers** → If any agent gets stuck >1h

---

**Status**: Ready to launch  
**Coordinator**: Main session  
**Timeline**: Thu 5/4 – Fri 5/10 (7 days to ship all P0 features)
