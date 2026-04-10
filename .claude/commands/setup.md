# Command: /setup

## Purpose
Validates and configures the development environment

## Trigger
User runs `/setup`

## Step-by-Step Process
Step 1: Check required tools (Node.js ≥18, Git, Claude CLI). Step 2: Check optional tools (Docker, pnpm/npm). Step 3: Validate IDE (VS Code recommended). Step 4: Check git configuration. Step 5: Install dependencies if package.json exists. Step 6: Validate .env.example → .env copy. Step 7: Report environment status.

## Required Inputs
None

## Involved Agents
See workflow for this stage.

## Outputs
Environment validation report

## Validation
All steps must complete. Governance chain must pass where applicable.

## Failure Handling
- Checkpoint state before each step
- Log failures to .claude/recovery/failure-log.md
- Max 3 retries for recoverable failures
- Escalate to user after retry exhaustion

## Next Command
/factory-init
