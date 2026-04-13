# 12 - Pipeline and Runtime Model

## Overview

ProjectZeroFactory supports an optional pipeline mode for asynchronous task execution. This is useful for large products where multiple stories can be implemented in parallel, or where long-running tasks (test suites, deployments, security scans) should not block the interactive session.

Pipeline mode is enabled via:
```env
ENABLE_PIPELINE_MODE=true
```

## Architecture

### Components

```
FastAPI Workers (execute tasks)
  |
  v
Redis (message queue and cache)
  |
  v
Dagster (orchestration and scheduling)
  |
  v
.claude/runtime/ (state tracking)
  |
  v
product repo .claude/delivery/queue/ (work queue)
```

### FastAPI Workers

FastAPI workers are lightweight HTTP services that execute factory tasks asynchronously. They run as background processes and accept work items from the Redis queue.

**Configuration**:
```env
WORKER_HOST=0.0.0.0
WORKER_PORT=8000
WORKER_CONCURRENCY=4
```

**Worker responsibilities**:
- Execute implementation tasks (code generation for a specific story)
- Run test suites (unit, integration, E2E)
- Execute security scans
- Perform integration syncs (JIRA, Confluence, GitHub)
- Generate reports

**Worker endpoints**:
```
POST /tasks/execute     # Submit a task for execution
GET  /tasks/{id}/status # Check task status
GET  /tasks/{id}/result # Retrieve task result
POST /tasks/{id}/cancel # Cancel a running task
GET  /health            # Worker health check
```

### Redis Queue

Redis serves as both the message queue and a cache layer.

**Queue model**:
- Each task type has its own queue: `factory:queue:{task-type}`
- Task types: `implement`, `test`, `review`, `scan`, `sync`, `report`
- Tasks are JSON messages with a defined schema

**Task message format**:
```json
{
  "task_id": "task-20260122-001",
  "type": "implement",
  "ticket_id": "MYP-13",
  "agent": "backend-engineer",
  "priority": "normal",
  "payload": {
    "module": "user-management",
    "story_spec": "...",
    "architecture": "...",
    "data_model": "..."
  },
  "created_at": "2026-01-22T15:00:00Z",
  "timeout_ms": 300000,
  "retry_count": 0,
  "max_retries": 3
}
```

**Cache usage**:
- Agent context cached for fast retrieval
- Checkpoint data cached for quick resume
- Integration state cached to reduce API calls

**Configuration**:
```env
REDIS_URL=redis://localhost:6379
REDIS_PASSWORD=
```

### Dagster Orchestration

Dagster manages complex pipelines where tasks have dependencies and must execute in a specific order.

**Pipeline definitions** live in `.claude/pipelines/`:

```python
# Example: .claude/pipelines/implementation_pipeline.py
from dagster import job, op, In, Out

@op
def load_specification(context, ticket_id: str):
    """Load the story specification and related architecture."""
    # Read from product repo .claude/delivery/features/{ticket_id}.json
    # Read from .claude/modules/{module}/architecture.md
    return spec

@op(ins={"spec": In()})
def write_tests(context, spec):
    """Write tests based on the specification (TDD)."""
    # Invoke qa-engineer agent
    return test_files

@op(ins={"spec": In(), "tests": In()})
def implement_code(context, spec, tests):
    """Implement the code to pass the tests."""
    # Invoke backend-engineer or frontend-engineer agent
    return code_files

@op(ins={"code": In()})
def run_checker(context, code):
    """Run checker validation."""
    # Invoke checker agent
    return check_result

@op(ins={"code": In(), "check": In()})
def run_reviewer(context, code, check):
    """Run reviewer if checker passed."""
    if check.status != "PASS":
        raise Exception(f"Checker failed: {check.reason}")
    # Invoke reviewer agent
    return review_result

@job
def implementation_pipeline():
    spec = load_specification()
    tests = write_tests(spec)
    code = implement_code(spec, tests)
    check = run_checker(code)
    run_reviewer(code, check)
```

**Configuration**:
```env
DAGSTER_HOME=/opt/dagster/home
DAGSTER_HOST=localhost
DAGSTER_PORT=3000
```

### Pipeline Creation

```
/pipeline-create --type implementation --tickets MYP-13,MYP-14,MYP-15
```

This command:
1. Creates a Dagster pipeline that implements the specified tickets
2. Determines dependencies between tickets (e.g., MYP-14 depends on MYP-13)
3. Parallelizes independent tickets
4. Configures the governance chain for each ticket
5. Registers the pipeline with Dagster

## Runtime State

### .claude/runtime/

