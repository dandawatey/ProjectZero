# Workflow: SPARC: Realization

## Purpose
Implementation phase of SPARC

## Entry Criteria
Approved architecture with tickets

## Process
Ralph assigns tickets to agents, engineers implement with TDD, each ticket through checker-reviewer-approver, track in queue, handle blocks

## Governance
All artifacts pass through maker-checker-reviewer-approver chain.

## Exit Criteria
All deliverables complete, validated, and approved. Ready for next phase.

## Failure Handling
- Checkpoint state before each step
- On failure: log to failure-log.md, attempt recovery, escalate after 3 retries
- Never skip steps or bypass governance
