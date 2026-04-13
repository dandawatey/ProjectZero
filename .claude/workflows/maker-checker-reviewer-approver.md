# Workflow: Maker-Checker-Reviewer-Approver (MCRA)

## Purpose

Temporal child workflow implementing the four-eye governance chain. Every artifact (spec, design, code, release) passes through three sequential gates after the Maker produces it. Each gate waits for a human signal from the React UI.

## Temporal Identity

- **Workflow type**: `maker_checker_reviewer_approver_workflow`
- **Task queue**: `governance-task-queue`
- **ID pattern**: `mcra-{parent_workflow_id}-{artifact_type}-{artifact_id}`
- **Invoked as**: Child workflow from any parent workflow requiring governance

## Workflow Definition (Python SDK)

```python
@workflow.defn
class MakerCheckerReviewerApproverWorkflow:
    def __init__(self):
        self.checker_decision = None
        self.reviewer_decision = None
        self.approver_decision = None

    @workflow.run
    async def run(self, params: MCRAParams) -> MCRAResult:
        # Step 1: Create artifact record in FastAPI
        artifact = await workflow.execute_activity(
            create_artifact_record,
            args=[params],
            start_to_close_timeout=timedelta(seconds=30),
        )

        # Step 2: Checker Gate
        await workflow.execute_activity(
            create_approval_request,
            args=[artifact.id, "checker", params.checker_agent],
            start_to_close_timeout=timedelta(seconds=30),
        )
        await workflow.wait_condition(lambda: self.checker_decision is not None)

        if self.checker_decision.verdict == "FAIL":
            return MCRAResult(status="rejected", gate="checker", feedback=self.checker_decision.feedback)

        # Step 3: Reviewer Gate
        await workflow.execute_activity(
            create_approval_request,
            args=[artifact.id, "reviewer", params.reviewer_agent],
            start_to_close_timeout=timedelta(seconds=30),
        )
        await workflow.wait_condition(lambda: self.reviewer_decision is not None)

        if self.reviewer_decision.verdict == "REJECT":
            return MCRAResult(status="rejected", gate="reviewer", feedback=self.reviewer_decision.feedback)

        # Step 4: Approver Gate
        await workflow.execute_activity(
            create_approval_request,
            args=[artifact.id, "approver", params.approver_agent],
            start_to_close_timeout=timedelta(seconds=30),
        )
        await workflow.wait_condition(lambda: self.approver_decision is not None)

        if self.approver_decision.verdict == "REJECT":
            return MCRAResult(status="rejected", gate="approver", feedback=self.approver_decision.feedback)

        return MCRAResult(status="approved", gate="approver", feedback=None)

    @workflow.signal
    async def checker_signal(self, decision: GateDecision):
        self.checker_decision = decision

    @workflow.signal
    async def reviewer_signal(self, decision: GateDecision):
        self.reviewer_decision = decision

    @workflow.signal
    async def approver_signal(self, decision: GateDecision):
        self.approver_decision = decision
```

## Signal Flow

```
React UI                  FastAPI                    Temporal
  |                         |                          |
  |  User clicks approve    |                          |
  | ----------------------> |                          |
  |                         | POST /api/approvals/{id} |
  |                         |   validate + log         |
  |                         | -----------------------> |
  |                         |   send_signal(           |
  |                         |     workflow_id,          |
  |                         |     "checker_signal",     |
  |                         |     GateDecision(...)     |
  |                         |   )                       |
  |                         |                          |
  |                         | <--- state sync -------- |
  |                         |   update Postgres        |
  | <-- SSE/poll update --- |                          |
```

## Gate Details

### Checker (Gate 1)
- **What**: Automated + semi-automated validation
- **Checks**: Tests pass, lint clean, security scan clean, builds successfully
- **Decision**: Binary PASS/FAIL -- no subjective judgment
- **Timeout**: 1 hour (configurable). On timeout, escalate to tech lead.
- **Activity**: `run_checker_activity` executes automated checks before creating approval request
- **PASS**: Workflow advances to Reviewer gate
- **FAIL**: Workflow returns rejected with specific findings (file, line, issue)

### Reviewer (Gate 2)
- **What**: Deep quality assessment by a qualified reviewer
- **Checks**: Code quality, architecture alignment, test adequacy, documentation completeness
- **Decision**: APPROVE or REJECT with actionable feedback
- **Timeout**: 4 hours. On timeout, notify product owner.
- **APPROVE**: Workflow advances to Approver gate
- **REJECT**: Workflow returns rejected. Parent workflow handles retry logic.

### Approver (Gate 3)
- **What**: Business and governance validation
- **Checks**: Business requirements met, governance compliant, ready for merge/deploy
- **Decision**: APPROVE or REJECT with business-level feedback
- **Timeout**: 8 hours. On timeout, notify CTO.
- **APPROVE**: Workflow returns approved. Parent workflow proceeds.
- **REJECT**: Workflow returns rejected. Parent workflow handles retry logic.

## FastAPI Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/api/artifacts/{id}/governance` | Start MCRA child workflow for artifact |
| GET | `/api/artifacts/{id}/governance/status` | Current gate status + pending decisions |
| POST | `/api/approvals/{approval_id}` | Submit gate decision (sends Temporal signal) |
| GET | `/api/approvals/pending` | List all pending approval requests |

## Postgres Tables

```sql
CREATE TABLE approval_requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    artifact_id UUID NOT NULL REFERENCES artifacts(id),
    workflow_id TEXT NOT NULL,
    gate TEXT NOT NULL CHECK (gate IN ('checker', 'reviewer', 'approver')),
    assigned_to TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected', 'timed_out')),
    verdict TEXT,
    feedback JSONB,
    created_at TIMESTAMPTZ DEFAULT now(),
    decided_at TIMESTAMPTZ,
    correlation_id UUID NOT NULL
);
```

## Retry Policy

When MCRA returns rejected, the parent workflow decides whether to retry:
- **Checker rejection**: Auto-retry after Maker fixes issues (max 3 retries)
- **Reviewer rejection**: Return to Maker with feedback, re-enter MCRA from Gate 1 (max 2 retries)
- **Approver rejection**: Escalate to human. No auto-retry.

## Rules

1. Each gate is independent -- Reviewer does not re-check what Checker checked.
2. Rejection always includes specific, actionable feedback in the `feedback` JSONB field.
3. Maker cannot be their own Checker, Reviewer, or Approver. Enforced by FastAPI validation.
4. All gate decisions logged in Postgres `approval_requests` table with full audit trail.
5. No bypassing gates -- even for "small" changes. The workflow enforces this structurally.
6. Signals are idempotent -- duplicate signals for the same gate are ignored.
