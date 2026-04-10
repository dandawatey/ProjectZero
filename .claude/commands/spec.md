# Command: /spec

## Purpose
Create specifications from BMAD/PRD with acceptance criteria and tickets

## Trigger
User runs `/spec`

## Step-by-Step Process
Step 1: Load BMAD from .claude/memory/domain-memory.md. Step 2: Product Manager creates feature specifications. Step 3: Break specifications into epics (one per module). Step 4: Break epics into user stories with acceptance criteria. Step 5: Define story points and priority. Step 6: Create JIRA tickets or local tracking. Step 7: Prioritize backlog. Step 8: Checker validates completeness. Step 9: Reviewer reviews spec quality. Step 10: Approver approves specification package.

## Required Inputs
BMAD in memory, module candidates

## Involved Agents
See workflow for this stage.

## Outputs
Approved specifications, tickets with acceptance criteria, prioritized backlog

## Validation
All steps must complete. Governance chain must pass where applicable.

## Failure Handling
- Checkpoint state before each step
- Log failures to .claude/recovery/failure-log.md
- Max 3 retries for recoverable failures
- Escalate to user after retry exhaustion

## Next Command
/arch
