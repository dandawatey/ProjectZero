#!/bin/bash
set -euo pipefail

# ============================================================
# ProjectZero Integration Validator
# Validates ALL required integrations before execution begins
# NO INTEGRATION → NO EXECUTION
# ============================================================

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

pass() { echo -e "  ${GREEN}✓${NC} $1"; }
fail() { echo -e "  ${RED}✗${NC} $1"; FAILURES=$((FAILURES + 1)); }
warn() { echo -e "  ${YELLOW}⚠${NC} $1"; }
info() { echo -e "  ${BLUE}→${NC} $1"; }

FAILURES=0

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║  ProjectZero Integration Validator       ║"
echo "╚══════════════════════════════════════════╝"
echo ""

# Load .env
if [ -f .env ]; then
    set -a; source .env; set +a
    pass ".env file found"
else
    fail ".env file missing — copy from .env.example"
    echo ""
    echo "Run: cp .env.example .env"
    exit 1
fi

# ── GITHUB ──────────────────────────────────────
echo ""
echo "── GitHub ──"
if [ -n "${GITHUB_TOKEN:-}" ]; then
    GITHUB_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" \
        -H "Authorization: token ${GITHUB_TOKEN}" \
        -H "Accept: application/vnd.github.v3+json" \
        https://api.github.com/user 2>/dev/null || echo "000")
    if [ "$GITHUB_RESPONSE" = "200" ]; then
        pass "GitHub token valid"
        GITHUB_USER=$(curl -s -H "Authorization: token ${GITHUB_TOKEN}" \
            https://api.github.com/user | grep -o '"login":"[^"]*"' | head -1 | cut -d'"' -f4)
        info "Authenticated as: ${GITHUB_USER}"
    else
        fail "GitHub token invalid (HTTP ${GITHUB_RESPONSE})"
    fi
    if [ -n "${GITHUB_ORG:-}" ]; then
        ORG_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" \
            -H "Authorization: token ${GITHUB_TOKEN}" \
            "https://api.github.com/orgs/${GITHUB_ORG}" 2>/dev/null || echo "000")
        if [ "$ORG_RESPONSE" = "200" ]; then
            pass "GitHub org '${GITHUB_ORG}' accessible"
        else
            warn "GitHub org '${GITHUB_ORG}' not accessible (HTTP ${ORG_RESPONSE}) — may be personal account"
        fi
    else
        fail "GITHUB_ORG not set"
    fi
else
    fail "GITHUB_TOKEN not set"
fi

# ── JIRA ────────────────────────────────────────
echo ""
echo "── JIRA ──"
if [ -n "${JIRA_BASE_URL:-}" ] && [ -n "${JIRA_API_TOKEN:-}" ] && [ -n "${JIRA_USER_EMAIL:-}" ]; then
    JIRA_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" \
        -u "${JIRA_USER_EMAIL}:${JIRA_API_TOKEN}" \
        -H "Accept: application/json" \
        "${JIRA_BASE_URL}/rest/api/3/myself" 2>/dev/null || echo "000")
    if [ "$JIRA_RESPONSE" = "200" ]; then
        pass "JIRA connection valid"
        JIRA_NAME=$(curl -s -u "${JIRA_USER_EMAIL}:${JIRA_API_TOKEN}" \
            "${JIRA_BASE_URL}/rest/api/3/myself" | grep -o '"displayName":"[^"]*"' | head -1 | cut -d'"' -f4)
        info "JIRA user: ${JIRA_NAME}"
    else
        fail "JIRA connection failed (HTTP ${JIRA_RESPONSE})"
    fi
    if [ -n "${JIRA_PROJECT_KEY:-}" ]; then
        PROJ_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" \
            -u "${JIRA_USER_EMAIL}:${JIRA_API_TOKEN}" \
            "${JIRA_BASE_URL}/rest/api/3/project/${JIRA_PROJECT_KEY}" 2>/dev/null || echo "000")
        if [ "$PROJ_RESPONSE" = "200" ]; then
            pass "JIRA project '${JIRA_PROJECT_KEY}' accessible"
        else
            warn "JIRA project '${JIRA_PROJECT_KEY}' not found — will create during bootstrap"
        fi
    else
        fail "JIRA_PROJECT_KEY not set"
    fi
else
    fail "JIRA credentials incomplete (need JIRA_BASE_URL, JIRA_USER_EMAIL, JIRA_API_TOKEN)"
fi

# ── CONFLUENCE ──────────────────────────────────
echo ""
echo "── Confluence ──"
if [ -n "${CONFLUENCE_BASE_URL:-}" ] && [ -n "${CONFLUENCE_API_TOKEN:-}" ]; then
    CONF_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" \
        -u "${JIRA_USER_EMAIL:-}:${CONFLUENCE_API_TOKEN}" \
        -H "Accept: application/json" \
        "${CONFLUENCE_BASE_URL}/rest/api/space" 2>/dev/null || echo "000")
    if [ "$CONF_RESPONSE" = "200" ]; then
        pass "Confluence connection valid"
    else
        fail "Confluence connection failed (HTTP ${CONF_RESPONSE})"
    fi
    if [ -n "${CONFLUENCE_SPACE_KEY:-}" ]; then
        SPACE_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" \
            -u "${JIRA_USER_EMAIL:-}:${CONFLUENCE_API_TOKEN}" \
            "${CONFLUENCE_BASE_URL}/rest/api/space/${CONFLUENCE_SPACE_KEY}" 2>/dev/null || echo "000")
        if [ "$SPACE_RESPONSE" = "200" ]; then
            pass "Confluence space '${CONFLUENCE_SPACE_KEY}' accessible"
        else
            warn "Confluence space '${CONFLUENCE_SPACE_KEY}' not found — will create during bootstrap"
        fi
    fi
else
    fail "Confluence credentials incomplete"
fi

# ── TEMPORAL ────────────────────────────────────
echo ""
echo "── Temporal ──"
TEMPORAL_HOST="${TEMPORAL_HOST:-localhost:7233}"
if command -v temporal &> /dev/null; then
    TEMPORAL_CHECK=$(temporal workflow list --address "${TEMPORAL_HOST}" --limit 1 2>&1 || echo "FAIL")
    if echo "$TEMPORAL_CHECK" | grep -q "FAIL\|error\|Error"; then
        fail "Temporal not reachable at ${TEMPORAL_HOST}"
    else
        pass "Temporal connected at ${TEMPORAL_HOST}"
    fi
else
    # Try raw TCP check
    TEMPORAL_ADDR=$(echo "$TEMPORAL_HOST" | cut -d: -f1)
    TEMPORAL_PORT=$(echo "$TEMPORAL_HOST" | cut -d: -f2)
    if nc -z -w3 "$TEMPORAL_ADDR" "$TEMPORAL_PORT" 2>/dev/null; then
        pass "Temporal port open at ${TEMPORAL_HOST}"
    else
        fail "Temporal not reachable at ${TEMPORAL_HOST}"
    fi
fi

# ── DATABASE ────────────────────────────────────
echo ""
echo "── Database ──"
if [ -n "${DATABASE_URL:-}" ]; then
    if command -v psql &> /dev/null; then
        DB_CHECK=$(psql "${DATABASE_URL}" -c "SELECT 1;" 2>&1 || echo "FAIL")
        if echo "$DB_CHECK" | grep -q "FAIL\|error\|could not"; then
            fail "Postgres connection failed"
        else
            pass "Postgres connected"
        fi
    else
        # Parse and TCP check
        DB_HOST=$(echo "$DATABASE_URL" | sed -E 's|.*@([^:/]+).*|\1|')
        DB_PORT=$(echo "$DATABASE_URL" | sed -E 's|.*:([0-9]+)/.*|\1|')
        DB_PORT=${DB_PORT:-5432}
        if nc -z -w3 "$DB_HOST" "$DB_PORT" 2>/dev/null; then
            pass "Postgres port open at ${DB_HOST}:${DB_PORT}"
        else
            fail "Postgres not reachable at ${DB_HOST}:${DB_PORT}"
        fi
    fi
else
    fail "DATABASE_URL not set"
fi

# ── REDIS ───────────────────────────────────────
echo ""
echo "── Redis ──"
if [ -n "${REDIS_URL:-}" ]; then
    REDIS_HOST=$(echo "$REDIS_URL" | sed -E 's|redis://([^:/]+).*|\1|')
    REDIS_PORT=$(echo "$REDIS_URL" | sed -E 's|.*:([0-9]+)$|\1|')
    REDIS_PORT=${REDIS_PORT:-6379}
    if command -v redis-cli &> /dev/null; then
        REDIS_CHECK=$(redis-cli -u "${REDIS_URL}" ping 2>&1 || echo "FAIL")
        if [ "$REDIS_CHECK" = "PONG" ]; then
            pass "Redis connected (PONG)"
        else
            fail "Redis ping failed"
        fi
    else
        if nc -z -w3 "$REDIS_HOST" "$REDIS_PORT" 2>/dev/null; then
            pass "Redis port open at ${REDIS_HOST}:${REDIS_PORT}"
        else
            fail "Redis not reachable at ${REDIS_HOST}:${REDIS_PORT}"
        fi
    fi
else
    fail "REDIS_URL not set"
fi

# ── AI PROVIDER ─────────────────────────────────
echo ""
echo "── AI Provider ──"
if [ -n "${ANTHROPIC_API_KEY:-}" ]; then
    AI_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" \
        -H "x-api-key: ${ANTHROPIC_API_KEY}" \
        -H "anthropic-version: 2023-06-01" \
        -H "content-type: application/json" \
        -d '{"model":"claude-sonnet-4-20250514","max_tokens":1,"messages":[{"role":"user","content":"hi"}]}' \
        https://api.anthropic.com/v1/messages 2>/dev/null || echo "000")
    if [ "$AI_RESPONSE" = "200" ]; then
        pass "Anthropic API key valid"
        info "Model: ${CLAUDE_MODEL:-claude-sonnet-4-20250514}"
    else
        fail "Anthropic API key invalid (HTTP ${AI_RESPONSE})"
    fi
else
    fail "ANTHROPIC_API_KEY not set"
fi

# ── OPTIONAL INTEGRATIONS ───────────────────────
echo ""
echo "── Optional ──"
[ -n "${SENTRY_DSN:-}" ] && pass "Sentry DSN configured" || warn "Sentry DSN not set (optional)"
[ -n "${POSTHOG_API_KEY:-}" ] && pass "PostHog configured" || warn "PostHog not set (optional)"
[ -n "${STRIPE_SECRET_KEY:-}" ] && pass "Stripe configured" || warn "Stripe not set (optional)"
[ -n "${MINIO_ENDPOINT:-}" ] && pass "MinIO configured" || warn "MinIO not set (optional)"

# ── SUMMARY ─────────────────────────────────────
echo ""
echo "══════════════════════════════════════════"
if [ $FAILURES -eq 0 ]; then
    echo -e "${GREEN}ALL INTEGRATIONS VALID${NC}"
    echo "Ready for workflow execution."
    exit 0
else
    echo -e "${RED}${FAILURES} INTEGRATION(S) FAILED${NC}"
    echo "Fix failures above before proceeding."
    echo "NO INTEGRATION → NO EXECUTION"
    exit 1
fi