```
.claude/runtime/
  workers/
    worker-001.json       # Worker status and current task
    worker-002.json       # Worker status and current task
  pipelines/
    pipeline-001.json     # Pipeline status and progress
  scheduler/
    cron.json             # Scheduled tasks (nightly tests, weekly reports)
  health.json             # Overall runtime health status
```

**Worker state format**:
```json
{
  "worker_id": "worker-001",
  "status": "busy",
  "current_task": "task-20260122-001",
  "started_at": "2026-01-22T15:00:00Z",
  "cpu_usage": 45,
  "memory_usage_mb": 512,
  "tasks_completed": 12,
  "tasks_failed": 1,
  "uptime_seconds": 3600
}
```

**Pipeline state format**:
```json
{
  "pipeline_id": "pipeline-001",
  "type": "implementation",
  "status": "running",
  "created_at": "2026-01-22T15:00:00Z",
  "tickets": ["MYP-13", "MYP-14", "MYP-15"],
  "progress": {
    "MYP-13": {"status": "completed", "duration_ms": 120000},
    "MYP-14": {"status": "running", "started_at": "2026-01-22T15:02:00Z"},
    "MYP-15": {"status": "queued"}
  },
  "dependency_graph": {
    "MYP-14": ["MYP-13"],
    "MYP-15": []
  }
}
```

## Work Queue Model

### product repo .claude/delivery/queue/

The work queue is the primary mechanism for tracking work items, even when pipeline mode is disabled.

```
product repo .claude/delivery/queue/
  ready/                  # Items ready to be worked on
    MYP-13.json
    MYP-14.json
  active/                 # Items currently being worked on
    MYP-15.json
  completed/              # Items that have passed all governance gates
    MYP-11.json
    MYP-12.json
  failed/                 # Items that have exhausted retries
  blocked/                # Items blocked by dependencies or escalation
```

### Queue Item Format

```json
{
  "ticket_id": "MYP-13",
  "type": "story",
  "module": "user-management",
  "priority": 2,
  "dependencies": [],
  "assigned_agent": null,
  "status": "ready",
  "created_at": "2026-01-20T10:00:00Z",
  "queue_position": 3,
  "estimated_effort_hours": 4,
  "governance_state": {
    "checker": null,
    "reviewer": null,
    "approver": null
  }
}
```

### Queue Transitions

```
ready --> active --> completed
  |         |
  |         +--> failed (after max retries)
  |         |
  |         +--> blocked (dependency unmet or escalated)
  |
  +--> blocked (dependency not yet completed)
```

**Transition rules**:
- **ready -> active**: When an agent starts work (`/implement` or pipeline picks it up)
- **active -> completed**: When the approver approves
- **active -> failed**: When retry limit is exhausted
- **active -> blocked**: When a dependency is discovered or the work is escalated
- **ready -> blocked**: When a dependency item is not yet completed
- **blocked -> ready**: When the blocking condition is resolved
- **failed -> ready**: When a human resets the item for re-attempt

## Pipeline Mode vs. Interactive Mode

| Aspect | Interactive Mode | Pipeline Mode |
|---|---|---|
| Execution | One story at a time, synchronous | Multiple stories in parallel, async |
| Worker requirement | None | FastAPI workers required |
| Redis requirement | None | Required |
| Dagster requirement | None | Required for complex pipelines |
| Queue usage | `product repo .claude/delivery/queue/` (files) | Redis queues + file-based state |
| Recovery | Checkpoint-based | Checkpoint + Dagster run recovery |
| Best for | Small products, early stages | Large products, realization stage |

## Monitoring Pipeline Mode

### Health Check

```
/monitor --pipeline
```

Shows:
- Worker status (count, busy/idle, uptime)
- Queue depth per task type
- Active pipelines with progress
- Failed tasks requiring attention
- Resource utilization

### Pipeline Logs

Pipeline execution logs are stored in `.claude/runtime/pipelines/` and include:
- Task start/end timestamps
- Agent invocations and their results
- Governance chain outcomes
- Error details for failures

## Starting and Stopping Pipeline Mode

### Start Workers

```bash
# Start FastAPI workers
python -m factory.workers --concurrency 4

# Start Dagster
dagster dev -f .claude/pipelines/
```

### Stop Workers

```bash
# Graceful shutdown (finish current tasks)
kill -SIGTERM $(cat .claude/runtime/workers/pid)

# Force shutdown (after timeout)
kill -SIGKILL $(cat .claude/runtime/workers/pid)
```

### Draining the Queue

Before stopping workers, drain the queue:
```
/pipeline-drain
```

This stops accepting new tasks, waits for active tasks to complete, and writes final state to `product repo .claude/delivery/queue/`.
