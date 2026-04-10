# Command: /monitor

## Purpose
Check health and performance after release

## Trigger
User runs `/monitor`

## Step-by-Step Process
Step 1: Verify health endpoints responding. Step 2: Check error rates (< 0.1%). Step 3: Check latency (p50 < 200ms, p99 < 2s). Step 4: Review application logs for anomalies. Step 5: Check business metrics (if configured). Step 6: Generate monitoring report.

## Required Inputs
Deployed application

## Involved Agents
See workflow for this stage.

## Outputs
Monitoring report, alerts if thresholds breached

## Validation
All steps must complete. Governance chain must pass where applicable.

## Failure Handling
- Checkpoint state before each step
- Log failures to .claude/recovery/failure-log.md
- Max 3 retries for recoverable failures
- Escalate to user after retry exhaustion

## Next Command
/optimize if issues found
