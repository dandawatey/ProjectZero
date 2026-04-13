# Workflow: Feature Development

## Purpose

The primary workflow in ProjectZeroFactory. Every new feature request starts a `feature_development_workflow` in Temporal. This workflow orchestrates the complete lifecycle from intake to deployed, tested, approved production code.

## Temporal Identity

- **Workflow type**: `feature_development_workflow`
- **Task queue**: `feature-dev-task-queue`
- **ID pattern**: `feature-{product_id}-{feature_id}-{timestamp}`
- **Execution timeout**: 7 days (configurable per product)
- **Run timeout**: 7 days

## Stages and Activities

### Stage 1: Intake

- **Activity**: `intake_activity`
- **Agent**: product-manager
- **Task queue**: `product-task-queue`
- **Timeout**: start_to_close=30m
- **Input**: Feature request (title, description, requester, priority)
- **Output**: Structured feature record with acceptance criteria, priority score, dependency map
- **Side effects**: Creates feature record in Postgres via sync layer

### Stage 2: Specification

- **Activity**: `specification_activity`
- **Agents**: spec-writer (primary), product-manager (review)
- **Task queue**: `product-task-queue`
- **Timeout**: start_to_close=2h
- **Input**: Feature record from intake
- **Output**: Full specification document (user stories, acceptance criteria, edge cases, non-functional requirements)
- **Governance**: Triggers MCRA child workflow on spec artifact
- **Child workflow**: `mcra-{workflow_id}-spec-{spec_id}`

### Stage 3: Design

- **Activity**: `design_activity`
- **Agents**: ux-designer, frontend-designer
- **Task queue**: `design-task-queue`
- **Timeout**: start_to_close=4h
- **Input**: Approved specification
- **Output**: Wireframes, component specs, interaction patterns, design tokens
- **Governance**: Triggers MCRA child workflow on design artifacts

### Stage 4: Architecture

- **Activity**: `architecture_activity`
- **Agents**: architect (primary), security-reviewer (secondary)
- **Task queue**: `architecture-task-queue`
- **Timeout**: start_to_close=4h
- **Input**: Approved spec + approved design
- **Output**: ADRs, API contracts, data models, component boundaries, security assessment
- **Governance**: Triggers MCRA child workflow on architecture artifacts

### Stage 5: Implementation

- **Activity**: `implementation_activity`
- **Agents**: backend-engineer, frontend-engineer (parallel when independent)
- **Task queue**: `engineering-task-queue`
- **Timeout**: start_to_close=8h, heartbeat=5m
- **Input**: Approved architecture, ticket list
- **Output**: Source code, unit tests, integration points
- **Pattern**: TDD enforced -- test written before implementation code
- **Heartbeat**: Agent sends heartbeat every 5m with progress update. Missed heartbeat triggers alert.

### Stage 6: Testing

- **Activity**: `testing_activity`
- **Agents**: qa-engineer
- **Task queue**: `qa-task-queue`
- **Timeout**: start_to_close=2h
- **Input**: Implementation artifacts
- **Output**: Test results, coverage report, bug list
- **Child workflow**: Starts `qa_validation_workflow` as child
- **Child workflow ID**: `qa-{workflow_id}-{timestamp}`

### Stage 7: Review

- **Activity**: `review_activity`
- **Agents**: code-reviewer, security-reviewer
- **Task queue**: `review-task-queue`
- **Timeout**: start_to_close=4h
- **Input**: Code + test results + coverage report
- **Output**: Review findings, approval/rejection
- **Governance**: Triggers MCRA child workflow on implementation artifact

### Stage 8: Approval

- **Activity**: `approval_activity`
- **Agents**: tech-lead, product-owner
- **Task queue**: `governance-task-queue`
- **Timeout**: start_to_close=24h
- **Input**: Review results, all prior artifacts
- **Output**: Business sign-off
- **Signal**: Waits for `approval_signal` from React UI via FastAPI

### Stage 9: Release Readiness

