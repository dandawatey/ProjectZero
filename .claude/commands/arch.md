# Command: /arch

## Purpose
Design system architecture with modules, contracts, and tech decisions

## Trigger
User runs `/arch`

## Step-by-Step Process
Step 1: Load approved specifications. Step 2: Architect designs system architecture. Step 3: Define modules with boundaries and APIs. Step 4: Create API contracts → product repo: .claude/contracts/api-contract.yaml (from template). Step 5: Create DB schema → product repo: .claude/contracts/db-schema.sql (from template). Step 6: Create frontend types → product repo: .claude/contracts/frontend-types.ts (from template). Step 7: Select and document tech stack. Step 8: Write Architecture Decision Records. Step 9: Checker validates contracts. Step 10: Reviewer reviews architecture. Step 11: Security Reviewer validates security architecture. Step 12: Approver approves architecture.

## Required Inputs
Approved specifications

## Involved Agents
See workflow for this stage.

## Outputs
Approved architecture, contracts, module definitions, ADRs

## Validation
All steps must complete. Governance chain must pass where applicable.

## Failure Handling
- Checkpoint state before each step
- Log failures to .claude/recovery/failure-log.md
- Max 3 retries for recoverable failures
- Escalate to user after retry exhaustion

## Brain Integration

Architecture decisions are stored in the Brain (`/api/v1/brain/decisions`). Before starting architecture work, the agent queries Brain for prior ADRs, rejected alternatives, and proven patterns. After completing architecture, all new ADRs and tech stack decisions are written back. This ensures architecture knowledge persists across products and sessions.

## Interaction Modes

Use `brainstorm` mode during design exploration (Steps 2-3) to evaluate trade-offs and alternatives before committing. Switch to `plan` mode for structuring contracts and module boundaries, and `implement` mode when writing final ADRs and contract files. Mode is switchable via React UI or Temporal signal.

## Next Command
/implement
