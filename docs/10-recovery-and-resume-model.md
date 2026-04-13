# 10 - Recovery and Resume Model

## Overview

Claude sessions end. Networks fail. Context windows overflow. The factory is designed to survive all of these failures and resume without losing work. The recovery system uses checkpoints, bounded retries, and structured recovery commands to maintain continuity.

## Recovery Architecture

```
.claude/recovery/
  current-stage.json      # Current SPARC stage and progress
  checkpoints/            # Saved state at key milestones
    cp-20260122-001.json  # Checkpoint after spec completion
    cp-20260122-002.json  # Checkpoint after architecture approval
  active-work.json        # Currently in-progress work items
  failure-log.json        # Log of failures and recovery actions
  retry-state.json        # Current retry counts per work item
```

## Checkpoint System

### When Checkpoints Are Created

The factory creates checkpoints at these moments:

1. **Stage completion**: After each SPARC stage is approved
2. **Story completion**: After each story passes the governance chain
3. **Before risky operations**: Before deployments, migrations, or large refactors
4. **Periodic**: Every 30 minutes during active work (configurable)
5. **On command**: User can run `/checkpoint` to create a manual checkpoint

### Checkpoint Format

```json
{
  "checkpoint_id": "cp-20260122-002",
  "timestamp": "2026-01-22T14:30:00Z",
  "stage": "realization",
  "trigger": "story-completion",
  "product": "MyProduct",
  "state": {
    "current_module": "user-management",
    "current_story": "MYP-11",
    "stories_completed": ["MYP-11", "MYP-12"],
    "stories_remaining": ["MYP-13", "MYP-14", "MYP-15"],
    "active_branch": "feature/MYP-11-user-registration",
    "tests_passing": true,
    "governance_chain": {
      "checker": "PASS",
      "reviewer": "APPROVED",
      "approver": "APPROVED"
    }
  },
  "context_summary": "Completed user registration story (MYP-11). API endpoint at /api/auth/register accepts email/password, validates input with Pydantic, hashes password with bcrypt, stores in PostgreSQL. Tests: 12 unit, 4 integration, 2 E2E. All pass. Coverage: 94%.",
  "files_modified": [
    "src/api/routes/auth.py",
    "src/services/auth_service.py",
    "src/models/user.py",
    "tests/unit/test_auth_service.py",
    "tests/integration/test_auth_api.py",
    "tests/e2e/test_registration_flow.py"
  ],
  "memory_snapshot": {
    "debug_patterns_count": 3,
    "review_patterns_count": 2,
    "learnings_captured": 1
  }
}
```

### Active Work Tracking

The `active-work.json` file tracks what was in progress when the session ended:

```json
{
  "active_items": [
    {
      "ticket_id": "MYP-13",
      "type": "story",
      "status": "in-progress",
      "agent": "backend-engineer",
      "started_at": "2026-01-22T15:00:00Z",
      "last_activity": "2026-01-22T16:45:00Z",
      "progress": {
        "tests_written": true,
        "implementation_started": true,
        "implementation_complete": false,
        "files_in_progress": [
          "src/api/routes/profile.py",
          "src/services/profile_service.py"
        ],
        "description": "Implementing user profile endpoint. API route and service layer started. Repository layer not yet written. 6 of 10 tests passing."
      }
    }
  ]
}
```

## Failure Classes

The factory handles five classes of failure:

### 1. Network Failure

**Symptoms**: JIRA/Confluence/GitHub API calls fail with connection errors or timeouts.

**Handling**:
- Integration-agent switches to local fallback mode
- Pending sync operations are queued in product repo `.claude/delivery/*/sync_queue/`
- Work continues using local file representations
- When connectivity returns, reconciliation runs automatically

**No retry needed**: The factory continues working locally.

### 2. Context Window Overflow

**Symptoms**: Claude's context window fills up, causing the session to lose track of earlier context.

**Handling**:
- The factory writes essential state to `.claude/recovery/active-work.json` continuously
- When context overflow is detected (response quality degrades), the factory suggests starting a new session
- The new session starts by reading the last checkpoint and active-work state
- The context_summary field in the checkpoint provides a compressed summary of all prior work

**Recovery command**: `/resume`

### 3. Validation Failure

**Symptoms**: An artifact fails the governance chain (checker fails, reviewer blocks, approver rejects).

**Handling**:
- The failure is logged with specific reasons
- The work item is returned to the maker agent with feedback
- Retry count is incremented in `retry-state.json`
- Maximum 3 retries per governance gate
- After 3 failures, the work item is marked as BLOCKED and escalated

