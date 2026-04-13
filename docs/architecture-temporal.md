# Architecture: Temporal Execution Engine

## System Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                        REACT CONTROL TOWER                           │
│  ┌──────────┐ ┌──────────────┐ ┌────────────┐ ┌──────────────────┐  │
│  │ Features │ │ Approval     │ │ Workflows  │ │ Release Board    │  │
│  │ Dashboard│ │ Queue        │ │ Detail     │ │                  │  │
│  └────┬─────┘ └──────┬───────┘ └─────┬──────┘ └────────┬─────────┘  │
└───────┼──────────────┼───────────────┼──────────────────┼────────────┘
        │ HTTP/SSE     │               │                  │
┌───────▼──────────────▼───────────────▼──────────────────▼────────────┐
│                         FASTAPI BACKEND                               │
│  ┌──────────┐ ┌──────────────┐ ┌────────────┐ ┌──────────────────┐  │
│  │ Feature  │ │ Approval     │ │ Workflow   │ │ Release          │  │
│  │ API      │ │ API          │ │ API        │ │ API              │  │
│  └────┬─────┘ └──────┬───────┘ └─────┬──────┘ └────────┬─────────┘  │
│       │              │               │                  │            │
│  ┌────▼──────────────▼───────────────▼──────────────────▼─────────┐  │
│  │                    SERVICE LAYER                                │  │
│  │  ┌──────────────────┐  ┌──────────────────┐                    │  │
│  │  │ Temporal Client  │  │ Sync Layer       │                    │  │
│  │  │ (start, signal,  │  │ (receive updates │                    │  │
│  │  │  query)          │  │  from workers)   │                    │  │
│  │  └────────┬─────────┘  └────────▲─────────┘                    │  │
│  └───────────┼─────────────────────┼──────────────────────────────┘  │
│              │                     │                                  │
│  ┌───────────▼─────────────────────┼──────────────────────────────┐  │
│  │              POSTGRES                                          │  │
│  │  features | approvals | releases | audit_log | stages          │  │
│  └────────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────────┘
               │                     ▲
               │ Temporal Client     │ HTTP (sync layer)
               ▼                     │
┌──────────────────────────────────────────────────────────────────────┐
│                       TEMPORAL SERVER                                 │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │  Workflow Engine                                               │  │
│  │  - Workflow state (event history)                              │  │
│  │  - Activity scheduling                                         │  │
│  │  - Signal dispatch                                             │  │
│  │  - Timer management                                            │  │
│  │  - Retry orchestration                                         │  │
│  └──────────────────────┬─────────────────────────────────────────┘  │
│                         │ Task Queues                                 │
│  ┌──────────┐ ┌────────┴───┐ ┌───────────┐ ┌──────────┐            │
│  │ feature- │ │ qa-task-   │ │ review-   │ │ release- │            │
│  │ dev-task │ │ queue      │ │ task-     │ │ task-    │            │
│  │ -queue   │ │            │ │ queue     │ │ queue    │            │
│  └────┬─────┘ └─────┬──────┘ └─────┬─────┘ └────┬─────┘            │
└───────┼─────────────┼──────────────┼────────────┼────────────────────┘
        │             │              │            │
┌───────▼─────────────▼──────────────▼────────────▼────────────────────┐
│                       TEMPORAL WORKERS                                │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐                 │
│  │ Engineering  │ │ QA Worker    │ │ Governance   │                 │
│  │ Worker       │ │              │ │ Worker       │                 │
│  │ - impl       │ │ - test_plan  │ │ - approval   │                 │
│  │ - fix        │ │ - unit_test  │ │ - review     │                 │
│  │ - arch       │ │ - e2e_test   │ │ - signoff    │                 │
│  └──────────────┘ └──────────────┘ └──────────────┘                 │
│  Each worker: poll queue → execute activity → sync via FastAPI       │
└──────────────────────────────────────────────────────────────────────┘
```

## Temporal as Execution Engine

### Why Temporal

Temporal provides durable execution. Workflow code runs as normal Python but survives process crashes, network failures, and server restarts. This eliminates:

- Custom state machine code
- Manual retry logic
- Distributed transaction coordination
- State recovery after failures
- Cron-based polling for completion

### Core Concepts

#### Workflows

A workflow is a durable function that orchestrates a sequence of activities. Workflow code must be deterministic -- no random values, no system time, no direct I/O. All side effects happen in activities.

```python
@workflow.defn
class FeatureDevelopmentWorkflow:
    @workflow.run
    async def run(self, params: FeatureParams) -> FeatureResult:
        # This code survives crashes. Temporal replays from event history.
        spec = await workflow.execute_activity(specification_activity, ...)
        approval = await workflow.execute_child_workflow(MCRAWorkflow.run, ...)
        impl = await workflow.execute_activity(implementation_activity, ...)
        return FeatureResult(...)
```

#### Activities

An activity is a function that performs actual work -- calling APIs, running agents, writing files. Activities can fail and are retried by Temporal per the configured retry policy.

```python
@activity.defn
async def implementation_activity(params: ImplParams) -> ImplResult:
    # This code does real work. It can fail. Temporal retries it.
    agent_result = await invoke_claude_agent("backend-engineer", params)
    await sync_to_fastapi(agent_result)
    return ImplResult(...)
