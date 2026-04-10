# Command: /review

## Purpose
Comprehensive quality review of checked work

## Trigger
User runs `/review`

## Step-by-Step Process
Step 1: Load check report (must be passing). Step 2: Review code quality and readability. Step 3: Validate architecture alignment. Step 4: Assess test coverage quality (meaningful tests, not just percentage). Step 5: Check documentation completeness. Step 6: For UI: check design system compliance, accessibility. Step 7: Generate review report with approve/reject and comments.

## Required Inputs
Work that passed /check

## Involved Agents
See workflow for this stage.

## Outputs
Review report with approval or rejection

## Validation
All steps must complete. Governance chain must pass where applicable.

## Failure Handling
- Checkpoint state before each step
- Log failures to .claude/recovery/failure-log.md
- Max 3 retries for recoverable failures
- Escalate to user after retry exhaustion

## Next Command
/approve if approved
