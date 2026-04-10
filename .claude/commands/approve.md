# Command: /approve

## Purpose
Business and governance validation

## Trigger
User runs `/approve`

## Step-by-Step Process
Step 1: Load review report (must be approved). Step 2: Validate business requirements fully met. Step 3: Confirm governance chain complete (checked + reviewed). Step 4: Assess merge readiness (no conflicts, CI green). Step 5: Authorize merge or reject with feedback.

## Required Inputs
Work that passed /review

## Involved Agents
See workflow for this stage.

## Outputs
Approval or rejection, merge authorization

## Validation
All steps must complete. Governance chain must pass where applicable.

## Failure Handling
- Checkpoint state before each step
- Log failures to .claude/recovery/failure-log.md
- Max 3 retries for recoverable failures
- Escalate to user after retry exhaustion

## Next Command
/release when ready
