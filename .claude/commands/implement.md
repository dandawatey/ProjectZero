# Command: /implement

## Purpose
Build features per ticket using TDD through governance chain

## Trigger
User runs `/implement`

## Step-by-Step Process
Step 1: Load approved architecture and tickets. Step 2: Ralph Controller reads queue, assigns tickets to agents. Step 3: Engineers implement per ticket following TDD (test first → implement → verify). Step 4: Each completed ticket → Checker validates (tests, lint, security). Step 5: If check passes → Reviewer reviews (quality, architecture, coverage). Step 6: If review passes → Approver approves. Step 7: Merge approved work. Step 8: Track progress in queue (ready→active→completed). Step 9: Handle blocked items (dependencies, failures). Step 10: Report progress.

## Required Inputs
Approved architecture, tickets in queue

## Involved Agents
See workflow for this stage.

## Outputs
Implemented and approved code, all tests passing

## Validation
All steps must complete. Governance chain must pass where applicable.

## Failure Handling
- Checkpoint state before each step
- Log failures to .claude/recovery/failure-log.md
- Max 3 retries for recoverable failures
- Escalate to user after retry exhaustion

## Next Command
/check (individual) or /release (batch)