```

#### Workers

Workers are Python processes that poll Temporal task queues and execute activities. Multiple workers can poll the same queue for horizontal scaling.

```python
async def main():
    client = await Client.connect("temporal:7233")
    worker = Worker(
        client,
        task_queue="engineering-task-queue",
        workflows=[FeatureDevelopmentWorkflow],
        activities=[implementation_activity, specification_activity],
    )
    await worker.run()
```

#### Task Queues

Task queues route activities to appropriate workers:

| Queue | Workers | Activities |
|-------|---------|------------|
| `feature-dev-task-queue` | Engineering workers | Feature workflow orchestration |
| `product-task-queue` | Product workers | Intake, specification |
| `design-task-queue` | Design workers | Design activities |
| `architecture-task-queue` | Architecture workers | Architecture activities |
| `engineering-task-queue` | Engineering workers | Implementation, fix, diagnosis |
| `qa-task-queue` | QA workers | All test activities |
| `review-task-queue` | Review workers | Code review, security review |
| `governance-task-queue` | Governance workers | MCRA, release sign-offs |
| `release-task-queue` | Release workers | Deployment, release activities |

## State Sync Pattern

Temporal is the source of truth for workflow execution state. Postgres is the source of truth for business state (what the UI reads). The sync layer bridges them.

### Pattern: Temporal -> Sync Layer -> FastAPI -> Postgres

```
Temporal Worker
  │
  │ Activity completes
  │
  ▼
Sync Layer (in worker process)
  │
  │ POST /api/internal/sync/stage-completion
  │ Headers: X-Idempotency-Key: {correlation_id}
  │ Body: { feature_id, stage, status, result, correlation_id }
  │
  ▼
FastAPI Sync Endpoint
  │
  │ 1. Check idempotency key in postgres
  │ 2. If already processed, return 200 (no-op)
  │ 3. If new, write to postgres in transaction
  │ 4. Return 200
  │
  ▼
Postgres
  │
  │ INSERT INTO stage_completions (...)
  │ UPDATE features SET current_stage = ...
  │ INSERT INTO audit_log (...)
  │
  ▼
SSE Notifier
  │
  │ Push update to connected React clients
```

### Idempotent Updates with correlation_id

Every sync operation carries a `correlation_id` (UUID). The sync endpoint checks if this ID has already been processed before writing. This ensures:

- Activity retries do not create duplicate state
- Network retries are safe
- At-least-once delivery becomes effectively-once processing

```python
async def sync_stage_completion(payload: SyncPayload):
    existing = await db.execute(
        select(SyncLog).where(SyncLog.correlation_id == payload.correlation_id)
    )
    if existing.scalar_one_or_none():
        return {"status": "already_processed"}

    async with db.begin():
        db.add(SyncLog(correlation_id=payload.correlation_id, payload=payload.dict()))
        await update_feature_stage(payload.feature_id, payload.stage, payload.result)
        await insert_audit_log(payload)

    return {"status": "processed"}
