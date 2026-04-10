# Command: /design-system-init

## Purpose
Set up packages/ui with Storybook and design tokens

## Trigger
User runs `/design-system-init`

## Step-by-Step Process
Step 1: Create packages/ui directory structure. Step 2: Initialize package.json with dependencies. Step 3: Configure Storybook (.storybook/main.ts, preview.ts). Step 4: Create design token files from .claude/design-system/token-rules.md. Step 5: Create base components (Button, Input, Card). Step 6: Create example stories. Step 7: Validate Storybook builds.

## Required Inputs
Design principles from .claude/design-system/

## Involved Agents
See relevant agent definitions.

## Outputs
Configured packages/ui with Storybook

## Validation
All steps must complete successfully.

## Failure Handling
- Checkpoint before each step
- Log failures to .claude/recovery/failure-log.md
- Retry recoverable failures (max 3)

## Next Command
/component-create
