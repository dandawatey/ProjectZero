# Ticket Enforcement: No Ticket, No Work

## Rule
Every code change must be traceable to a ticket. No exceptions.

## Requirements
- Every commit message includes ticket ID: `[HEALTH-42] Add vitals dashboard`
- Every PR title includes ticket ID
- Every PR description links to ticket
- Every branch name includes ticket ID: `feature/HEALTH-42`

## Enforcement
- Checker agent validates ticket reference in PR
- CI hook validates commit message format
- Work without ticket reference rejected at first gate
- Orphaned PRs (no ticket) flagged and blocked

## Ticket Requirements
Before work begins, ticket MUST have:
- Clear description
- Acceptance criteria (testable)
- Priority assigned
- Epic/module linked
- Story points estimated (for stories)

## Why
- Traceability: every line of code has business justification
- Accountability: who requested what and why
- Metrics: velocity, cycle time, throughput measured from tickets
- Recovery: interrupted work can be resumed from ticket context
