# Recovery and Resume Model

Temporal is the primary recovery mechanism. Temporal never loses state. Event sourcing. Every activity completion is a checkpoint.

## Architecture

```
React UI → FastAPI → Postgres → Temporal → Recovery Activities → Product Repo
```

Temporal event history = source of truth. Product repo `.claude/recovery/` = human-readable state for CLI tools.

## Why Temporal Makes This Work

Temporal uses event sourcing. Every workflow execution, every activity completion, every signal — recorded permanently. If anything crashes, Temporal replays the event history and picks up exactly where it left off.

No custom checkpoint logic needed for workflow state. Temporal handles it.

## Recovery State

Product repo `.claude/recovery/`:
```
current-stage.json      — Current workflow stage and progress
checkpoints/            — Human-readable state snapshots
active-work.json        — In-progress work items
failure-log.json        — Failure history
retry-state.json        — Retry counts per work item
```

This is supplementary. Temporal event history is the real state. These files exist for CLI commands and human inspection.

## Failure Classes

### 1. IDE Crash / Session End

Temporal continues running. Workflows do not stop. When you come back:
- `/resume` reloads context from Temporal workflow state
- Active workflows kept executing the whole time
- No work lost

### 2. Workflow Failure

Auto-retry: max 3 attempts per activity. Temporal retry policy handles this natively.

After 3 failures: escalate. Work item marked BLOCKED. Human notified with failure details and recommendation.

```
Activity fails → Temporal retries (max 3) → Escalate → Human decides
```

### 3. Integration Failure

Retry with exponential backoff (1s, 5s, 30s). Temporal activity retry policy.

If all retries fail: fallback to local file representation. Queue operation for later. When external system recovers, reconciliation runs.

```
API call fails → Retry with backoff (max 3) → Fallback to local → Queue for later
```

### 4. Context Overflow

When Claude context window fills up:
1. Temporal checkpoints current activity state
2. New session started
3. `/resume` loads checkpoint + Temporal workflow state
4. Continues from exact point of overflow

At most one activity's worth of re-work.

## Temporal Checkpoints

Temporal checkpoints every activity completion. Automatic. No configuration needed.

Additionally, human-readable checkpoints written to product repo at:
- Stage completion (after each workflow phase approved)
- Story completion (after governance chain passes)
- Before risky operations (deployments, migrations)

## Recovery Commands

### /resume

Resume from last known state.

1. Reads Temporal workflow state for active workflows
2. Reads `.claude/recovery/current-stage.json`
3. Reads `.claude/recovery/active-work.json`
4. Reconstructs context
5. Presents status report
6. Continues work

Use at the start of every session.

### /recover-ticket {ticket-id}

Recover state of a specific ticket.

1. Queries Temporal for workflow execution tied to ticket
2. Reads all related checkpoints
3. Reads retry state
4. Reads git branch state
5. Presents complete ticket status
6. Offers to continue

Use when a ticket seems stuck.

### /recover-workflow

Recover state of the entire workflow.

1. Queries Temporal for all active/completed/failed workflow executions
2. Reads all checkpoints, active work, retry states, failure logs
3. Produces comprehensive status report
4. Offers recommended next action

Use when you need the full picture.

## Bounded Retries

All retries bounded. No infinite loops.

| Mechanism | Max Retries | Backoff | On Exhaustion |
|---|---|---|---|
| Temporal activity | 3 | Exponential | Escalate to human |
| Governance gate (checker/reviewer) | 3 | None (immediate) | Block ticket |
| Full governance chain | 5 total | None | Block ticket |
| Integration sync | 3 | Exponential (1s, 5s, 30s) | Fallback to local |
| Debug resolution | 3 | None | Escalate to architect |

### Escalation Path

```
Retry limit hit
  → Work item BLOCKED in Temporal
  → Failure logged in product repo .claude/recovery/failure-log.json
  → User notified with details + recommendation
  → Human decides: fix, redesign, or deprioritize
```

## State Boundary

| Location | Contains |
|---|---|
| **Temporal** | Workflow state, event history, activity results (source of truth) |
| **Product Repo** `.claude/recovery/` | Human-readable checkpoints, failure logs, retry state |
| **Factory** | Recovery workflow definitions, retry policies |

Temporal never loses state. That's the whole point.