- **Activity**: `release_readiness_activity`
- **Agents**: release-manager, sre-engineer
- **Task queue**: `release-task-queue`
- **Timeout**: start_to_close=2h
- **Input**: Approved feature artifacts
- **Output**: Release checklist result, deployment plan
- **Child workflow**: Starts `deployment_readiness_workflow` as child

### Stage 10: Completion

- **Activity**: `completion_activity`
- **Agents**: release-manager
- **Task queue**: `release-task-queue`
- **Timeout**: start_to_close=1h
- **Input**: Deployment readiness result
- **Output**: Deployment confirmation, changelog entry, learning capture
- **Side effects**: Updates feature status to `completed` in Postgres, triggers notifications

## Workflow Definition (Python SDK)

```python
@workflow.defn
class FeatureDevelopmentWorkflow:
    def __init__(self):
        self.current_stage = "intake"
        self.approval_signal_received = False
        self.cancel_requested = False

    @workflow.run
    async def run(self, params: FeatureParams) -> FeatureResult:
        # Stage 1: Intake
        self.current_stage = "intake"
        feature = await workflow.execute_activity(
            intake_activity,
            args=[params],
            start_to_close_timeout=timedelta(minutes=30),
            retry_policy=RetryPolicy(maximum_attempts=3),
        )

        # Stage 2: Specification
        self.current_stage = "specification"
        spec = await workflow.execute_activity(
            specification_activity,
            args=[feature],
            start_to_close_timeout=timedelta(hours=2),
            retry_policy=RetryPolicy(maximum_attempts=2),
        )
        spec_approval = await workflow.execute_child_workflow(
            MakerCheckerReviewerApproverWorkflow.run,
            MCRAParams(artifact_id=spec.id, artifact_type="spec", ...),
            id=f"mcra-{workflow.info().workflow_id}-spec-{spec.id}",
        )
        if spec_approval.status == "rejected":
            return FeatureResult(status="rejected", stage="specification", reason=spec_approval.feedback)

        # Stage 3: Design
        self.current_stage = "design"
        design = await workflow.execute_activity(
            design_activity,
            args=[spec],
            start_to_close_timeout=timedelta(hours=4),
            retry_policy=RetryPolicy(maximum_attempts=2),
        )
        design_approval = await workflow.execute_child_workflow(
            MakerCheckerReviewerApproverWorkflow.run,
            MCRAParams(artifact_id=design.id, artifact_type="design", ...),
            id=f"mcra-{workflow.info().workflow_id}-design-{design.id}",
        )
        if design_approval.status == "rejected":
            return FeatureResult(status="rejected", stage="design", reason=design_approval.feedback)

        # Stage 4: Architecture
        self.current_stage = "architecture"
        arch = await workflow.execute_activity(
            architecture_activity,
            args=[spec, design],
            start_to_close_timeout=timedelta(hours=4),
            retry_policy=RetryPolicy(maximum_attempts=2),
        )
        arch_approval = await workflow.execute_child_workflow(
            MakerCheckerReviewerApproverWorkflow.run,
            MCRAParams(artifact_id=arch.id, artifact_type="architecture", ...),
            id=f"mcra-{workflow.info().workflow_id}-arch-{arch.id}",
        )
        if arch_approval.status == "rejected":
            return FeatureResult(status="rejected", stage="architecture", reason=arch_approval.feedback)

        # Stage 5: Implementation
        self.current_stage = "implementation"
        impl = await workflow.execute_activity(
            implementation_activity,
            args=[arch, spec],
            start_to_close_timeout=timedelta(hours=8),
            heartbeat_timeout=timedelta(minutes=5),
            retry_policy=RetryPolicy(maximum_attempts=3, backoff_coefficient=2.0),
        )

        # Stage 6: Testing
        self.current_stage = "testing"
        qa_result = await workflow.execute_child_workflow(
            QAValidationWorkflow.run,
            QAParams(feature_id=feature.id, impl_artifacts=impl),
            id=f"qa-{workflow.info().workflow_id}-{workflow.now().isoformat()}",
        )
        if qa_result.status == "failed":
            return FeatureResult(status="failed", stage="testing", reason=qa_result.failures)

        # Stage 7: Review
        self.current_stage = "review"
        review_approval = await workflow.execute_child_workflow(
            MakerCheckerReviewerApproverWorkflow.run,
            MCRAParams(artifact_id=impl.id, artifact_type="implementation", ...),
            id=f"mcra-{workflow.info().workflow_id}-impl-{impl.id}",
        )
        if review_approval.status == "rejected":
            return FeatureResult(status="rejected", stage="review", reason=review_approval.feedback)

        # Stage 8: Approval (wait for human signal)
        self.current_stage = "approval"
        await workflow.execute_activity(
            create_approval_request,
            args=[feature.id, "business_approval"],
            start_to_close_timeout=timedelta(seconds=30),
        )
        await workflow.wait_condition(lambda: self.approval_signal_received)

        # Stage 9: Release Readiness
        self.current_stage = "release_readiness"
        readiness = await workflow.execute_child_workflow(
            DeploymentReadinessWorkflow.run,
            DeploymentParams(feature_id=feature.id, artifacts=impl),
            id=f"deploy-ready-{workflow.info().workflow_id}",
        )
        if readiness.status == "not_ready":
            return FeatureResult(status="blocked", stage="release_readiness", reason=readiness.blockers)

        # Stage 10: Completion
        self.current_stage = "completion"
        result = await workflow.execute_activity(
            completion_activity,
            args=[feature, impl, qa_result],
            start_to_close_timeout=timedelta(hours=1),
        )
        return FeatureResult(status="completed", stage="completion", artifacts=result)

    @workflow.signal
    async def approval_signal(self, decision: ApprovalDecision):
        self.approval_signal_received = True

    @workflow.signal
    async def cancel_signal(self):
        self.cancel_requested = True

    @workflow.query
    def get_current_stage(self) -> str:
        return self.current_stage
```

