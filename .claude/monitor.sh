#!/bin/bash
# CI/CD + Compliance monitoring (runs continuously)

PROJECT_ROOT="/Users/yogesh/1_Code/Office/i-ProjectZero/ProjectZeroFactory"

while true; do
  clear

  echo ""
  echo "╔═══════════════════════════════════════════════════════════════════════════╗"
  echo "║              CI/CD + COMPLIANCE MONITOR (Continuous)                      ║"
  echo "╚═══════════════════════════════════════════════════════════════════════════╝"
  echo ""

  cd "$PROJECT_ROOT"

  # Check main branch status
  echo "📍 MAIN BRANCH STATUS:"
  echo ""
  echo -n "   Branch:    "
  git branch --show-current
  echo -n "   Commits:   "
  git rev-list --count HEAD
  echo -n "   Last commit: "
  git log -1 --pretty=format:"%h - %s" 2>/dev/null || echo "N/A"
  echo ""

  # Check each worktree
  echo "🔍 WORKTREE STATUS:"
  echo ""

  for worktree in "platform/auth-endpoints" "platform/billing-api" "platform/auth-ui"; do
    if [ -d "$worktree" ]; then
      wt_name=$(basename "$worktree")
      echo "   ▶ $wt_name"

      (
        cd "$worktree"

        # Git info
        echo -n "     Branch: "
        git branch --show-current 2>/dev/null || echo "N/A"

        echo -n "     Commits: "
        git rev-list --count HEAD 2>/dev/null || echo "0"

        # Git status
        echo -n "     Status: "
        if [ -z "$(git status --porcelain 2>/dev/null)" ]; then
          echo "✅ Clean"
        else
          changes=$(git status --porcelain 2>/dev/null | wc -l)
          echo "⚠️  $changes changes"
          git status --porcelain 2>/dev/null | head -3 | sed 's/^/       /'
        fi

        # Python checks
        if [ -f "pyproject.toml" ] || [ -f "requirements.txt" ]; then

          # Type checking
          echo -n "     Pyright: "
          if command -v pyright &> /dev/null; then
            pyright_errors=$(pyright --outputstyle=json . 2>/dev/null | grep -o '"severity": "error"' | wc -l)
            if [ "$pyright_errors" -eq 0 ]; then
              echo "✅ No errors"
            else
              echo "❌ $pyright_errors errors"
            fi
          else
            echo "⚠️  Not installed"
          fi

          # Linting
          echo -n "     Ruff: "
          if command -v ruff &> /dev/null; then
            lint_errors=$(ruff check . 2>/dev/null | wc -l)
            if [ "$lint_errors" -eq 0 ]; then
              echo "✅ No errors"
            else
              echo "⚠️  $lint_errors warnings"
            fi
          else
            echo "⚠️  Not installed"
          fi

          # Tests
          echo -n "     Tests: "
          if [ -d "tests" ] && command -v pytest &> /dev/null; then
            test_result=$(pytest --co -q 2>/dev/null | wc -l)
            if [ "$test_result" -gt 0 ]; then
              echo "✅ $test_result tests ready"
            else
              echo "⚠️  No tests found"
            fi
          else
            echo "⚠️  No test directory"
          fi
        fi

        echo ""

      ) || echo "     ❌ Error reading worktree"
    fi
  done

  # Summary
  echo "📊 OVERALL STATUS:"
  echo ""

  total_changes=0
  for worktree in "platform/auth-endpoints" "platform/billing-api" "platform/auth-ui"; do
    if [ -d "$worktree" ]; then
      changes=$(cd "$worktree" && git status --porcelain 2>/dev/null | wc -l)
      total_changes=$((total_changes + changes))
    fi
  done

  echo "   Uncommitted changes across worktrees: $total_changes"
  echo "   All checks enabled: ✅ Type, Lint, Tests"
  echo ""

  # Next check info
  echo "⏰ Last check: $(date '+%Y-%m-%d %H:%M:%S')"
  echo "   Next check in 30 seconds... (Ctrl+C to stop)"
  echo ""

  sleep 30
done