**Retry state**:
```json
{
  "MYP-13": {
    "checker_attempts": 2,
    "checker_last_failure": "Missing test for error path: invalid email format",
    "reviewer_attempts": 0,
    "approver_attempts": 0,
    "max_attempts": 3,
    "status": "retrying"
  }
}
```

### 4. Integration Failure

**Symptoms**: JIRA ticket creation fails, Confluence page update fails, GitHub PR creation fails.

**Handling**:
- The specific integration operation is queued for retry
- Maximum 3 retries with exponential backoff (1s, 5s, 30s)
- If all retries fail, the operation is logged as failed and falls back to local mode
- The reconciliation system will handle it when the integration recovers

### 5. IDE Session Restart

**Symptoms**: The user closes and reopens Claude Code, or the IDE crashes.

**Handling**:
- All state was already persisted to `.claude/recovery/`
- On next session start, the factory detects the last checkpoint
- The user runs `/resume` to pick up where they left off
- The factory reads the checkpoint, reconstructs context, and continues

## Recovery Commands

### /resume

Resume work from the last checkpoint.

**What it does**:
1. Reads `.claude/recovery/current-stage.json` to determine the current SPARC stage
2. Reads the latest checkpoint from `.claude/recovery/checkpoints/`
3. Reads `.claude/recovery/active-work.json` for in-progress items
4. Reconstructs the context summary for the Claude session
5. Presents the user with a status report:
   ```
   Resuming from checkpoint cp-20260122-002
   Stage: Realization
   Module: user-management
   Completed: MYP-11, MYP-12
   In progress: MYP-13 (backend-engineer, 60% complete)
   Remaining: MYP-14, MYP-15
   
   Ready to continue with MYP-13.
   ```
6. Continues work on the in-progress item

**When to use**: After any session interruption (IDE restart, context overflow, overnight break).

### /recover-ticket {ticket-id}

Recover the state of a specific ticket.

**What it does**:
1. Looks up the ticket in product repo `.claude/delivery/jira/issues/` or `.claude/delivery/features/`
2. Reads all related checkpoints
3. Reads the retry state
4. Reads the git branch state
5. Presents a complete status report for the ticket
6. Offers to continue work on the ticket

**When to use**: When you need to understand the state of a specific ticket or when a ticket is stuck.

### /recover-workflow

Recover the state of the entire workflow.

**What it does**:
1. Reads all checkpoints, active work, retry states, and failure logs
2. Produces a comprehensive status report covering all modules, active work, blocked items, failed items, and integration status
3. Offers to continue with the recommended action

**When to use**: When you are starting a new session and want a complete picture of where things stand.

## Bounded Retries

All retry mechanisms in the factory are bounded to prevent infinite loops:

| Mechanism | Maximum Retries | Backoff | Escalation |
|---|---|---|---|
| Checker validation | 3 | None (immediate) | Block ticket, log for human review |
| Reviewer validation | 3 | None (immediate) | Block ticket, log for human review |
| Full governance chain | 5 total iterations | None | Block ticket, log for human review |
| Integration sync | 3 | Exponential (1s, 5s, 30s) | Fall back to local mode |
| Pipeline task | 3 | Linear (10s) | Mark task as failed, notify ralph-controller |
| Debug resolution | 3 | None | Escalate to architect for redesign |

### Escalation Path

When retries are exhausted:

```
Retry limit reached
  |
  v
Work item marked as BLOCKED in product repo .claude/delivery/queue/
  |
  v
Failure logged in .claude/recovery/failure-log.json
  |
  v
Ralph-controller notifies user with details and recommendation
  |
  v
User decides: fix, redesign, or deprioritize
```

## Failure Log

All failures are logged for analysis:

```json
{
  "failures": [
    {
      "timestamp": "2026-01-22T16:30:00Z",
      "class": "validation",
      "ticket_id": "MYP-13",
      "gate": "checker",
      "attempt": 3,
      "reason": "Missing error handling for concurrent profile updates. Acceptance criteria require optimistic locking but implementation uses no locking.",
      "resolution": "pending",
      "escalated": true
    }
  ]
}
```

This log feeds into the memory system. If the same failure class appears repeatedly, it becomes a pattern that is promoted to project learning.

## Best Practices for Recovery

1. **Run `/resume` at the start of every session**: Even if you think you remember where you left off, the resume command ensures the factory's state is properly loaded.

2. **Do not fear session interruptions**: The checkpoint system captures state continuously. Losing a session loses at most 30 minutes of work.

3. **Read the recovery report carefully**: The `/recover-workflow` output tells you exactly where things stand. Trust it over your memory.

4. **When in doubt, `/recover-ticket`**: If a specific ticket seems stuck, use this command to get the full picture.

5. **Escalation is not failure**: When retries are exhausted, the factory is telling you that the problem needs human judgment. This is governance working correctly.
