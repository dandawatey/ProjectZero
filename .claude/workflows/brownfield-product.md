# Workflow: Brownfield Product

## Purpose
Existing product onboarding

## Entry Criteria
Existing codebase, factory initialized

## Process
Analyze existing code structure, map to modules, identify gaps vs factory standards, create migration plan for compliance, preserve existing functionality

## Governance
All artifacts pass through maker-checker-reviewer-approver chain.

## Exit Criteria
All deliverables complete, validated, and approved. Ready for next phase.

## Failure Handling
- Checkpoint state before each step
- On failure: log to failure-log.md, attempt recovery, escalate after 3 retries
- Never skip steps or bypass governance
