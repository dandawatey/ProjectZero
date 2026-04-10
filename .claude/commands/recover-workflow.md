# Command: /recover-workflow

## Purpose
Recover entire workflow from failure

## Trigger
User runs `/recover-workflow`

## Step-by-Step Process
Step 1: Read .claude/recovery/active-workflow.json. Step 2: Identify failed stage and step. Step 3: Validate state from last good checkpoint. Step 4: Determine recovery strategy. Step 5: Execute recovery. Step 6: Re-validate. Step 7: Continue workflow.

## Required Inputs
active-workflow.json

## Involved Agents
See relevant agent definitions.

## Outputs
Recovered workflow state

## Validation
All steps must complete successfully.

## Failure Handling
- Checkpoint before each step
- Log failures to .claude/recovery/failure-log.md
- Retry recoverable failures (max 3)

## Next Command
Previous active command
