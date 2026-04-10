# Command: /story-validate

## Purpose
Check all Storybook stories render and pass accessibility

## Trigger
User runs `/story-validate`

## Step-by-Step Process
Step 1: Build Storybook. Step 2: Check all stories render without errors. Step 3: Run accessibility checks (axe). Step 4: Verify all components have stories. Step 5: Report missing stories and a11y violations.

## Required Inputs
packages/ui

## Involved Agents
See relevant agent definitions.

## Outputs
Validation report

## Validation
All steps must complete successfully.

## Failure Handling
- Checkpoint before each step
- Log failures to .claude/recovery/failure-log.md
- Retry recoverable failures (max 3)

## Next Command
Fix violations
