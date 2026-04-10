# Execution Model

## Work Flow

```
Ticket Created → Queued (ready) → Assigned (active) → Implemented → Checked → Reviewed → Approved → Merged → Deployed
```

## Queue States

| State | File | Description |
|-------|------|-------------|
| Ready | `queue/ready.json` | Dependencies met, waiting for agent assignment |
| Active | `queue/active.json` | Agent working on it |
| Blocked | `queue/blocked.json` | Waiting on dependency or external input |
| Completed | `queue/completed.json` | Done, passed all gates |
| Failed | `queue/failed.json` | Failed, needs recovery |

## Execution Steps

### 1. Ticket Creation (during /spec)
- Product Manager creates tickets from specifications
- Each ticket has: ID, description, acceptance criteria, priority, story points, module, dependencies
- Stored in `.claude/delivery/jira/issues/` (local) and synced to JIRA (if configured)

### 2. Queue Assignment (Ralph Controller)
- Ralph reads `ready.json`, checks dependencies
- Assigns to appropriate agent based on ticket type:
  - API/backend tickets → backend-engineer
  - UI tickets → frontend-engineer
  - Pipeline tickets → data-engineer
  - Infra tickets → devops-engineer
- Moves ticket from ready → active
- Max 3 parallel agents (configurable)

### 3. Implementation (Engineer Agent)
- Agent reads ticket, loads relevant memory
- Follows TDD: write failing test → implement → pass → refactor
- Commits with ticket ID in message
- Creates PR linking to ticket
- Writes checkpoint to `.claude/recovery/active-ticket.json`

### 4. Check (Checker Agent)
- Runs all tests (unit + integration)
- Runs linter (zero errors required)
- Runs security scan
- Validates ticket acceptance criteria met
- Validates API contracts honored
- **Pass**: Moves to review. **Fail**: Returns to maker with specific findings.

### 5. Review (Reviewer Agent)
- Reviews code quality and readability
- Validates architecture alignment
- Checks test coverage (≥80%)
- Verifies documentation updated
- Checks design system compliance (UI work)
- **Pass**: Moves to approve. **Fail**: Returns to maker with actionable feedback.

### 6. Approve (Approver Agent)
- Validates business requirements fully met
- Confirms governance chain complete
- Authorizes merge
- **Pass**: PR merged. **Fail**: Returns to maker.

### 7. Merge
- Squash merge to develop branch
- Delete feature branch
- Update ticket status to Done
- Move queue item to completed
- Update progress report

### 8. Deploy (via /release)
- Batch completed work into release
- Full test suite on release branch
- Security scan
- Deploy to staging → smoke test → deploy to production
- Health check verification

## Parallel Execution

- Multiple tickets can be active simultaneously (up to `maxParallelAgents`)
- Tickets with dependencies must wait (blocked queue)
- Cross-module work can run in parallel if no data dependency
- Ralph tracks the dependency graph in `.claude/runtime/execution-graph.md`

## Failure Handling

- Failed check/review → ticket returns to maker, retry count incremented
- 3 consecutive failures → escalate to user
- Integration failure → queue for retry, continue with local-first
- Agent context overflow → checkpoint and restart in new session
