# Command: /optimize

## Purpose
Identify and plan improvements from monitoring data

## Trigger
User runs `/optimize`

## Step-by-Step Process
Step 1: Analyze monitoring data for bottlenecks. Step 2: Review code quality metrics. Step 3: Identify technical debt. Step 4: Assess cost optimization opportunities. Step 5: Create optimization tickets with clear objectives. Step 6: Prioritize optimization backlog.

## Required Inputs
Monitoring data, metrics

## Involved Agents
See workflow for this stage.

## Outputs
Optimization tickets in backlog

## Validation
All steps must complete. Governance chain must pass where applicable.

## Failure Handling
- Checkpoint state before each step
- Log failures to .claude/recovery/failure-log.md
- Max 3 retries for recoverable failures
- Escalate to user after retry exhaustion

## Next Command
/implement for optimization work
