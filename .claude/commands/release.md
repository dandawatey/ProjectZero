# Command: /release

## Purpose
Deploy approved work to production

## Trigger
User runs `/release`

## Step-by-Step Process
Step 1: Create release branch. Step 2: Bump version. Step 3: Run full test suite. Step 4: Run security scan. Step 5: Generate changelog. Step 6: Deploy to staging. Step 7: Run smoke tests. Step 8: Deploy to production. Step 9: Verify health checks. Step 10: Tag release. Step 11: Update documentation. Step 12: Notify stakeholders.

## Required Inputs
All approved work for release

## Involved Agents
See workflow for this stage.

## Outputs
Deployed application, release notes, changelog

## Validation
All steps must complete. Governance chain must pass where applicable.

## Failure Handling
- Checkpoint state before each step
- Log failures to .claude/recovery/failure-log.md
- Max 3 retries for recoverable failures
- Escalate to user after retry exhaustion

## Next Command
/monitor