## Signals

| Signal | Source | Purpose |
|--------|--------|---------|
| `approval_signal` | React UI via FastAPI | Business approval at Stage 8 |
| `cancel_signal` | React UI via FastAPI | Cancel the entire workflow |

## Queries

| Query | Returns |
|-------|---------|
| `get_current_stage` | Current stage name string |

## Retry Policy

| Stage | Max Attempts | Backoff | Rationale |
|-------|-------------|---------|-----------|
| Intake | 3 | 1.0 | Simple data capture, transient failures only |
| Specification | 2 | 1.0 | Agent work, retry on timeout |
| Design | 2 | 1.0 | Agent work, retry on timeout |
| Architecture | 2 | 1.0 | Agent work, retry on timeout |
| Implementation | 3 | 2.0 | Complex work, exponential backoff for resource contention |
| Testing | 3 | 1.5 | Test infra flakiness, moderate backoff |
| Review | 1 | N/A | Human-driven, no auto-retry |
| Approval | 1 | N/A | Human-driven, no auto-retry |
| Release Readiness | 2 | 1.0 | Infra checks, retry on transient failure |
| Completion | 3 | 1.0 | Deployment operations, retry on transient failure |

## State Sync

After each stage completes, the sync layer updates Postgres:

```python
async def sync_stage_completion(feature_id: str, stage: str, result: Any, correlation_id: str):
    async with httpx.AsyncClient() as client:
        await client.post(
            f"{FASTAPI_URL}/api/features/{feature_id}/stages",
            json={
                "stage": stage,
                "status": "completed",
                "result": result.dict(),
                "correlation_id": correlation_id,
                "completed_at": datetime.utcnow().isoformat(),
            },
            headers={"X-Idempotency-Key": correlation_id},
        )
```

## Failure Modes

| Failure | Handling |
|---------|----------|
| Activity timeout | Temporal retries per retry policy. After exhaustion, workflow fails with stage context. |
| Agent crash mid-activity | Heartbeat timeout triggers retry. Agent state is not preserved -- activity re-executes from start. |
| MCRA rejection | Parent workflow returns with rejected status and feedback. Caller decides retry. |
| Postgres sync failure | Sync layer retries with exponential backoff. Workflow continues -- Temporal is source of truth. |
| Cancel signal | Workflow sets cancel flag. Next activity check respects cancellation. In-flight activities complete. |
