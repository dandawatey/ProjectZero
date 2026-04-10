# Command: /component-create

## Purpose
Create a new shared component in the design system

## Trigger
User runs `/component-create`

## Step-by-Step Process
Step 1: Check packages/ui for existing similar component. Step 2: Define props interface. Step 3: Implement component using design tokens. Step 4: Write unit tests. Step 5: Create Storybook stories. Step 6: Validate accessibility. Step 7: Submit for design review.

## Required Inputs
Component name, props spec

## Involved Agents
See relevant agent definitions.

## Outputs
Component with tests and stories

## Validation
All steps must complete successfully.

## Failure Handling
- Checkpoint before each step
- Log failures to .claude/recovery/failure-log.md
- Retry recoverable failures (max 3)

## Next Command
/component-review
