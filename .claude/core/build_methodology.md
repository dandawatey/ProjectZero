# Build Methodology

## Overview
ProjectZeroFactory uses **SPARC + BMAD + TDD + Governance** as its build methodology. Every product follows this exact process. No shortcuts. No stage skipping.

## SPARC Framework

### S — Specification
- **Entry**: Approved BMAD document
- **Agents**: Product Manager, spec-miner skill
- **Activities**: Extract requirements, write specifications, define acceptance criteria, create tickets, prioritize backlog
- **Artifacts**: Specifications, epics, stories with acceptance criteria, prioritized backlog
- **Exit**: Specifications approved through maker-checker-reviewer-approver chain
- **Command**: `/spec`

### P — Pseudocode / Design
- **Entry**: Approved specifications
- **Agents**: Architect, Product Manager
- **Activities**: Design logic flows, define interfaces, create pseudocode for complex algorithms, wireframe key screens
- **Artifacts**: Logic flow documents, interface definitions, wireframes
- **Exit**: Design reviewed and approved
- **Command**: Part of `/arch`

### A — Architecture
- **Entry**: Approved specifications and design
- **Agents**: Architect, Security Reviewer, SRE Engineer
- **Activities**: System design, module decomposition, tech stack selection, API contract creation, DB schema design, infrastructure planning
- **Artifacts**: Architecture document, module definitions, api-contract.yaml, db-schema.sql, frontend-types.ts, ADRs
- **Exit**: Architecture approved through governance chain
- **Command**: `/arch`

### R — Realization
- **Entry**: Approved architecture with tickets
- **Agents**: Backend Engineer, Frontend Engineer, Data Engineer, DevOps Engineer, QA Engineer
- **Activities**: Implement features per ticket using TDD, each through maker-checker-reviewer-approver
- **Artifacts**: Working code with tests, Storybook stories, documentation
- **Exit**: All tickets completed and approved, all tests passing
- **Command**: `/implement`

### C — Completion
- **Entry**: All realization work approved
- **Agents**: Release Manager, QA Engineer, Security Reviewer, SRE Engineer
- **Activities**: Final validation, release preparation, deployment, monitoring setup
- **Artifacts**: Release notes, deployed application, monitoring dashboards, runbooks
- **Exit**: Application deployed, health checks passing, monitoring active
- **Command**: `/release`, `/monitor`

## TDD Discipline

Every implementation follows:
1. **Red**: Write a failing test that describes expected behavior
2. **Green**: Write minimum code to make the test pass
3. **Refactor**: Clean up code while keeping tests green
4. **Repeat**: Next behavior

Rules:
- No production code without a test
- Tests run before every commit
- Coverage minimum: 80% lines, 100% on critical paths
- Test names describe behavior, not implementation

## Governance Chain

Every artifact passes through:
```
Maker (creates) → Checker (validates basics) → Reviewer (deep review) → Approver (authorizes)
```

- **Maker**: The agent that produces the work
- **Checker**: Validates tests pass, lint clean, security clean, ticket requirements met
- **Reviewer**: Deep review of quality, architecture alignment, test coverage, documentation
- **Approver**: Validates business requirements met, governance satisfied, authorizes merge

Rejection at any gate sends work back to Maker with specific, actionable feedback.

## No Ticket, No Work

- Every code change must reference a ticket ID
- Every commit message includes ticket ID
- Every PR links to ticket
- Work without a ticket is rejected at Checker gate
- Tickets must have acceptance criteria before work begins
