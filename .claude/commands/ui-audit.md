# Command: /ui-audit

## Purpose
Audit entire application UI for compliance

## Trigger
User runs `/ui-audit`

## Step-by-Step Process
Step 1: Scan all pages/components. Step 2: Check shared component usage (vs ad-hoc). Step 3: Check design token compliance. Step 4: Run accessibility audit (all pages). Step 5: Check responsive behavior (all breakpoints). Step 6: Check required states (loading, error, empty). Step 7: Generate audit report.

## Required Inputs
Application UI code

## Involved Agents
See relevant agent definitions.

## Outputs
Audit report with findings

## Validation
All steps must complete successfully.

## Failure Handling
- Checkpoint before each step
- Log failures to .claude/recovery/failure-log.md
- Retry recoverable failures (max 3)

## Next Command
Fix findings