```

### Postgres Schema for Sync

```sql
CREATE TABLE sync_log (
    correlation_id UUID PRIMARY KEY,
    payload JSONB NOT NULL,
    processed_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE stage_completions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    feature_id UUID NOT NULL REFERENCES features(id),
    stage TEXT NOT NULL,
    status TEXT NOT NULL,
    result JSONB,
    correlation_id UUID NOT NULL UNIQUE,
    completed_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE audit_log (
    id BIGSERIAL PRIMARY KEY,
    entity_type TEXT NOT NULL,
    entity_id UUID NOT NULL,
    action TEXT NOT NULL,
    actor TEXT NOT NULL,
    details JSONB,
    correlation_id UUID,
    created_at TIMESTAMPTZ DEFAULT now()
);
```

## Signal-Based Approvals

Human decisions (approve, reject, sign-off) flow from React UI through FastAPI to Temporal as signals.

### Flow

```
1. Workflow reaches approval point
   └─> Executes create_approval_request activity
   └─> Activity POSTs to FastAPI: creates approval_request row in Postgres
   └─> Workflow calls: await workflow.wait_condition(lambda: self.decision is not None)

2. React UI displays pending approval
   └─> GET /api/approvals/pending returns list
   └─> User sees approval request with context (artifact, stage, requester)

3. User clicks Approve/Reject in React UI
   └─> POST /api/approvals/{id} with {verdict, feedback}

4. FastAPI processes decision
   └─> Updates approval_request row in Postgres
   └─> Gets workflow_id from approval_request
   └─> temporal_client.get_workflow_handle(workflow_id).signal("checker_signal", decision)

5. Temporal delivers signal to workflow
   └─> self.decision = decision
   └─> wait_condition resolves
   └─> Workflow continues
```

### FastAPI Signal Endpoint

```python
@router.post("/api/approvals/{approval_id}")
async def submit_approval(approval_id: UUID, body: ApprovalSubmission, db: AsyncSession, temporal: Client):
    approval = await db.get(ApprovalRequest, approval_id)
    if not approval or approval.status != "pending":
        raise HTTPException(404)

    approval.verdict = body.verdict
    approval.feedback = body.feedback
    approval.decided_at = datetime.utcnow()
    approval.status = "approved" if body.verdict == "APPROVE" else "rejected"
    await db.commit()

    handle = temporal.get_workflow_handle(approval.workflow_id)
    signal_name = f"{approval.gate}_signal"
    await handle.signal(signal_name, GateDecision(verdict=body.verdict, feedback=body.feedback))

    return {"status": "signal_sent"}
```

## Child Workflows for Governance

Governance (MCRA, QA validation, deployment readiness) runs as child workflows:

```
feature_development_workflow (parent)
  │
  ├── maker_checker_reviewer_approver_workflow (child) -- spec governance
  ├── maker_checker_reviewer_approver_workflow (child) -- design governance
  ├── maker_checker_reviewer_approver_workflow (child) -- arch governance
  ├── qa_validation_workflow (child) -- testing
  ├── maker_checker_reviewer_approver_workflow (child) -- code review governance
  ├── deployment_readiness_workflow (child) -- pre-deploy checks
  └── release_governance_workflow (child) -- release sign-offs
```

Child workflow benefits:
- **Isolation**: Child failure does not crash parent. Parent handles the result.
- **Reuse**: Same MCRA workflow used for spec, design, arch, and code governance.
- **Visibility**: Each child has its own workflow ID, queryable independently.
- **Cancellation**: Parent can cancel children. Children can complete independently.

## Retry and Failure Handling

### Activity Retry Policy

```python
RetryPolicy(
    initial_interval=timedelta(seconds=1),      # First retry after 1s
    backoff_coefficient=2.0,                      # Double each retry
    maximum_interval=timedelta(minutes=5),        # Cap at 5m between retries
    maximum_attempts=3,                           # Max 3 attempts total
    non_retryable_error_types=["ValueError"],     # Don't retry validation errors
)
```

### Failure Hierarchy

| Failure Type | Handling |
|-------------|----------|
| Activity timeout | Temporal retries per policy. After exhaustion, activity fails. Workflow receives ActivityError. |
| Activity application error | Temporal retries unless error type is in non_retryable_error_types. |
| Heartbeat timeout | Worker presumed dead. Activity rescheduled to another worker. |
| Workflow timeout | Workflow fails. Must be restarted manually or by parent. |
| Child workflow failure | Parent receives ChildWorkflowError. Parent decides: retry child, fail, or escalate. |
| Temporal server outage | Workers reconnect automatically. In-flight activities resume. No data loss. |
| Worker crash | Temporal reschedules activity to another worker. Workflow state is preserved. |

### Non-Retryable Errors

These errors should NOT be retried:
- Validation failures (bad input data)
- Authorization failures (wrong permissions)
- Business rule violations (e.g., trying to approve own work)

Mark them explicitly:

```python
raise ApplicationError("Cannot approve own work", type="BusinessRuleViolation", non_retryable=True)
```

## Observability

### Prometheus Metrics

Exported by workers and FastAPI:

| Metric | Type | Description |
|--------|------|-------------|
| `workflow_started_total` | Counter | Workflows started by type |
| `workflow_completed_total` | Counter | Workflows completed by type and status |
| `workflow_duration_seconds` | Histogram | Workflow duration by type |
| `activity_execution_seconds` | Histogram | Activity duration by name |
| `activity_failures_total` | Counter | Activity failures by name and error type |
| `approval_pending_count` | Gauge | Currently pending approvals by gate |
| `approval_latency_seconds` | Histogram | Time from request to decision |
| `sync_operations_total` | Counter | Sync layer operations by status |

### Grafana Dashboards

| Dashboard | Panels |
|-----------|--------|
| Workflow Pipeline | Active workflows by stage, completion rate, average duration |
| Approval Latency | Pending count, median decision time, SLA breach alerts |
| Release Velocity | Releases per week, rollback rate, deploy duration |
| Worker Health | Worker count, task queue depth, activity throughput |

### Sentry Integration

Every activity wraps execution in a Sentry transaction:

```python
@activity.defn
async def implementation_activity(params: ImplParams) -> ImplResult:
    with sentry_sdk.start_transaction(op="temporal.activity", name="implementation_activity"):
        sentry_sdk.set_context("temporal", {
            "workflow_id": activity.info().workflow_id,
            "activity_id": activity.info().activity_id,
            "task_queue": activity.info().task_queue,
        })
        # ... activity logic
```

### OpenTelemetry

Temporal Python SDK has built-in OpenTelemetry support. Configure the interceptor:

```python
from temporalio.contrib.opentelemetry import TracingInterceptor

client = await Client.connect(
    "temporal:7233",
    interceptors=[TracingInterceptor()],
)
```

This produces distributed traces spanning:
- React UI request -> FastAPI handler -> Temporal workflow start
- Temporal activity execution -> Agent invocation -> Sync callback
- Signal delivery from FastAPI -> Temporal workflow continuation

Traces are exported to an OTLP collector and visualized in Grafana Tempo or Jaeger.
