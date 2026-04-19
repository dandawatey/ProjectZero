#!/bin/bash
# JIRA ↔ GitHub Sync Script
# Keeps JIRA tickets synchronized with git commits and PR status
# Run: bash .claude/jira-sync.sh [ticket-key] [action]

set -e

JIRA_HOST="${JIRA_HOST:-jira.yourcompany.com}"
JIRA_PROJECT="PRJ0"
JIRA_API_TOKEN="${JIRA_API_TOKEN:-}"
GITHUB_REPO="${GITHUB_REPO:-}"
GITHUB_TOKEN="${GITHUB_TOKEN:-}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Helper: Print colored status
status() { echo -e "${GREEN}✓${NC} $1"; }
error() { echo -e "${RED}✗${NC} $1" >&2; exit 1; }
warn() { echo -e "${YELLOW}⚠${NC} $1"; }

# Parse arguments
TICKET_KEY="${1:-}"
ACTION="${2:-sync}"

if [[ -z "$TICKET_KEY" ]]; then
  error "Usage: jira-sync.sh [TICKET-KEY] [action: sync|status|link|close]"
fi

# ============================================================================
# ACTION: sync — Find all commits for ticket and sync to JIRA
# ============================================================================
if [[ "$ACTION" == "sync" ]]; then
  status "Syncing $TICKET_KEY with git history..."

  # Find all commits mentioning this ticket
  COMMITS=$(git log --all --grep="$TICKET_KEY" --oneline | head -10)

  if [[ -z "$COMMITS" ]]; then
    warn "No commits found for $TICKET_KEY"
  else
    status "Found commits:"
    echo "$COMMITS"

    # For each commit, create JIRA issue link
    while IFS= read -r line; do
      COMMIT_HASH=$(echo "$line" | awk '{print $1}')
      COMMIT_MSG=$(echo "$line" | cut -d' ' -f2-)

      # Get full commit URL
      COMMIT_URL="https://github.com/${GITHUB_REPO}/commit/${COMMIT_HASH}"

      status "Linking commit ${COMMIT_HASH:0:7}: $COMMIT_MSG → $TICKET_KEY"

      # Call JIRA API to add issue link (development/commit)
      curl -s -X POST \
        "https://${JIRA_HOST}/rest/api/3/issues/${TICKET_KEY}/remotelink" \
        -H "Authorization: Bearer ${JIRA_API_TOKEN}" \
        -H "Content-Type: application/json" \
        -d "{
          \"object\": {
            \"url\": \"${COMMIT_URL}\",
            \"title\": \"${COMMIT_MSG} [${COMMIT_HASH:0:7}]\",
            \"icon\": {
              \"url16x16\": \"https://github.com/favicon.ico\",
              \"title\": \"GitHub Commit\"
            }
          }
        }" > /dev/null 2>&1

      status "Commit ${COMMIT_HASH:0:7} linked to JIRA"
    done <<< "$COMMITS"
  fi

  # Update ticket status based on PR status
  status "Checking PR status for $TICKET_KEY..."

  PR_STATUS=$(curl -s -X GET \
    "https://api.github.com/search/issues?q=repo:${GITHUB_REPO}+PRJ0-.*${TICKET_KEY##*-}" \
    -H "Authorization: token ${GITHUB_TOKEN}" | jq -r '.items[0].state // "none"')

  case "$PR_STATUS" in
    "open")
      JIRA_STATUS="In Code Review"
      ;;
    "closed")
      JIRA_STATUS="Done"
      ;;
    *)
      JIRA_STATUS="In Progress"
      ;;
  esac

  status "Setting JIRA status to: $JIRA_STATUS"

  curl -s -X PUT \
    "https://${JIRA_HOST}/rest/api/3/issues/${TICKET_KEY}" \
    -H "Authorization: Bearer ${JIRA_API_TOKEN}" \
    -H "Content-Type: application/json" \
    -d "{
      \"fields\": {
        \"status\": {\"name\": \"${JIRA_STATUS}\"}
      }
    }" > /dev/null 2>&1

  status "JIRA ticket $TICKET_KEY synced"

# ============================================================================
# ACTION: status — Show JIRA ticket status
# ============================================================================
elif [[ "$ACTION" == "status" ]]; then
  status "Fetching $TICKET_KEY status from JIRA..."

  curl -s -X GET \
    "https://${JIRA_HOST}/rest/api/3/issues/${TICKET_KEY}" \
    -H "Authorization: Bearer ${JIRA_API_TOKEN}" | jq '{
      key: .key,
      summary: .fields.summary,
      status: .fields.status.name,
      assignee: .fields.assignee.displayName,
      created: .fields.created,
      updated: .fields.updated
    }'

# ============================================================================
# ACTION: link — Link a specific commit to JIRA ticket
# ============================================================================
elif [[ "$ACTION" == "link" ]]; then
  COMMIT_HASH="${3:-}"

  if [[ -z "$COMMIT_HASH" ]]; then
    error "Usage: jira-sync.sh $TICKET_KEY link [COMMIT_HASH]"
  fi

  status "Linking commit $COMMIT_HASH to $TICKET_KEY..."

  COMMIT_URL="https://github.com/${GITHUB_REPO}/commit/${COMMIT_HASH}"
  COMMIT_MSG=$(git log -1 --format=%B "$COMMIT_HASH" 2>/dev/null || echo "Commit $COMMIT_HASH")

  curl -s -X POST \
    "https://${JIRA_HOST}/rest/api/3/issues/${TICKET_KEY}/remotelink" \
    -H "Authorization: Bearer ${JIRA_API_TOKEN}" \
    -H "Content-Type: application/json" \
    -d "{
      \"object\": {
        \"url\": \"${COMMIT_URL}\",
        \"title\": \"${COMMIT_MSG}\",
        \"icon\": {
          \"url16x16\": \"https://github.com/favicon.ico\",
          \"title\": \"GitHub Commit\"
        }
      }
    }" > /dev/null 2>&1

  status "Commit linked to $TICKET_KEY"

# ============================================================================
# ACTION: close — Close JIRA ticket (mark as Done)
# ============================================================================
elif [[ "$ACTION" == "close" ]]; then
  status "Closing $TICKET_KEY in JIRA..."

  curl -s -X PUT \
    "https://${JIRA_HOST}/rest/api/3/issues/${TICKET_KEY}" \
    -H "Authorization: Bearer ${JIRA_API_TOKEN}" \
    -H "Content-Type: application/json" \
    -d '{
      "fields": {
        "status": {"name": "Done"}
      }
    }' > /dev/null 2>&1

  status "JIRA ticket $TICKET_KEY closed"

else
  error "Unknown action: $ACTION. Use: sync | status | link | close"
fi
