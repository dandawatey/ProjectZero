# Workflow: SPARC: Architecture

## Purpose
Architecture phase of SPARC

## Entry Criteria
Approved specifications and designs

## Process
Architect designs system, defines modules and boundaries, creates API contracts and DB schemas, selects tech stack, creates ADRs, validates through governance

## Governance
All artifacts pass through maker-checker-reviewer-approver chain.

## Exit Criteria
All deliverables complete, validated, and approved. Ready for next phase.

## Failure Handling
- Checkpoint state before each step
- On failure: log to failure-log.md, attempt recovery, escalate after 3 retries
- Never skip steps or bypass governance
