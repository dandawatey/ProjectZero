# INFRA: DevEx Improvements (Tools + Observability)

**Ticket**: SaaS-DEVEX-1  
**Type**: Infrastructure / Developer Experience  
**Priority**: P1 (Nice to have, but improves velocity)  
**Sprint**: Sprint 1 (Can run in parallel)  
**Story Points**: 5  
**Owner**: DevOps Lead  

---

## SaaS-DEVEX-1: TMUX + Multi-Worktree Dashboard

**Description**:
Set up TMUX with automated dashboard for monitoring parallel feature development across multiple git worktrees (SaaS-AUTH-2, SaaS-BILL-2, SaaS-FE-1).

### SPARC S1: Specification

**Acceptance Criteria**:
- [ ] TMUX installed (brew on macOS, apt on Linux)
- [ ] TMUX session "projectzero" created with 5 windows:
  1. Dashboard (live progress tracking)
  2. AUTH-2 worktree (auth-endpoints)
  3. BILL-2 worktree (billing-api)
  4. FE-1 worktree (auth-ui)
  5. Monitor (compliance + CI/CD tracking)
- [ ] Each window auto-cd to its worktree directory
- [ ] Dashboard shows:
  - [ ] Current sprint burndown (eng-days vs. target)
  - [ ] Ticket status (SaaS-AUTH-2, SaaS-BILL-2, SaaS-FE-1)
  - [ ] Test coverage per worktree (live updates)
  - [ ] Git branch status (commits, uncommitted files)
  - [ ] CI/CD pipeline status (GitHub Actions)
  - [ ] Alerts for blockers (linting, type errors, test failures)
- [ ] Keyboard shortcuts:
  - [ ] Ctrl+B n = next window
  - [ ] Ctrl+B p = previous window
  - [ ] Ctrl+B 0–4 = jump to window
  - [ ] Ctrl+B l = list windows
  - [ ] Ctrl+B d = detach session
- [ ] Tmux script: `.claude/launch-tmux-dashboard.sh`

### SPARC S2: Pseudocode

```bash
#!/bin/bash
# launch-tmux-dashboard.sh

# Kill existing session
tmux kill-session -t projectzero 2>/dev/null

# Create main session
tmux new-session -d -s projectzero -x 250 -y 50 -c $PROJECT_ROOT

# Window 0: Dashboard (main monitoring)
tmux send-keys -t projectzero:0 "clear && bash .claude/dashboard.sh" Enter

# Window 1: AUTH-2 worktree
tmux new-window -t projectzero:1 -n "AUTH-2" -c "platform/auth-endpoints"
tmux send-keys -t projectzero:1 "clear && git status && echo 'Ready for SaaS-AUTH-2 work'" Enter

# Window 2: BILL-2 worktree
tmux new-window -t projectzero:2 -n "BILL-2" -c "platform/billing-api"
tmux send-keys -t projectzero:2 "clear && git status && echo 'Ready for SaaS-BILL-2 work'" Enter

# Window 3: FE-1 worktree
tmux new-window -t projectzero:3 -n "FE-1" -c "platform/auth-ui"
tmux send-keys -t projectzero:3 "clear && git status && echo 'Ready for SaaS-FE-1 work'" Enter

# Window 4: Monitor (compliance + CI/CD)
tmux new-window -t projectzero:4 -n "MONITOR" -c "."
tmux send-keys -t projectzero:4 "clear && bash .claude/monitor.sh" Enter

# Attach session
tmux attach-session -t projectzero
```

### SPARC S3: Architecture

```
TMUX SESSION STRUCTURE:

Session: projectzero (5 windows, 250 cols × 50 rows)

Window 0: DASHBOARD (Live Progress)
├─ Top pane: Sprint 1 burndown chart
├─ Mid pane: Ticket statuses (AUTH-2, BILL-2, FE-1, ORG-1)
├─ Bottom pane: Key metrics (coverage, lint, type, test pass rate)
└─ Auto-refresh: Every 5 seconds

Window 1: AUTH-2 Worktree
├─ CWD: platform/auth-endpoints
├─ Branch: feature/SaaS-AUTH-2
├─ Ready for: pytest, code editing, git commands
└─ Layout: Single pane (full window)

Window 2: BILL-2 Worktree
├─ CWD: platform/billing-api
├─ Branch: feature/SaaS-BILL-2
├─ Ready for: pytest, code editing, git commands
└─ Layout: Single pane (full window)

Window 3: FE-1 Worktree
├─ CWD: platform/auth-ui
├─ Branch: feature/SaaS-FE-1
├─ Ready for: npm test, code editing, git commands
└─ Layout: Single pane (full window)

Window 4: MONITOR
├─ CWD: . (project root)
├─ Shows: CI/CD status, test results, coverage
├─ Auto-runs: pytest, ruff, pyright in loop
└─ Alerts: Red text on failures, Slack notifications

KEYBOARD NAVIGATION:
  Prefix: Ctrl+B

  Ctrl+B 0 → Window 0 (Dashboard)
  Ctrl+B 1 → Window 1 (AUTH-2)
  Ctrl+B 2 → Window 2 (BILL-2)
  Ctrl+B 3 → Window 3 (FE-1)
  Ctrl+B 4 → Window 4 (Monitor)
  
  Ctrl+B n → Next window
  Ctrl+B p → Previous window
  Ctrl+B l → Last window (toggle)
  
  Ctrl+B % → Split pane (vertical)
  Ctrl+B " → Split pane (horizontal)
  Ctrl+B ← → Navigate panes
  Ctrl+B d → Detach session
  
  In new terminal:
    tmux attach -t projectzero
```

