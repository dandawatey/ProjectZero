# Workflow: Release Governance

## Purpose

Temporal workflow that manages the release approval chain for production deployments. Executes after deployment readiness passes. Coordinates sign-offs from engineering, product, and operations before authorizing a release.

## Temporal Identity

- **Workflow type**: `release_governance_workflow`
- **Task queue**: `governance-task-queue`
- **ID pattern**: `release-gov-{product_id}-{release_version}-{timestamp}`
- **Execution timeout**: 48 hours

## Stages

```
release_summary → engineering_signoff → product_signoff → ops_signoff → release_authorization → post_release_verification
```

### Stage 1: Release Summary

- **Activity**: `release_summary_activity`
- **Agent**: release-manager
- **Timeout**: start_to_close=30m
- **Input**: Feature list, deployment readiness report, changelog, risk assessment
- **Output**: Release summary document (what is shipping, known risks, rollback plan, stakeholder list)
- **Side effect**: Creates release record in Postgres, notifies stakeholders via React UI

### Stage 2: Engineering Sign-off

- **Signal**: `engineering_signoff_signal`
- **Approver**: tech-lead
- **Timeout**: 8 hours
- **Criteria**: All tests pass, code review complete, no critical bugs open, architecture review done
- **On timeout**: Escalate to CTO notification

### Stage 3: Product Sign-off

- **Signal**: `product_signoff_signal`
- **Approver**: product-owner
- **Timeout**: 8 hours
- **Criteria**: Acceptance criteria met, UX review complete, documentation updated, release notes approved
- **On timeout**: Escalate to CPO notification

### Stage 4: Ops Sign-off

- **Signal**: `ops_signoff_signal`
- **Approver**: sre-engineer
- **Timeout**: 4 hours
- **Criteria**: Deployment readiness passed, monitoring configured, runbooks updated, capacity sufficient
- **On timeout**: Escalate to VP Engineering notification

### Stage 5: Release Authorization

- **Activity**: `release_authorization_activity`
- **Agent**: release-manager
- **Timeout**: start_to_close=15m
- **Input**: All three sign-offs
- **Output**: Release authorization token, deployment window, deployment plan
- **Logic**: All three sign-offs must be APPROVE. Any REJECT sends the release back with feedback.

### Stage 6: Post-Release Verification

- **Activity**: `post_release_verification_activity`
- **Agent**: sre-engineer
- **Timeout**: start_to_close=1h
- **Input**: Deployment confirmation
- **Checks**:
  - Health check endpoints return 200
  - Error rate within baseline (< 1% increase)
  - Latency within baseline (< 10% increase for p99)
  - No new Sentry alerts in first 15 minutes
  - Smoke tests pass against production
- **Output**: Verification result (healthy/degraded/rollback_needed)
- **On `rollback_needed`**: Triggers rollback activity, notifies all stakeholders

## Workflow Definition

