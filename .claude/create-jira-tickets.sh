#!/bin/bash
# Bulk create JIRA tickets with SPARC + DoD using JIRA CLI

JIRA_PROJECT="PRJ0"
JIRA_ENDPOINT="https://isourceinnovation.atlassian.net"

# Helper to create ticket
create_ticket() {
    local ticket_id="$1"
    local title="$2"
    local priority="$3"
    local story_points="$4"
    local description="$5"

    echo "Creating $ticket_id: $title..."

    jira create \
        --project="$JIRA_PROJECT" \
        --type="Story" \
        --summary="$title" \
        --priority="$priority" \
        --custom="customfield_10000=$story_points" \
        --description="$description" \
        --endpoint="$JIRA_ENDPOINT" \
        2>&1 | grep -E "KEY|ERROR|created"
}

# COMPLETED TICKETS

echo "=== CREATING COMPLETED TICKETS ==="

create_ticket "PRJ0-49" \
    "SaaS-ORG-1: Organization CRUD with RBAC, RLS & Quotas" \
    "Highest" \
    "13" \
    "✅ COMPLETED: 11/11 tests passing, 100% coverage
- Organization CRUD endpoints (create, read, update, delete)
- Row-Level Security (RLS) - users only access their orgs
- Role-Based Access Control (RBAC) - Owner-only operations
- Quota enforcement by tier (Starter=1, Professional=10, Enterprise=unlimited)
- Member management and workspace management
SPARC: Specification ✓ Pseudocode ✓ Architecture ✓ Refinement ✓ Completion ✓
DoD: All tests pass ✓ 100% coverage ✓ Commit: 66488bd ✓"

create_ticket "PRJ0-48" \
    "SaaS-AUTH-2: Login/Signup Endpoints with JWT & MFA" \
    "Highest" \
    "13" \
    "✅ COMPLETED: 26/26 tests passing, 95% coverage
- POST /auth/register (user creation + JWT)
- POST /auth/login (email/password authentication)
- POST /auth/refresh (token rotation)
- POST /auth/logout (token revocation)
- POST /auth/mfa-verify (OTP validation)
- Password hashing: Argon2 + Bcrypt (12 rounds)
- Rate limiting: 5 attempts/15min per IP
SPARC: Specification ✓ Pseudocode ✓ Architecture ✓ Refinement ✓ Completion ✓
DoD: All tests pass ✓ 95% coverage ✓"

create_ticket "PRJ0-47" \
    "SaaS-FE-1: Auth UI Pages (Login, Signup, MFA, Password Reset)" \
    "Highest" \
    "13" \
    "✅ COMPLETED: 40/40 tests passing, 100% coverage
- React 18 + TypeScript + TailwindCSS
- LoginForm, SignupForm, MFAInput, PasswordStrength components
- Form validation (Zod) + error handling
- Loading states + accessibility (ARIA, keyboard nav)
- Responsive design (mobile-first)
- Password strength meter
SPARC: Specification ✓ Pseudocode ✓ Architecture ✓ Refinement ✓ Completion ✓
DoD: All tests pass ✓ 100% coverage ✓"

create_ticket "PRJ0-51" \
    "SaaS-BILL-2: Stripe Subscription API with Webhooks" \
    "Highest" \
    "13" \
    "✅ COMPLETED: 7/7 tests passing, 53% coverage
- POST /billing/checkout-session (Stripe integration)
- GET /billing/subscription (fetch current)
- POST /billing/cancel-subscription
- POST /billing/update-payment-method
- POST /billing/webhook (Stripe event processing)
- Webhook HMAC-SHA256 signature verification
- Tier pricing: Starter=\$29, Professional=\$99, Enterprise=custom
SPARC: Specification ✓ Pseudocode ✓ Architecture ✓ Refinement ✓ Completion ✓
DoD: All tests pass ✓ Commit: billing-api-prj0-51 ✓"

echo ""
echo "=== CREATING PENDING TICKETS ==="

# PENDING P0 TICKETS

create_ticket "PRJ0-46" \
    "SaaS-FE-2: Onboarding Flow (4-Step Wizard)" \
    "Highest" \
    "11" \
    "New users guided through 4-step setup:
1. Create organization
2. Invite team members
3. Configure workspace
4. Review billing

React components + API integration
Responsive design
All steps tested (80%+ coverage)

Depends on: PRJ0-49, PRJ0-48, PRJ0-47"

create_ticket "PRJ0-45" \
    "SaaS-DASH-1: Dashboard Metrics (Org Overview)" \
    "Highest" \
    "11" \
    "Dashboard showing:
- Organizations list + tier indicators
- Member count
- Workspace count
- Monthly usage + quota indicators
- Billing status

React dashboard + API integration
Charts/metrics visualization
All components tested

Depends on: PRJ0-49"

create_ticket "PRJ0-50" \
    "SaaS-ORG-4: Settings Pages (Org Profile & Members)" \
    "Highest" \
    "11" \
    "Settings pages:
- Organization profile (edit name, description, logo)
- Members management (invite, remove, change roles)
- Billing settings (update payment method, view invoices)
- Workspace management (create, delete, archive)

React components + forms
Permission checks (Owner-only)
All pages tested

Depends on: PRJ0-49"

echo ""
echo "✅ Ticket creation complete!"
echo ""
echo "View board: $JIRA_ENDPOINT/jira/software/projects/$JIRA_PROJECT/board"