### SPARC S4: Refinement (Implementation)

**File**: `.claude/launch-tmux-dashboard.sh`

```bash
#!/bin/bash
set -e

PROJECT_ROOT="/Users/yogesh/1_Code/Office/i-ProjectZero/ProjectZeroFactory"
cd "$PROJECT_ROOT"

# Kill existing session
echo "🔄 Killing existing projectzero session..."
tmux kill-session -t projectzero 2>/dev/null || true

# Create new session (large enough for 3-column layout)
echo "📺 Creating TMUX session (projectzero)..."
tmux new-session -d -s projectzero -x 250 -y 50

# Window 0: Dashboard
echo "📊 Setting up Dashboard window..."
tmux send-keys -t projectzero:0 "cd '$PROJECT_ROOT'" Enter
tmux send-keys -t projectzero:0 "clear" Enter
tmux send-keys -t projectzero:0 "bash .claude/dashboard.sh" Enter

# Window 1: AUTH-2 Worktree
echo "🔐 Setting up AUTH-2 window..."
tmux new-window -t projectzero:1 -n "AUTH-2"
tmux send-keys -t projectzero:1 "cd '$PROJECT_ROOT/platform/auth-endpoints'" Enter
tmux send-keys -t projectzero:1 "clear && git status" Enter

# Window 2: BILL-2 Worktree
echo "💳 Setting up BILL-2 window..."
tmux new-window -t projectzero:2 -n "BILL-2"
tmux send-keys -t projectzero:2 "cd '$PROJECT_ROOT/platform/billing-api'" Enter
tmux send-keys -t projectzero:2 "clear && git status" Enter

# Window 3: FE-1 Worktree
echo "🎨 Setting up FE-1 window..."
tmux new-window -t projectzero:3 -n "FE-1"
tmux send-keys -t projectzero:3 "cd '$PROJECT_ROOT/platform/auth-ui'" Enter
tmux send-keys -t projectzero:3 "clear && git status" Enter

# Window 4: Monitor
echo "📡 Setting up Monitor window..."
tmux new-window -t projectzero:4 -n "MONITOR"
tmux send-keys -t projectzero:4 "cd '$PROJECT_ROOT'" Enter
tmux send-keys -t projectzero:4 "clear && bash .claude/monitor.sh" Enter

# List windows
echo "✅ TMUX session ready!"
tmux list-windows -t projectzero

# Attach
echo ""
echo "🚀 Attaching to projectzero session..."
echo "   Navigation:"
echo "   - Ctrl+B 0 = Dashboard"
echo "   - Ctrl+B 1 = AUTH-2"
echo "   - Ctrl+B 2 = BILL-2"
echo "   - Ctrl+B 3 = FE-1"
echo "   - Ctrl+B 4 = Monitor"
echo "   - Ctrl+B d = Detach"
echo ""

tmux attach-session -t projectzero
```

**File**: `.claude/dashboard.sh`

