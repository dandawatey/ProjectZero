#!/bin/bash
# Bulk create JIRA tickets via REST API

JIRA_URL="https://isourceinnovation.atlassian.net"
JIRA_PROJECT="PRJ0"
JIRA_USER="dandawate.y@isourceinfosystems.com"
JIRA_TOKEN=$(grep "^JIRA_API_TOKEN=" /Users/yogesh/1_Code/Office/i-ProjectZero/ProjectZeroFactory/.env 2>/dev/null | cut -d'=' -f2)

# Encode credentials for Basic auth
AUTH_HEADER="Authorization: Basic $(echo -n "$JIRA_USER:$JIRA_TOKEN" | base64)"

# Create ticket helper
create_jira_ticket() {
    local summary="$1"
    local description="$2"
    local priority="$3"
    local story_points="$4"

    local payload=$(cat <<EOF
{
  "fields": {
    "project": {"key": "$JIRA_PROJECT"},
    "summary": "$summary",
    "description": "$description",
    "issuetype": {"name": "Story"},
    "priority": {"name": "$priority"},
    "customfield_10016": $story_points
  }
}
EOF
)

    curl -s -X POST \
        -H "$AUTH_HEADER" \
        -H "Content-Type: application/json" \
        -d "$payload" \
        "$JIRA_URL/rest/api/3/issues" \
        2>&1 | jq -r '.key // .errors[0].message // "Error"'
}

echo "🔄 Bulk creating JIRA tickets..."
echo ""

# COMPLETED TICKETS

echo "✅ Creating completed tickets:"

ticket_49=$(create_jira_ticket \
    "SaaS-ORG-1: Organization CRUD with RBAC, RLS & Quotas" \
    "COMPLETED: 11/11 tests passing, 100% coverage. Organization CRUD endpoints, RLS, RBAC, quota enforcement. Commit: 66488bd" \
    "Highest" \
    "13")
echo "  PRJ0-49: $ticket_49"

ticket_48=$(create_jira_ticket \
    "SaaS-AUTH-2: Login/Signup Endpoints with JWT & MFA" \
    "COMPLETED: 26/26 tests passing, 95% coverage. Register, login, refresh, logout, MFA endpoints. JWT + bcrypt." \
    "Highest" \
    "13")
echo "  PRJ0-48: $ticket_48"

ticket_47=$(create_jira_ticket \
    "SaaS-FE-1: Auth UI Pages (Login, Signup, MFA, Password Reset)" \
    "COMPLETED: 40/40 tests passing, 100% coverage. React components, forms, validation, accessibility." \
    "Highest" \
    "13")
echo "  PRJ0-47: $ticket_47"

ticket_51=$(create_jira_ticket \
    "SaaS-BILL-2: Stripe Subscription API with Webhooks" \
    "COMPLETED: 7/7 tests passing. Stripe checkout, subscriptions, webhooks, signature verification." \
    "Highest" \
    "13")
echo "  PRJ0-51: $ticket_51"

echo ""
echo "⏳ Creating pending P0 tickets:"

ticket_46=$(create_jira_ticket \
    "SaaS-FE-2: Onboarding Flow (4-Step Wizard)" \
    "Depends: PRJ0-49, PRJ0-48, PRJ0-47. New user onboarding: org setup, member invite, workspace config, billing review." \
    "Highest" \
    "11")
echo "  PRJ0-46: $ticket_46"

ticket_45=$(create_jira_ticket \
    "SaaS-DASH-1: Dashboard Metrics (Org Overview)" \
    "Depends: PRJ0-49. Dashboard showing orgs, members, workspaces, usage, billing status." \
    "Highest" \
    "11")
echo "  PRJ0-45: $ticket_45"

ticket_50=$(create_jira_ticket \
    "SaaS-ORG-4: Settings Pages (Org Profile & Members)" \
    "Depends: PRJ0-49. Settings for org profile, members, billing, workspaces." \
    "Highest" \
    "11")
echo "  PRJ0-50: $ticket_50"

echo ""
echo "✅ Bulk creation complete!"
echo ""
echo "View board: $JIRA_URL/jira/software/projects/$JIRA_PROJECT/board"
