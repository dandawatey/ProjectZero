# Workflow: Bug Fix

## Purpose

Temporal workflow for structured bug resolution. Every bug report triggers a `bug_fix_workflow` that enforces triage, root cause analysis, fix implementation, testing, governance, and deployment.

## Temporal Identity

- **Workflow type**: `bug_fix_workflow`
- **Task queue**: `bugfix-task-queue`
- **ID pattern**: `bugfix-{product_id}-{bug_id}-{timestamp}`
- **Execution timeout**: 48 hours

## Stages

```
triage → diagnosis → fix → testing → review → approval → deployment
```

### Stage 1: Triage

- **Activity**: `triage_activity`
- **Agent**: qa-engineer
- **Task queue**: `qa-task-queue`
- **Timeout**: start_to_close=30m
- **Input**: Bug report (title, description, reproduction steps, severity, reporter)
- **Output**: Triage result (confirmed/duplicate/not_a_bug, severity, affected_components, priority)
- **Logic**: If `not_a_bug` or `duplicate`, workflow completes early with status `closed`.

### Stage 2: Diagnosis

- **Activity**: `diagnosis_activity`
- **Agent**: backend-engineer or frontend-engineer (based on affected_components)
- **Task queue**: `engineering-task-queue`
- **Timeout**: start_to_close=2h
- **Input**: Triage result, affected component list, reproduction steps
- **Output**: Root cause analysis (root_cause, affected_files, regression_risk, proposed_fix_approach)

### Stage 3: Fix

- **Activity**: `fix_activity`
- **Agent**: backend-engineer or frontend-engineer
- **Task queue**: `engineering-task-queue`
- **Timeout**: start_to_close=4h, heartbeat=5m
- **Input**: Diagnosis result, proposed fix approach
- **Output**: Code changes, regression test added
- **Constraint**: Must add a regression test that fails without the fix and passes with it

### Stage 4: Testing

- **Activity**: `bug_testing_activity`
- **Agent**: qa-engineer
- **Task queue**: `qa-task-queue`
- **Timeout**: start_to_close=1h
- **Input**: Fix artifacts, original reproduction steps
- **Output**: Test results (regression test passes, existing tests pass, no new failures)
- **Child workflow**: Starts `qa_validation_workflow` scoped to affected modules

### Stage 5: Review

- **Activity**: `bug_review_activity`
- **Agent**: code-reviewer
- **Task queue**: `review-task-queue`
- **Timeout**: start_to_close=2h
- **Governance**: Triggers MCRA child workflow on fix artifact
- **Focus**: Minimal change, no scope creep, regression test quality, root cause correctly addressed

### Stage 6: Approval

- **Signal-based**: Waits for `approval_signal` from React UI
- **Timeout**: 8 hours
- **Approver**: tech-lead
- **Criteria**: Fix is minimal, targeted, and well-tested

### Stage 7: Deployment

- **Activity**: `bug_deployment_activity`
- **Agent**: release-manager
- **Task queue**: `release-task-queue`
- **Timeout**: start_to_close=1h
- **Input**: Approved fix, deployment plan
- **Output**: Deployment confirmation, monitoring verification
- **Post-deploy**: Verify the original reproduction steps no longer reproduce the bug

## Workflow Definition

```python
@workflow.defn
class BugFixWorkflow:
    def __init__(self):
        self.current_stage = "triage"
        self.approval_received = False

    @workflow.run
    async def run(self, params: BugParams) -> BugFixResult:
        # Triage
        self.current_stage = "triage"
        triage = await workflow.execute_activity(
            triage_activity, args=[params],
            start_to_close_timeout=timedelta(minutes=30),
            retry_policy=RetryPolicy(maximum_attempts=2),
        )
        if triage.verdict in ("duplicate", "not_a_bug"):
            return BugFixResult(status="closed", reason=triage.verdict)

        # Diagnosis
        self.current_stage = "diagnosis"
        diagnosis = await workflow.execute_activity(
            diagnosis_activity, args=[triage],
            start_to_close_timeout=timedelta(hours=2),
            retry_policy=RetryPolicy(maximum_attempts=2),
        )

        # Fix
        self.current_stage = "fix"
        fix = await workflow.execute_activity(
            fix_activity, args=[diagnosis],
            start_to_close_timeout=timedelta(hours=4),
            heartbeat_timeout=timedelta(minutes=5),
            retry_policy=RetryPolicy(maximum_attempts=3, backoff_coefficient=2.0),
        )

        # Testing
        self.current_stage = "testing"
        test_result = await workflow.execute_child_workflow(
            QAValidationWorkflow.run,
            QAParams(scope="bugfix", affected_modules=diagnosis.affected_components, fix_artifacts=fix),
            id=f"qa-bugfix-{workflow.info().workflow_id}",
        )
        if test_result.status == "failed":
            return BugFixResult(status="test_failure", failures=test_result.failures)

        # Review via MCRA
        self.current_stage = "review"
        review = await workflow.execute_child_workflow(
            MakerCheckerReviewerApproverWorkflow.run,
            MCRAParams(artifact_id=fix.id, artifact_type="bugfix"),
            id=f"mcra-bugfix-{workflow.info().workflow_id}",
        )
        if review.status == "rejected":
            return BugFixResult(status="rejected", stage="review", feedback=review.feedback)

        # Approval
        self.current_stage = "approval"
        await workflow.execute_activity(
            create_approval_request,
            args=[params.bug_id, "bugfix_approval"],
            start_to_close_timeout=timedelta(seconds=30),
        )
        await workflow.wait_condition(lambda: self.approval_received)

        # Deployment
        self.current_stage = "deployment"
        deploy = await workflow.execute_activity(
            bug_deployment_activity, args=[fix, params],
            start_to_close_timeout=timedelta(hours=1),
            retry_policy=RetryPolicy(maximum_attempts=2),
        )
        return BugFixResult(status="deployed", deployment=deploy)

    @workflow.signal
    async def approval_signal(self, decision: ApprovalDecision):
        self.approval_received = True

    @workflow.query
    def get_current_stage(self) -> str:
        return self.current_stage
```

## Severity-Based Timeouts

| Severity | Total Workflow Timeout | Approval Timeout |
|----------|----------------------|------------------|
| critical | 12 hours | 1 hour |
| high | 24 hours | 4 hours |
| medium | 48 hours | 8 hours |
| low | 72 hours | 24 hours |

## Hotfix Path

For `critical` severity bugs, the workflow skips the Design stage (there is none) and uses expedited timeouts. The MCRA child workflow uses a single combined Checker+Reviewer gate instead of three sequential gates. Approver gate remains mandatory.
