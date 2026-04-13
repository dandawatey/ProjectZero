#!/bin/bash
set -euo pipefail

# ============================================================
# ProjectZero Guided Integration Setup
# Walks user through each integration one-by-one
# ============================================================

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

header() { echo -e "\n${CYAN}${BOLD}── $1 ──${NC}\n"; }
guide() { echo -e "${BLUE}→${NC} $1"; }
ask() { echo -en "${YELLOW}? ${NC}$1: "; }
ok() { echo -e "${GREEN}✓${NC} $1"; }
err() { echo -e "${RED}✗${NC} $1"; }

# Start
echo ""
echo "╔══════════════════════════════════════════════════╗"
echo "║  ProjectZero — Guided Integration Setup          ║"
echo "║  We'll configure each integration step-by-step   ║"
echo "╚══════════════════════════════════════════════════╝"
echo ""

# Create .env if missing
if [ ! -f .env ]; then
    cp .env.example .env
    ok "Created .env from .env.example"
fi

# Source existing values
set -a; source .env 2>/dev/null || true; set +a

update_env() {
    local key="$1"
    local value="$2"
    if grep -q "^${key}=" .env; then
        sed -i '' "s|^${key}=.*|${key}=${value}|" .env 2>/dev/null || \
        sed -i "s|^${key}=.*|${key}=${value}|" .env
    else
        echo "${key}=${value}" >> .env
    fi
}

# ── GITHUB ──────────────────────────────────────
header "GitHub Setup"
guide "You need a Personal Access Token with repo + workflow scopes."
guide "1. Go to: https://github.com/settings/tokens"
guide "2. Click 'Generate new token (classic)'"
guide "3. Select scopes: repo, workflow"
guide "4. Generate and copy the token"
echo ""

if [ -n "${GITHUB_TOKEN:-}" ]; then
    guide "Current token: ${GITHUB_TOKEN:0:8}...***"
    ask "Keep existing? (y/n)"
    read -r keep
    [ "$keep" = "y" ] || GITHUB_TOKEN=""
fi

if [ -z "${GITHUB_TOKEN:-}" ]; then
    ask "GitHub Personal Access Token"
    read -r GITHUB_TOKEN
    update_env "GITHUB_TOKEN" "$GITHUB_TOKEN"
fi

# Validate
GITHUB_STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
    -H "Authorization: token ${GITHUB_TOKEN}" \
    https://api.github.com/user 2>/dev/null || echo "000")
if [ "$GITHUB_STATUS" = "200" ]; then
    ok "GitHub token valid"
else
    err "GitHub token invalid — please check and try again"
fi

ask "GitHub Organization (or username)"
read -r GITHUB_ORG
update_env "GITHUB_ORG" "$GITHUB_ORG"

ask "Default branch (main)"
read -r GITHUB_BRANCH
GITHUB_BRANCH=${GITHUB_BRANCH:-main}
update_env "GITHUB_DEFAULT_BRANCH" "$GITHUB_BRANCH"

# ── JIRA ────────────────────────────────────────
header "JIRA Setup"
guide "You need:"
guide "  - Your Atlassian site URL (e.g., https://yourorg.atlassian.net)"
guide "  - Your email address"
guide "  - An API token"
guide ""
guide "To create API token:"
guide "1. Go to: https://id.atlassian.com/manage-profile/security/api-tokens"
guide "2. Click 'Create API token'"
guide "3. Copy the token"
echo ""

ask "JIRA Base URL (e.g., https://yourorg.atlassian.net)"
read -r JIRA_BASE_URL
update_env "JIRA_BASE_URL" "$JIRA_BASE_URL"

ask "JIRA Email"
read -r JIRA_USER_EMAIL
update_env "JIRA_USER_EMAIL" "$JIRA_USER_EMAIL"

ask "JIRA API Token"
read -r JIRA_API_TOKEN
update_env "JIRA_API_TOKEN" "$JIRA_API_TOKEN"

# Validate
JIRA_STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
    -u "${JIRA_USER_EMAIL}:${JIRA_API_TOKEN}" \
    "${JIRA_BASE_URL}/rest/api/3/myself" 2>/dev/null || echo "000")
if [ "$JIRA_STATUS" = "200" ]; then
    ok "JIRA connection valid"
