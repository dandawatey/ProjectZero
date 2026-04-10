# Command: /recover-ticket

## Purpose
Recover a specific ticket that failed or was interrupted

## Trigger
User runs `/recover-ticket`

## Step-by-Step Process
Step 1: Read .claude/recovery/active-ticket.json. Step 2: Identify ticket state (in-progress, failed, blocked). Step 3: Determine recovery action (retry, rollback, escalate). Step 4: Execute recovery. Step 5: Verify recovered state. Step 6: Log to failure-log.md.

## Required Inputs
Ticket ID or active-ticket.json

## Involved Agents
See relevant agent definitions.

## Outputs
Recovered ticket, action log

## Validation
All steps must complete successfully.

## Failure Handling
- Checkpoint before each step
- Log failures to .claude/recovery/failure-log.md
- Retry recoverable failures (max 3)

## Next Command
/implement to continue
