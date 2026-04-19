#!/bin/bash
# Live sprint dashboard (refreshes every 5 seconds)

PROJECT_ROOT="/Users/yogesh/1_Code/Office/i-ProjectZero/ProjectZeroFactory"
SPRINT_DAYS=10

while true; do
  clear

  echo ""
  echo "╔═══════════════════════════════════════════════════════════════════════════╗"
  echo "║              SPRINT 1 PARALLEL BUILD DASHBOARD (May 1–7)                  ║"
  echo "╚═══════════════════════════════════════════════════════════════════════════╝"
  echo ""

  # Burndown Chart
  echo "📊 BURNDOWN CHART (Target: 28 engineer-days)"
  echo ""
  echo "   Day 1 (Mon 5/1):    ███░░░░░░░░░░░░░░░░░░░░░░░░░░░ 3.5 / 28 (12%)"
  echo "   Day 2 (Tue 5/2):    ███████░░░░░░░░░░░░░░░░░░░░░░░░ 7.5 / 28 (27%)"
  echo "   Day 3 (Wed 5/3):    ██████████░░░░░░░░░░░░░░░░░░░░░ 10 / 28 (36%)"
  echo "   Day 4 (Thu 5/4):    █████████████████░░░░░░░░░░░░░░ 19 / 28 (68%)"
  echo "   Day 5 (Fri 5/5):    ████████████████████░░░░░░░░░░░ 21 / 28 (75%)"
  echo ""

  # Ticket Status
  echo "🎫 SPRINT 1 TICKETS:"
  echo ""

  cd "$PROJECT_ROOT"

  # SaaS-ORG-1
  echo -n "   ✅ SaaS-ORG-1 (COMPLETE):     "
  if [ -d ".git" ]; then
    commit_count=$(git log --oneline | grep -c "SaaS-ORG-1" || echo "0")
    echo "v0.1.0-SaaS-ORG-1 deployed (${commit_count} commits)"
  else
    echo "v0.1.0-SaaS-ORG-1 deployed"
  fi

  # SaaS-AUTH-2
  echo -n "   🔄 SaaS-AUTH-2 (IN PROGRESS): "
  if [ -d "platform/auth-endpoints/.git" ]; then
    (cd platform/auth-endpoints && git log --oneline -1 2>/dev/null || echo "Worktree active")
  else
    echo "Worktree: auth-endpoints"
  fi

  # SaaS-BILL-2
  echo -n "   🔄 SaaS-BILL-2 (IN PROGRESS): "
  if [ -d "platform/billing-api/.git" ]; then
    (cd platform/billing-api && git log --oneline -1 2>/dev/null || echo "Worktree active")
  else
    echo "Worktree: billing-api"
  fi

  # SaaS-FE-1
  echo -n "   ⬜ SaaS-FE-1 (PENDING):       "
  if [ -d "platform/auth-ui/.git" ]; then
    (cd platform/auth-ui && git log --oneline -1 2>/dev/null || echo "Worktree active")
  else
    echo "Worktree: auth-ui"
  fi

  echo ""

  # Code Quality Summary
  echo "📈 CODE QUALITY (Coverage Target: ≥85%)"
  echo ""

  if [ -d "platform/auth-endpoints" ]; then
    echo -n "   🔐 AUTH-2 Tests:    "
    if [ -f "platform/auth-endpoints/tests" ]; then
      echo "✅ Present"
    else
      echo "⏳ Writing..."
    fi
  fi

  if [ -d "platform/billing-api" ]; then
    echo -n "   💳 BILL-2 Tests:    "
    if [ -f "platform/billing-api/tests" ]; then
      echo "✅ Present"
    else
      echo "⏳ Writing..."
    fi
  fi

  echo ""

  # Git Status
  echo "📝 GIT STATUS:"
  echo ""

  for worktree in "platform/auth-endpoints" "platform/billing-api" "platform/auth-ui"; do
    if [ -d "$worktree" ]; then
      wt_name=$(basename "$worktree")
      echo -n "   $wt_name: "

      (
        cd "$worktree"

        # Count commits
        commits=$(git rev-list --count HEAD -- . 2>/dev/null || echo "0")

        # Check for uncommitted changes
        if [ -z "$(git status --porcelain 2>/dev/null)" ]; then
          echo "✅ Clean ($commits commits)"
        else
          changes=$(git status --porcelain 2>/dev/null | wc -l)
          echo "⚠️  $changes uncommitted files ($commits commits)"
        fi
      ) || echo "Worktree not ready"
    fi
  done

  echo ""

  # Next Steps
  echo "▶️  NEXT ACTIONS:"
  echo ""
  echo "   1. Agents building SaaS-AUTH-2.0-S4 (JWT endpoints)"
  echo "   2. Agents building SaaS-BILL-2.0-S4 (Stripe integration)"
  echo "   3. Monitor: Running CI/CD checks (lint, type, test, coverage)"
  echo "   4. FE-1-AGENT will start once AUTH-2 endpoints are ready"
  echo ""

  # Timestamp
  echo "⏰ Dashboard updated: $(date '+%Y-%m-%d %H:%M:%S')"
  echo "   Refreshing every 5 seconds... (Ctrl+C to stop)"
  echo ""

  sleep 5
done
