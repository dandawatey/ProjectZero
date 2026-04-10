# Command: /component-review

## Purpose
Review component for design system compliance

## Trigger
User runs `/component-review`

## Step-by-Step Process
Step 1: Check design token usage (no hardcoded values). Step 2: Check accessibility (WCAG 2.1 AA). Step 3: Check responsive behavior. Step 4: Check keyboard navigation. Step 5: Check Storybook story completeness. Step 6: Check test coverage. Step 7: Generate compliance report.

## Required Inputs
Component path

## Involved Agents
See relevant agent definitions.

## Outputs
Compliance report

## Validation
All steps must complete successfully.

## Failure Handling
- Checkpoint before each step
- Log failures to .claude/recovery/failure-log.md
- Retry recoverable failures (max 3)

## Next Command
Fix findings
