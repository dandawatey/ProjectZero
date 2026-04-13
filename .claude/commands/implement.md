# Command: /implement

## Purpose

Start a `feature_development_workflow` via Temporal. No direct code generation. The system guides the feature through all stages with enforced governance gates.

## Trigger

User runs `/implement` (optionally with a feature ID or description)

## What Happens

### Step 1: Select or Create Feature

If a feature ID is provided, load the existing feature from Postgres via FastAPI:
```
GET /api/features/{feature_id}
```

If no feature ID, create a new feature:
```
POST /api/features
Body: { title, description, priority, product_id }
```

### Step 2: Start Temporal Workflow

FastAPI starts a `feature_development_workflow`:
```
temporal_client.start_workflow(
    FeatureDevelopmentWorkflow.run,
    FeatureParams(feature_id=feature.id, product_id=product.id, ...),
    id=f"feature-{product.id}-{feature.id}-{timestamp}",
    task_queue="feature-dev-task-queue",
)
```

The workflow ID is stored on the feature record in Postgres.

### Step 3: Workflow Executes Stages

The system drives the feature through 10 stages automatically:

1. **Intake**: Agent captures requirements, creates structured feature record
2. **Specification**: Agent writes full spec with acceptance criteria. MCRA governance gate.
3. **Design**: Agent produces design artifacts. MCRA governance gate.
4. **Architecture**: Agent writes ADRs, API contracts, data models. MCRA governance gate.
5. **Implementation**: Agent writes code following TDD (test first, implement, verify). Heartbeat every 5m.
6. **Testing**: QA validation child workflow runs full test suite (unit, integration, E2E, coverage).
7. **Review**: MCRA governance gate on implementation artifacts.
8. **Approval**: Workflow pauses. Human must approve via React UI or `/approve` command.
9. **Release Readiness**: Deployment readiness child workflow validates infrastructure.
10. **Completion**: Deploy, verify health, capture learnings.

### Step 4: Human Interaction Points

The workflow pauses and waits for human signals at:
- **MCRA gates**: Checker, Reviewer, Approver decisions at stages 2, 3, 4, 7
- **Business approval**: Stage 8 requires explicit human approval signal
- **Release sign-offs**: Engineering, Product, Ops sign-offs during release governance

Use React UI (Control Tower) to view pending approvals and submit decisions.
Alternatively, use `/approve` command to send approval signals.

### Step 5: Monitor Progress

Query workflow state at any time:
```
GET /api/features/{feature_id}/workflow
```

Returns current stage, stage history, pending approvals, blockers.

Or use `/monitor` command to check status.

## Required Inputs

- Product must be bootstrapped (`/bootstrap-product` completed)
- Platform must be running (FastAPI, Postgres, Temporal)
- At minimum: feature title and description

## Outputs

- Feature record in Postgres with full stage history
- All artifacts: spec, design, architecture, code, tests, reviews
- Audit trail of every decision and state transition
- Deployed and verified feature (on workflow completion)

## What /implement Does NOT Do

- Does not generate code directly. Code is produced by agents within Temporal activities.
- Does not skip stages. Every stage executes in sequence.
- Does not bypass governance. MCRA gates are structural, not optional.
- Does not auto-approve. Human signals are required at governance gates.

## Failure Handling

- **Activity failure**: Temporal retries per retry policy (max 3 attempts with exponential backoff)
- **MCRA rejection**: Workflow returns with rejection feedback. Re-run `/implement` with the same feature ID to restart from the rejected stage.
- **Workflow timeout**: 7-day execution timeout. If exceeded, feature is marked `timed_out`. Re-run `/implement` to start a new workflow.
- **Platform outage**: Temporal preserves workflow state. Activities resume when workers reconnect.

## Example Usage

```
# Start new feature
/implement "Add user authentication with OAuth2"

# Resume existing feature
/implement FEAT-42

# Check status
/monitor FEAT-42

# Approve pending gate
/approve FEAT-42
```

## Next Command

- `/monitor` -- Check workflow progress
- `/approve` -- Submit approval at governance gates
- `/check` -- View QA validation results
- `/release` -- View release governance status
