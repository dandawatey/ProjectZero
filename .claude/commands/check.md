# Command: /check

## Purpose
Run automated checks on completed work

## Trigger
User runs `/check`

## Step-by-Step Process
Step 1: Identify target (ticket, PR, or module). Step 2: Run all tests (unit + integration + e2e). Step 3: Run linter (zero errors, zero warnings). Step 4: Run security scan. Step 5: Validate ticket acceptance criteria addressed. Step 6: Validate API contracts honored. Step 7: Check test coverage ≥ 80%. Step 8: Generate check report with pass/fail per category.

## Required Inputs
Completed implementation

## Involved Agents
See workflow for this stage.

## Outputs
Check report (pass/fail with details)

## Validation
All steps must complete. Governance chain must pass where applicable.

## Failure Handling
- Checkpoint state before each step
- Log failures to .claude/recovery/failure-log.md
- Max 3 retries for recoverable failures
- Escalate to user after retry exhaustion

## Next Command
/review if pass
