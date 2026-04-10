# Command: /pipeline-create

## Purpose
Define and configure an async processing pipeline for Dagster

## Trigger
User runs `/pipeline-create`

## Step-by-Step Process
Step 1: Define pipeline purpose and steps. Step 2: Define data inputs and outputs. Step 3: Define schedule (cron or event-triggered). Step 4: Define retry policy. Step 5: Generate Dagster job definition. Step 6: Validate pipeline configuration. Step 7: Register in pipeline registry.

## Required Inputs
Pipeline requirements

## Involved Agents
See relevant agent definitions.

## Outputs
Pipeline configuration file

## Validation
All steps must complete successfully.

## Failure Handling
- Checkpoint before each step
- Log failures to .claude/recovery/failure-log.md
- Retry recoverable failures (max 3)

## Next Command
N/A
