# 04 - Governance Model

## Overview

The governance model is the enforcement mechanism that ensures every artifact produced by the factory meets quality, security, and compliance standards. It operates through three interlocking systems: process governance (BMAD + SPARC), quality governance (Maker-Checker-Reviewer-Approver), and operational governance (No Ticket No Work + TDD).

## BMAD: Business Model Architecture Document

### Purpose

The BMAD is the foundational document for every product. It answers "what are we building and why?" before any code is written. No development work can proceed without a validated BMAD.

### Required Sections

| Section | Content | Validated By |
|---|---|---|
| Business Context | Market, problem, opportunity | product-manager |
| Target Users | Personas, segments, needs | product-manager |
| Value Proposition | Why users choose this product | product-manager |
| Revenue Model | How the product makes money | product-manager, finops-analyst |
| Competitive Landscape | Alternatives and differentiation | product-manager |
| Technical Constraints | Platform, performance, compliance | architect |
| Non-Functional Requirements | Scalability, security, availability | architect, sre-engineer |
| Success Metrics | KPIs with targets | product-manager |
| Risk Assessment | Business and technical risks | product-manager, architect |

### BMAD Validation

The product-manager agent validates the BMAD for:
- **Completeness**: All required sections are present
- **Consistency**: No contradictions between sections
- **Measurability**: Success metrics have concrete targets
- **Feasibility**: Technical constraints are compatible with the chosen stack
- **Clarity**: Ambiguous statements are flagged for clarification

A BMAD that fails validation cannot be used to start the SPARC workflow.

## SPARC: The Development Lifecycle

SPARC defines five stages through which every feature passes. Each stage has entry criteria, required activities, and exit criteria. No stage can be skipped.

### S - Specification

**Objective**: Define what will be built with enough precision that it can be designed and implemented without ambiguity.

**Entry criteria**: BMAD is loaded and validated.

**Activities**:
- Decompose BMAD into modules (bounded contexts)
- Define epics per module
- Break epics into user stories with acceptance criteria
- Define API contracts between modules
- Identify cross-cutting concerns (auth, logging, monitoring)

**Exit criteria**: All stories have acceptance criteria. All module boundaries are defined. All API contracts are documented. Product-manager agent has signed off.

### P - Pseudocode / Design

**Objective**: Design the solution at a logical level before writing any implementation code.

**Entry criteria**: Specification is complete and approved.

**Activities**:
- Create pseudocode for complex algorithms
- Design data models and schemas
- Design UI wireframes and user flows
- Define state management approach
- Plan error handling and edge cases
- Create test plans (what will be tested, at what level)

**Exit criteria**: All complex logic has pseudocode. Data models are defined. UI flows are documented. Test plans are complete. Architect agent has signed off.

### A - Architecture

**Objective**: Make and document all technical decisions that constrain implementation.

**Entry criteria**: Design is complete and approved.

**Activities**:
- Select patterns (repository, CQRS, event-driven, etc.)
- Define service boundaries and communication protocols
- Design database schema and migration strategy
- Define infrastructure requirements
- Establish security architecture
- Document architecture decision records (ADRs)
- Review against non-functional requirements from BMAD

**Exit criteria**: All architecture decisions are documented as ADRs. Infrastructure requirements are defined. Security architecture is reviewed. Architect and security-reviewer agents have signed off.

### R - Realization

**Objective**: Build the software according to the specification, design, and architecture.

**Entry criteria**: Architecture is complete and approved.

**Activities**:
- Implement code module by module
- Write unit tests (TDD: test first, then code)
- Write integration tests
- Write end-to-end tests (using Playwright for UI)
- Pass each module through Maker-Checker-Reviewer-Approver
- Sync progress to JIRA and Confluence

**Exit criteria**: All stories are implemented. All tests pass. All modules have passed governance chain. Test coverage meets threshold (default 80%). No critical or high security findings.

### C - Completion

**Objective**: Release, monitor, and learn from the delivery.

**Entry criteria**: Realization is complete and all governance gates have passed.

**Activities**:
- Final integration testing
- Performance testing against NFR benchmarks
- Security scan (final)
- Create release notes
- Deploy to staging
- Smoke test in staging
- Deploy to production
- Configure monitoring and alerting
- Conduct retrospective
- Capture learnings

**Exit criteria**: Production deployment successful. Monitoring is active. Release notes published. Learnings captured and promoted.

## TDD: Test-Driven Development

TDD is not optional in the factory. The enforcement works as follows:

### The TDD Cycle

1. **Write the test first**: Before any implementation code, the engineer agent writes a failing test that describes the expected behavior
2. **Run the test**: Confirm it fails (red)
3. **Write the minimum code** to make the test pass (green)
4. **Refactor**: Clean up the code while keeping tests green
5. **Repeat**

### TDD Enforcement

The checker agent validates TDD compliance by examining:
- **Test timestamps**: Tests must be committed before or in the same commit as implementation code
- **Test coverage**: New code must have corresponding tests
- **Test quality**: Tests must test behavior, not implementation details
- **Test levels**: Unit, integration, and E2E tests are all required for features with UI

### Test Level Requirements

| Test Level | Required For | Minimum Coverage |
|---|---|---|
| Unit tests | All code | 80% line coverage |
| Integration tests | All API endpoints, all database operations | All happy paths + critical error paths |
| E2E tests | All user-facing features with UI | All critical user flows |
| Performance tests | All features with NFR benchmarks | All benchmarked operations |
| Security tests | All authentication/authorization flows | All auth flows, all input validation |