else
    err "JIRA connection failed (HTTP ${JIRA_STATUS})"
fi

ask "JIRA Project Key (e.g., PZ)"
read -r JIRA_PROJECT_KEY
update_env "JIRA_PROJECT_KEY" "$JIRA_PROJECT_KEY"

# ── CONFLUENCE ──────────────────────────────────
header "Confluence Setup"
guide "Uses same Atlassian credentials as JIRA."
echo ""

CONFLUENCE_BASE_URL="${JIRA_BASE_URL}/wiki"
update_env "CONFLUENCE_BASE_URL" "$CONFLUENCE_BASE_URL"
update_env "CONFLUENCE_API_TOKEN" "$JIRA_API_TOKEN"
ok "Confluence URL set to: ${CONFLUENCE_BASE_URL}"

ask "Confluence Space Key (e.g., PZ)"
read -r CONFLUENCE_SPACE_KEY
update_env "CONFLUENCE_SPACE_KEY" "$CONFLUENCE_SPACE_KEY"

# ── TEMPORAL ────────────────────────────────────
header "Temporal Setup"
guide "Default: localhost:7233 (local Temporal server)"
guide "Start Temporal: temporal server start-dev"
echo ""

ask "Temporal host (localhost:7233)"
read -r TEMPORAL_HOST
TEMPORAL_HOST=${TEMPORAL_HOST:-localhost:7233}
update_env "TEMPORAL_HOST" "$TEMPORAL_HOST"

ask "Temporal namespace (default)"
read -r TEMPORAL_NAMESPACE
TEMPORAL_NAMESPACE=${TEMPORAL_NAMESPACE:-default}
update_env "TEMPORAL_NAMESPACE" "$TEMPORAL_NAMESPACE"

ask "Temporal task queue (projectzero-factory)"
read -r TEMPORAL_TASK_QUEUE
TEMPORAL_TASK_QUEUE=${TEMPORAL_TASK_QUEUE:-projectzero-factory}
update_env "TEMPORAL_TASK_QUEUE" "$TEMPORAL_TASK_QUEUE"

# ── DATABASE ────────────────────────────────────
header "Database Setup"
guide "Default: postgresql://postgres:postgres@localhost:5432/projectzero"
echo ""

ask "Postgres URL (press enter for default)"
read -r DATABASE_URL
DATABASE_URL=${DATABASE_URL:-postgresql://postgres:postgres@localhost:5432/projectzero}
update_env "DATABASE_URL" "$DATABASE_URL"

# ── REDIS ───────────────────────────────────────
header "Redis Setup"
guide "Default: redis://localhost:6379"
echo ""

ask "Redis URL (press enter for default)"
read -r REDIS_URL
REDIS_URL=${REDIS_URL:-redis://localhost:6379}
update_env "REDIS_URL" "$REDIS_URL"

# ── AI PROVIDER ─────────────────────────────────
header "AI Provider Setup"
guide "You need an Anthropic API key."
guide "1. Go to: https://console.anthropic.com/settings/keys"
guide "2. Create a new key"
guide "3. Copy the key"
echo ""

ask "Anthropic API Key"
read -r ANTHROPIC_API_KEY
update_env "ANTHROPIC_API_KEY" "$ANTHROPIC_API_KEY"
update_env "CLAUDE_MODEL" "claude-sonnet-4-20250514"

# ── OPTIONAL ────────────────────────────────────
header "Optional Integrations"
echo ""

ask "Sentry DSN (press enter to skip)"
read -r SENTRY_DSN
[ -n "$SENTRY_DSN" ] && update_env "SENTRY_DSN" "$SENTRY_DSN"

ask "PostHog API Key (press enter to skip)"
read -r POSTHOG_API_KEY
[ -n "$POSTHOG_API_KEY" ] && update_env "POSTHOG_API_KEY" "$POSTHOG_API_KEY"

# ── DONE ────────────────────────────────────────
echo ""
echo "╔══════════════════════════════════════════════════╗"
echo "║  Setup Complete!                                  ║"
echo "║                                                   ║"
echo "║  Run validation:                                  ║"
echo "║  ./scripts/validate-integrations.sh               ║"
echo "║                                                   ║"
echo "║  Then:                                            ║"
echo "║  /factory-init                                    ║"
echo "╚══════════════════════════════════════════════════╝"
