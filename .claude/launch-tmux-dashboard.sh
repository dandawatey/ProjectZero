#!/bin/bash
set -e

PROJECT_ROOT="/Users/yogesh/1_Code/Office/i-ProjectZero/ProjectZeroFactory"
cd "$PROJECT_ROOT"

# Kill existing session
echo "🔄 Killing existing projectzero session..."
tmux kill-session -t projectzero 2>/dev/null || true
sleep 1

# Create new session
echo "📺 Creating TMUX session (projectzero, 250x50)..."
tmux new-session -d -s projectzero -x 250 -y 50 -c "$PROJECT_ROOT"

# Window 0: Dashboard
echo "📊 Setting up Dashboard window..."
tmux send-keys -t projectzero:0 "cd '$PROJECT_ROOT' && clear && echo 'SPRINT 1 DASHBOARD (refreshing every 5s)...' && bash .claude/dashboard.sh" Enter

# Window 1: AUTH-2 Worktree
echo "🔐 Setting up AUTH-2 window..."
tmux new-window -t projectzero:1 -n "AUTH-2" -c "$PROJECT_ROOT/platform/auth-endpoints"
tmux send-keys -t projectzero:1 "clear && echo '=== SaaS-AUTH-2 Worktree ===' && git branch && git status" Enter

# Window 2: BILL-2 Worktree
echo "💳 Setting up BILL-2 window..."
tmux new-window -t projectzero:2 -n "BILL-2" -c "$PROJECT_ROOT/platform/billing-api"
tmux send-keys -t projectzero:2 "clear && echo '=== SaaS-BILL-2 Worktree ===' && git branch && git status" Enter

# Window 3: FE-1 Worktree
echo "🎨 Setting up FE-1 window..."
tmux new-window -t projectzero:3 -n "FE-1" -c "$PROJECT_ROOT/platform/auth-ui"
tmux send-keys -t projectzero:3 "clear && echo '=== SaaS-FE-1 Worktree ===' && git branch && git status" Enter

# Window 4: Monitor
echo "📡 Setting up Monitor window..."
tmux new-window -t projectzero:4 -n "MONITOR" -c "$PROJECT_ROOT"
tmux send-keys -t projectzero:4 "clear && echo 'COMPLIANCE MONITOR (checking every 30s)...' && bash .claude/monitor.sh" Enter

# List windows
echo "✅ TMUX session ready!"
tmux list-windows -t projectzero
echo ""

# Print help
cat << 'EOF'
╔══════════════════════════════════════════════════════════╗
║         SPRINT 1 PARALLEL BUILD DASHBOARD READY          ║
╚══════════════════════════════════════════════════════════╝

📺 TMUX NAVIGATION:
   Ctrl+B 0 = Dashboard (live progress)
   Ctrl+B 1 = AUTH-2 worktree
   Ctrl+B 2 = BILL-2 worktree
   Ctrl+B 3 = FE-1 worktree
   Ctrl+B 4 = Monitor (CI/CD + compliance)

   Ctrl+B n = Next window
   Ctrl+B p = Previous window
   Ctrl+B d = Detach (doesn't kill session)

🚀 LAUNCHING AGENTS:
   In AUTH-2 window:  Agent building SaaS-AUTH-2.0-S4
   In BILL-2 window:  Agent building SaaS-BILL-2.0-S4
   In Monitor window: Continuous compliance checks

   Each agent will:
   - Run TDD: write failing tests → implement → refactor
   - Enforce linting (ruff)
   - Enforce type checking (pyright)
   - Target ≥85% code coverage
   - Commit with JIRA references
   - Create PR when done

📊 PROGRESS TRACKING:
   - Dashboard: Updated every 5s (burndown, ticket status, coverage)
   - Monitor: Checks CI/CD every 30s (type errors, lint, tests)
   - Real-time: Watch commits as agents work

EOF

echo ""
echo "🔗 Attaching to projectzero session..."
echo ""

tmux attach-session -t projectzero