```bash
#!/bin/bash
# Live sprint dashboard (refreshes every 5 seconds)

PROJECT_ROOT="/Users/yogesh/1_Code/Office/i-ProjectZero/ProjectZeroFactory"

while true; do
  clear
  
  echo "╔════════════════════════════════════════════════════════════╗"
  echo "║       SPRINT 1 PARALLEL BUILD DASHBOARD (May 1–7)         ║"
  echo "╚════════════════════════════════════════════════════════════╝"
  echo ""
  
  # Burndown Chart
  echo "📊 BURNDOWN (Target: 28 eng-days)"
  echo "   Day 1:  ███░░░░░░░ 3.5/28 (12%)"
  echo "   Day 2:  ██████░░░░ 7.5/28 (27%)"
  echo "   Day 3:  █████████░ 10/28  (36%)"
  echo "   Day 4:  ███████████████░░ 19/28 (68%)"
  echo "   Day 5:  ██████████████████ 21/28 (75%)"
  echo ""
  
  # Ticket Status
  echo "🎫 TICKET STATUS:"
  cd "$PROJECT_ROOT"
  
  # SaaS-ORG-1
  echo -n "   ✅ SaaS-ORG-1 (DONE):        "
  git log --oneline feature/SaaS-ORG-1 2>/dev/null | wc -l | xargs echo "commits"
  
  # SaaS-AUTH-2
  echo -n "   🔄 SaaS-AUTH-2 (IN PROGRESS): "
  if [ -d "platform/auth-endpoints" ]; then
    (cd platform/auth-endpoints && git log --oneline -1 2>/dev/null | cut -c1-50)
  else
    echo "Worktree not found"
  fi
  
  # SaaS-BILL-2
  echo -n "   🔄 SaaS-BILL-2 (IN PROGRESS): "
  if [ -d "platform/billing-api" ]; then
    (cd platform/billing-api && git log --oneline -1 2>/dev/null | cut -c1-50)
  else
    echo "Worktree not found"
  fi
  
  # SaaS-FE-1
  echo -n "   ⬜ SaaS-FE-1 (PENDING):       "
  if [ -d "platform/auth-ui" ]; then
    (cd platform/auth-ui && git log --oneline -1 2>/dev/null | cut -c1-50)
  else
    echo "Worktree not found"
  fi
  
  echo ""
  
  # Test Coverage
  echo "📈 CODE QUALITY (per worktree):"
  
  if [ -d "platform/auth-endpoints" ]; then
    echo -n "   AUTH-2 coverage: "
    (cd platform/auth-endpoints && pytest --cov=app --cov-report=term-missing 2>/dev/null | grep TOTAL | awk '{print $(NF-1)}') || echo "N/A"
  fi
  
  if [ -d "platform/billing-api" ]; then
    echo -n "   BILL-2 coverage: "
    (cd platform/billing-api && pytest --cov=app --cov-report=term-missing 2>/dev/null | grep TOTAL | awk '{print $(NF-1)}') || echo "N/A"
  fi
  
  echo ""
  echo "🔄 Last updated: $(date '+%H:%M:%S')"
  echo "   Refreshing in 5 seconds... (Ctrl+C to stop)"
  
  sleep 5
done
```

**File**: `.claude/monitor.sh`

```bash
#!/bin/bash
# CI/CD + Compliance monitoring (runs in background)

PROJECT_ROOT="/Users/yogesh/1_Code/Office/i-ProjectZero/ProjectZeroFactory"

while true; do
  clear
  
  echo "╔════════════════════════════════════════════════════════════╗"
  echo "║            CI/CD + COMPLIANCE MONITOR                      ║"
  echo "╚════════════════════════════════════════════════════════════╝"
  echo ""
  
  cd "$PROJECT_ROOT"
  
  # Check each worktree
  for worktree in "platform/auth-endpoints" "platform/billing-api" "platform/auth-ui"; do
    if [ -d "$worktree" ]; then
      echo "🔍 Checking: $worktree"
      
      cd "$worktree"
      
      # Git status
      echo -n "   Git status: "
      if [ -z "$(git status --porcelain)" ]; then
        echo "✅ Clean"
      else
        echo "⚠️  Uncommitted changes:"
        git status --porcelain | head -3
      fi
      
      # Type checking
      echo -n "   Type check: "
      if pyright --outputstyle=json . 2>/dev/null | grep -q '"generalDiagnostics": \[\]'; then
        echo "✅ No errors"
      else
        echo "❌ Type errors found"
        pyright . 2>/dev/null | grep "error:" | head -2
      fi
      
      # Linting
      echo -n "   Linting: "
      if ruff check . 2>/dev/null | wc -l | grep -q "^0$"; then
        echo "✅ No errors"
      else
        echo "❌ Lint errors found"
        ruff check . 2>/dev/null | head -2
      fi
      
      # Tests
      echo -n "   Tests: "
      if pytest 2>/dev/null | grep -q "passed"; then
        echo "✅ Passing"
      else
        echo "⚠️  Check manually"
      fi
      
      cd "$PROJECT_ROOT"
      echo ""
    fi
  done
  
  echo "⏰ Last check: $(date '+%H:%M:%S')"
  echo "   Next check in 30 seconds... (Ctrl+C to stop)"
  
  sleep 30
done
```

### SPARC S5: Completion

- [ ] Install TMUX (if not present)
- [ ] Create `.claude/launch-tmux-dashboard.sh`
- [ ] Create `.claude/dashboard.sh`
- [ ] Create `.claude/monitor.sh`
- [ ] Test: Run `bash .claude/launch-tmux-dashboard.sh`
- [ ] Verify all 5 windows load correctly
- [ ] Test keyboard navigation (Ctrl+B 0–4)
- [ ] Document in README.md
- [ ] Commit to main

---

## Installation Steps

```bash
# macOS
brew install tmux

# Linux (Ubuntu/Debian)
sudo apt-get install tmux

# Verify
tmux -V

# Test dashboard
cd /Users/yogesh/1_Code/Office/i-ProjectZero/ProjectZeroFactory
bash .claude/launch-tmux-dashboard.sh
```

---

**Status**: Ready to implement  
**Timeline**: 2 hours  
**Owner**: DevOps Lead  
**Depends on**: TMUX available on system