```python
@workflow.defn
class ReleaseGovernanceWorkflow:
    def __init__(self):
        self.current_stage = "release_summary"
        self.engineering_signoff = None
        self.product_signoff = None
        self.ops_signoff = None

    @workflow.run
    async def run(self, params: ReleaseParams) -> ReleaseResult:
        # Stage 1: Release Summary
        self.current_stage = "release_summary"
        summary = await workflow.execute_activity(
            release_summary_activity, args=[params],
            start_to_close_timeout=timedelta(minutes=30),
            retry_policy=RetryPolicy(maximum_attempts=2),
        )

        # Stage 2: Engineering Sign-off
        self.current_stage = "engineering_signoff"
        await workflow.execute_activity(
            create_signoff_request,
            args=[summary.release_id, "engineering", "tech-lead"],
            start_to_close_timeout=timedelta(seconds=30),
        )
        await workflow.wait_condition(lambda: self.engineering_signoff is not None)
        if self.engineering_signoff.verdict == "REJECT":
            return ReleaseResult(status="rejected", gate="engineering", feedback=self.engineering_signoff.feedback)

        # Stage 3: Product Sign-off
        self.current_stage = "product_signoff"
        await workflow.execute_activity(
            create_signoff_request,
            args=[summary.release_id, "product", "product-owner"],
            start_to_close_timeout=timedelta(seconds=30),
        )
        await workflow.wait_condition(lambda: self.product_signoff is not None)
        if self.product_signoff.verdict == "REJECT":
            return ReleaseResult(status="rejected", gate="product", feedback=self.product_signoff.feedback)

        # Stage 4: Ops Sign-off
        self.current_stage = "ops_signoff"
        await workflow.execute_activity(
            create_signoff_request,
            args=[summary.release_id, "ops", "sre-engineer"],
            start_to_close_timeout=timedelta(seconds=30),
        )
        await workflow.wait_condition(lambda: self.ops_signoff is not None)
        if self.ops_signoff.verdict == "REJECT":
            return ReleaseResult(status="rejected", gate="ops", feedback=self.ops_signoff.feedback)

        # Stage 5: Release Authorization
        self.current_stage = "release_authorization"
        auth = await workflow.execute_activity(
            release_authorization_activity,
            args=[summary, self.engineering_signoff, self.product_signoff, self.ops_signoff],
            start_to_close_timeout=timedelta(minutes=15),
        )

        # Execute deployment
        deployment = await workflow.execute_activity(
            execute_deployment_activity,
            args=[auth],
            start_to_close_timeout=timedelta(hours=1),
            retry_policy=RetryPolicy(maximum_attempts=2),
        )

        # Stage 6: Post-Release Verification
        self.current_stage = "post_release_verification"
        verification = await workflow.execute_activity(
            post_release_verification_activity,
            args=[deployment],
            start_to_close_timeout=timedelta(hours=1),
        )

        if verification.status == "rollback_needed":
            await workflow.execute_activity(
                execute_rollback_activity,
                args=[deployment],
                start_to_close_timeout=timedelta(minutes=30),
            )
            return ReleaseResult(status="rolled_back", reason=verification.issues)

        return ReleaseResult(
            status="released",
            version=params.version,
            verification=verification,
        )

    @workflow.signal
    async def engineering_signoff_signal(self, decision: SignoffDecision):
        self.engineering_signoff = decision

    @workflow.signal
    async def product_signoff_signal(self, decision: SignoffDecision):
        self.product_signoff = decision

    @workflow.signal
    async def ops_signoff_signal(self, decision: SignoffDecision):
        self.ops_signoff = decision

    @workflow.query
    def get_current_stage(self) -> str:
        return self.current_stage

    @workflow.query
    def get_signoff_status(self) -> dict:
        return {
            "engineering": self.engineering_signoff.verdict if self.engineering_signoff else "pending",
            "product": self.product_signoff.verdict if self.product_signoff else "pending",
            "ops": self.ops_signoff.verdict if self.ops_signoff else "pending",
        }
```

## Signals

| Signal | Source | Purpose |
|--------|--------|---------|
| `engineering_signoff_signal` | React UI via FastAPI | Tech lead approves/rejects |
| `product_signoff_signal` | React UI via FastAPI | Product owner approves/rejects |
| `ops_signoff_signal` | React UI via FastAPI | SRE approves/rejects |

## Queries

| Query | Returns |
|-------|---------|
| `get_current_stage` | Current stage name |
| `get_signoff_status` | Dict of all three signoff statuses |

## Postgres Tables

```sql
CREATE TABLE releases (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID NOT NULL,
    version TEXT NOT NULL,
    workflow_id TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    summary JSONB,
    created_at TIMESTAMPTZ DEFAULT now(),
    released_at TIMESTAMPTZ,
    correlation_id UUID NOT NULL
);

CREATE TABLE release_signoffs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    release_id UUID NOT NULL REFERENCES releases(id),
    gate TEXT NOT NULL CHECK (gate IN ('engineering', 'product', 'ops')),
    assigned_to TEXT NOT NULL,
    verdict TEXT CHECK (verdict IN ('APPROVE', 'REJECT')),
    feedback JSONB,
    requested_at TIMESTAMPTZ DEFAULT now(),
    decided_at TIMESTAMPTZ
);
```

## Release Types

| Type | Sign-off Requirements | Deployment Window |
|------|----------------------|-------------------|
| Major (x.0.0) | All three required | Scheduled maintenance window |
| Minor (0.x.0) | Engineering + Product | Business hours |
| Patch (0.0.x) | Engineering only | Any time |
| Hotfix | Engineering only (expedited) | Immediate |
