# Command: /resume

## Purpose
Resume from last checkpoint after interruption

## Trigger
User runs `/resume`

## Step-by-Step Process
Step 1: Read .claude/recovery/state.json. Step 2: Identify last checkpoint (stage, command, step). Step 3: Validate current file state matches checkpoint. Step 4: Reload relevant context from memory. Step 5: Verify queue state consistency. Step 6: Continue from checkpoint.

## Required Inputs
Recovery state

## Involved Agents
See relevant agent definitions.

## Outputs
Resumed session at last checkpoint

## Validation
All steps must complete successfully.

## Failure Handling
- Checkpoint before each step
- Log failures to .claude/recovery/failure-log.md
- Retry recoverable failures (max 3)

## Next Command
Previous active command
