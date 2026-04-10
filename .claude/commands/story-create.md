# Command: /story-create

## Purpose
Create stories for a UI component

## Trigger
User runs `/story-create`

## Step-by-Step Process
Step 1: Identify target component. Step 2: Analyze component props and variants. Step 3: Create story file with: Default, all variants, all states (loading, disabled, error), sizes, interactive args. Step 4: Add accessibility annotations. Step 5: Validate story renders.

## Required Inputs
Component path

## Involved Agents
See relevant agent definitions.

## Outputs
Story file with all variants

## Validation
All steps must complete successfully.

## Failure Handling
- Checkpoint before each step
- Log failures to .claude/recovery/failure-log.md
- Retry recoverable failures (max 3)

## Next Command
/story-validate