## No Ticket No Work

### Principle

Every piece of work must trace to a ticket. This means:
- No code changes without a JIRA ticket (or local equivalent)
- No branch without a ticket number in the branch name
- No PR without a ticket reference
- No deployment without an approved ticket trail

### Enforcement

The factory enforces this through:

1. **Branch naming**: Branches must match the pattern `{type}/{ticket-id}-{description}` (e.g., `feature/PROJ-42-user-authentication`)
2. **Commit messages**: Must include a ticket reference
3. **PR validation**: The repo-validator agent checks that every PR references a valid ticket
4. **Implementation gate**: The `/implement` command requires a ticket ID

### Ticket Hierarchy

```
Epic (PROJ-10: User Management)
  |
  +-- Story (PROJ-11: As a user, I can register)
  |     +-- Task (PROJ-12: Implement registration API)
  |     +-- Task (PROJ-13: Implement registration UI)
  |     +-- Task (PROJ-14: Write registration tests)
  |
  +-- Story (PROJ-15: As a user, I can log in)
        +-- Task (PROJ-16: Implement login API)
        +-- Task (PROJ-17: Implement login UI)
        +-- Task (PROJ-18: Write login tests)
```

## Maker-Checker-Reviewer-Approver Chain

This is the quality gate chain that every artifact passes through.

### Maker

The **Maker** is the agent that produces the artifact. For code, this is typically the backend-engineer, frontend-engineer, or data-engineer. For specifications, this is the product-manager. For architecture, this is the architect.

**Maker responsibilities**:
- Produce the artifact according to the specification
- Self-check against the definition of done
- Write tests (for code artifacts)
- Document the work

### Checker

The **checker** agent validates the artifact against its specification and contract.

**Checker responsibilities**:
- Verify the artifact matches the specification
- Verify all acceptance criteria are met
- Verify tests exist and pass
- Verify the artifact conforms to its contract (input/output format)
- Flag any deviations

**Checker output**: PASS (proceed to review) or FAIL (return to maker with specific issues)

### Reviewer

The **reviewer** agent (and optionally specialized reviewers like security-reviewer or ux-reviewer) examines the artifact for quality.

**Reviewer responsibilities**:
- Code quality (readability, maintainability, SOLID principles)
- Security (vulnerabilities, injection risks, auth issues)
- Performance (N+1 queries, unnecessary computations, memory leaks)
- Standards compliance (naming conventions, file organization)
- UX quality (for UI artifacts)

**Reviewer output**: APPROVE (proceed to approver), REQUEST_CHANGES (return to maker with specific feedback), or BLOCK (critical issue, cannot proceed)

### Approver

The **approver** agent gives final sign-off.

**Approver responsibilities**:
- Verify that checker passed
- Verify that reviewer approved
- Verify that all governance requirements are met
- Authorize the artifact to proceed to the next stage

**Approver output**: APPROVED (artifact can proceed) or REJECTED (with rationale)

### Chain Visualization

```
Maker (produces artifact)
  |
  v
Checker (validates against spec)
  |-- FAIL --> return to Maker
  |-- PASS
  v
Reviewer (examines quality)
  |-- BLOCK --> return to Maker (critical)
  |-- REQUEST_CHANGES --> return to Maker
  |-- APPROVE
  v
Approver (final sign-off)
  |-- REJECTED --> return to Maker (with rationale)
  |-- APPROVED --> proceed to next stage
```

### Maximum Iterations

To prevent infinite loops, the governance chain has bounded retries:
- **Maker-Checker loop**: Maximum 3 attempts. If the checker fails 3 times, the issue is escalated (logged for human review).
- **Maker-Reviewer loop**: Maximum 3 attempts. If the reviewer requests changes 3 times, the issue is escalated.
- **Total chain**: Maximum 5 total iterations through the full chain. After 5, the work item is blocked and flagged.

## Module Approval Gates

Beyond individual artifacts, entire modules must pass approval gates before they can be considered complete:

### Module Gate Checklist

- [ ] All stories in the module are implemented
- [ ] All tests pass (unit, integration, E2E)
- [ ] Test coverage meets threshold (default 80%)
- [ ] No critical or high security findings
- [ ] All API contracts are honored
- [ ] Documentation is complete (Confluence pages updated)
- [ ] Performance benchmarks met (if NFRs defined)
- [ ] UX review passed (if UI module)
- [ ] Architecture review confirmed no drift from ADRs
- [ ] All JIRA tickets updated to "Done"

### Gate Enforcement

```
/approve --module user-management
```

The approver agent runs the module gate checklist. If any item fails, the module cannot be approved and the specific failures are reported.

## Governance Exceptions

In rare cases, governance can be relaxed for specific purposes:

- **Prototype mode**: Skips checker and reviewer for rapid prototyping. Code produced in prototype mode cannot be promoted to production without going through the full chain.
- **Hotfix mode**: Accelerated chain where checker and reviewer operate with reduced scope. Post-deployment, a full review is required within 48 hours.

These modes are activated explicitly:
```
/implement --mode prototype PROJ-99
/implement --mode hotfix PROJ-100
```

All exceptions are logged in `product repo .claude/delivery/reconciliation/` for audit purposes.
