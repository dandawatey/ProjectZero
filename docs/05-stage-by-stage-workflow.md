# 05 - Stage-by-Stage Workflow

## Overview

This document details each SPARC stage with the specific steps, agents involved, artifacts produced, and exit criteria. Use this as the authoritative reference for what happens at each stage.

---

## Stage 1: Specification

### Objective

Transform the BMAD and PRD into a complete, implementable specification consisting of modules, epics, stories, and acceptance criteria.

### Trigger

```
/spec
```

### Steps

1. **Load context**: The product-manager agent reads `.claude/knowledge/bmad.md` and (if present) `.claude/knowledge/prd.md`.

2. **Identify modules**: Decompose the product into bounded contexts. Each module represents a self-contained area of functionality (e.g., user-management, billing, notifications, reporting).

3. **Define module boundaries**: For each module, define:
   - Responsibility (what it does)
   - Owned entities (data it manages)
   - Public API (how other modules interact with it)
   - Dependencies (what it needs from other modules)

4. **Create epics**: For each module, create one or more epics that represent major feature groups. Each epic maps to a JIRA epic.

5. **Decompose into stories**: For each epic, create user stories in the format:
   ```
   As a [persona], I want to [action] so that [outcome].
   
   Acceptance criteria:
   - Given [context], when [action], then [result]
   - Given [context], when [action], then [result]
   ```

6. **Define API contracts**: For each inter-module communication, define the contract in product repo `.claude/contracts/`:
   ```json
   {
     "contract_id": "user-management-to-billing",
     "source_module": "user-management",
     "target_module": "billing",
     "endpoint": "/api/billing/create-subscription",
     "method": "POST",
     "request_schema": { ... },
     "response_schema": { ... },
     "error_codes": [ ... ]
   }
   ```

7. **Identify cross-cutting concerns**: Authentication, authorization, logging, monitoring, error handling, rate limiting. These become their own stories or are attached as requirements to relevant stories.

8. **Create JIRA artifacts**: Epics and stories are created in JIRA (or as local JSON files in `product repo .claude/delivery/jira/issues/`).

9. **Create Confluence documentation**: The specification is published to the Confluence project hub (or saved locally in `product repo .claude/delivery/confluence/pages/`).

10. **Validate specification**: The checker agent reviews the specification for completeness, consistency, and clarity.

### Agents Involved

| Agent | Role in this stage |
|---|---|
| product-manager | Primary: drives the specification |
| architect | Advisory: validates module boundaries and API contracts |
| checker | Validates the specification |
| approver | Signs off on the specification |

### Artifacts Produced

- `.claude/modules/{module-name}/spec.md` for each module
- product repo `.claude/contracts/{source}-to-{target}.json` for each inter-module contract
- `product repo .claude/delivery/epics/{epic-id}.json` for each epic
- `product repo .claude/delivery/features/{story-id}.json` for each story
- Confluence pages (or local equivalents)
- JIRA epics and stories (or local equivalents)

### Exit Criteria

- [ ] All modules are defined with clear boundaries
- [ ] All epics are created with descriptions
- [ ] All stories have acceptance criteria in Given/When/Then format
- [ ] All inter-module contracts are defined
- [ ] Cross-cutting concerns are identified and assigned
- [ ] Checker has validated completeness
- [ ] Approver has signed off
- [ ] JIRA and Confluence are synced (or local equivalents created)

---

## Stage 2: Pseudocode / Design

### Objective

Design the solution at a logical level. Produce pseudocode for complex logic, data models, UI wireframes, and test plans.

### Trigger

```
/arch --stage design
```

### Steps

1. **Load specification**: The architect agent reads all module specs and contracts.

2. **Design data models**: For each module, define:
   - Entities and their attributes
   - Relationships (one-to-one, one-to-many, many-to-many)
   - Indexes and constraints
   - Migration strategy

3. **Write pseudocode**: For each story with complex logic (algorithms, state machines, business rules), write pseudocode that:
   - Describes the logic step by step
   - Handles all edge cases from acceptance criteria
   - Is implementation-language-agnostic
   - Can be directly translated to code

4. **Design UI flows**: For each user-facing story, the ux-reviewer agent produces:
   - Screen inventory (what screens exist)
   - Navigation flow (how users move between screens)
   - Component hierarchy (what components compose each screen)
   - State management plan (what state each screen needs)

5. **Create test plans**: For each story, define:
   - Unit test scenarios
   - Integration test scenarios
   - E2E test scenarios (if UI)
   - Performance test scenarios (if NFR applies)

6. **Review designs**: The checker validates designs against the specification. The architect validates technical feasibility.

### Agents Involved

| Agent | Role in this stage |
|---|---|
| architect | Primary: drives data model and pseudocode design |
| ux-reviewer | UI flow design and wireframes |
| product-manager | Validates designs match requirements |
| qa-engineer | Creates test plans |
| checker | Validates designs against spec |
| approver | Signs off on designs |

### Artifacts Produced

- `.claude/modules/{module-name}/data-model.md` for each module
- `.claude/modules/{module-name}/pseudocode.md` for complex logic
- `.claude/modules/{module-name}/ui-flows.md` for UI modules
- `.claude/modules/{module-name}/test-plan.md` for each module
- Updated Confluence pages

### Exit Criteria

- [ ] Data models defined for all modules
- [ ] Pseudocode written for all complex logic
- [ ] UI flows documented for all user-facing features
- [ ] Test plans complete for all stories
- [ ] Checker validated against specification
- [ ] Approver signed off

---

## Stage 3: Architecture

### Objective

Make and document all technical decisions. Select patterns, define infrastructure, establish security architecture.

### Trigger

```
/arch
```

### Steps

1. **Select architectural patterns**: Based on the product type and requirements:
   - API style (REST, GraphQL, gRPC)
   - Database strategy (single DB, DB per service, CQRS)
   - Communication (synchronous, event-driven, hybrid)
   - Caching strategy
   - Authentication/authorization approach

2. **Document Architecture Decision Records (ADRs)**: For each significant decision:
   ```markdown
   # ADR-001: Use PostgreSQL with row-level security
   
   ## Status: Accepted
   
   ## Context
   The product handles multi-tenant patient data requiring strict isolation.
   
   ## Decision
   Use PostgreSQL with row-level security policies for tenant isolation.
   
   ## Consequences
   - Positive: Strong isolation without separate databases
   - Positive: Standard PostgreSQL, no vendor lock-in
   - Negative: RLS policies add complexity to queries
   - Negative: Must validate RLS in all integration tests
   ```

3. **Define infrastructure requirements**: The devops-engineer agent specifies:
   - Compute requirements (CPU, memory, scaling rules)
   - Storage requirements (database size, object storage)
   - Networking (VPC, subnets, load balancers)
   - CI/CD pipeline configuration
   - Environment definitions (dev, staging, production)

4. **Establish security architecture**: The security-reviewer agent defines:
   - Authentication mechanism (JWT, session, OAuth2)
   - Authorization model (RBAC, ABAC)
   - Data encryption (at rest, in transit)
   - Secret management approach
   - Input validation and sanitization rules
   - OWASP Top 10 mitigation plan

5. **Define observability architecture**: The sre-engineer agent defines:
   - Logging strategy (structured logs, log levels, retention)
   - Metrics (what to measure, thresholds, alerts)
   - Tracing (distributed tracing setup)
   - Dashboards (key operational dashboards)
   - Incident response runbooks

6. **Review architecture**: The checker validates completeness. The security-reviewer validates security posture. The sre-engineer validates operability.

### Agents Involved

| Agent | Role in this stage |
|---|---|
| architect | Primary: drives all architectural decisions |
| security-reviewer | Security architecture |
| sre-engineer | Observability and operability architecture |
| devops-engineer | Infrastructure and CI/CD |
| finops-analyst | Cost estimation and optimization |
| checker | Validates architecture completeness |
| approver | Signs off on architecture |

### Artifacts Produced

- `.claude/modules/{module-name}/architecture.md` for each module
- `.claude/knowledge/adrs/ADR-{number}.md` for each decision
- `.claude/devops/infrastructure.md` for infrastructure requirements
- `.claude/devops/ci-cd.md` for CI/CD pipeline configuration
- `.claude/operations/observability.md` for monitoring setup
- Updated Confluence pages

### Exit Criteria

- [ ] All architectural decisions documented as ADRs
- [ ] Infrastructure requirements defined
- [ ] Security architecture reviewed and approved
- [ ] Observability architecture defined
- [ ] Cost estimates produced by finops-analyst
- [ ] Checker validated completeness
- [ ] Approver signed off

---

## Stage 4: Realization

### Objective

Build the software. Implement all stories using TDD, passing each through the governance chain.

### Trigger

```
/implement {ticket-id}
```

(Repeated for each story/task)

### Steps

For each story:

1. **Create branch**: `feature/{ticket-id}-{description}`

2. **Write tests first** (TDD):
   - Unit tests based on test plan
   - Integration tests for API endpoints
   - E2E tests for UI flows (using Playwright)

3. **Implement code**:
   - Follow pseudocode from design stage
   - Honor data models from design stage
   - Honor architecture decisions from architecture stage
   - Use shared components from design system (for UI)

4. **Self-check**:
   - All tests pass
   - Code meets linting and formatting standards
   - No TODO/FIXME left unresolved
   - Documentation comments present

5. **Pass governance chain**:
   - **Checker**: Validates against specification and contract
   - **Reviewer**: Code quality, security, performance review
   - **Approver**: Final sign-off

6. **Create PR**: With ticket reference, description, and test evidence

7. **Sync status**: Update JIRA ticket to "In Review" then "Done"

8. **Checkpoint**: Save recovery state in `.claude/recovery/`

### Agents Involved

| Agent | Role in this stage |
|---|---|
| backend-engineer | Implements backend code |
| frontend-engineer | Implements frontend code |
| data-engineer | Implements data pipelines and schemas |
| qa-engineer | Writes and validates tests |
| security-reviewer | Scans for vulnerabilities |
| ux-reviewer | Reviews UI implementation |
| checker | Validates against spec |
| reviewer | Code quality review |
| approver | Final sign-off |
| release-manager | Creates PRs and manages branches |
| integration-agent | Syncs with JIRA/Confluence/GitHub |

### Artifacts Produced

- Source code files (implementation)
- Test files (unit, integration, E2E)
- Git branches and commits
- Pull requests
- Updated JIRA tickets
- Updated Confluence pages
- Recovery checkpoints

### Exit Criteria (Per Story)

- [ ] All acceptance criteria met
- [ ] All tests pass
- [ ] Test coverage meets threshold (80%)
- [ ] No critical or high security findings
- [ ] Checker passed
- [ ] Reviewer approved
- [ ] Approver approved
- [ ] PR created and ready for merge
- [ ] JIRA ticket updated

### Exit Criteria (Per Module)

- [ ] All stories in the module are done
- [ ] Module integration tests pass
- [ ] Module gate checklist complete (see [04-governance-model.md](04-governance-model.md))
- [ ] Module approved via `/approve --module {name}`

---

## Stage 5: Completion

### Objective

Release the product (or module), establish monitoring, conduct retrospective, capture learnings.

### Trigger

```
/release
```

### Steps

1. **Pre-release validation**:
   - All module gates passed
   - Full integration test suite passes
   - Performance tests pass against NFR benchmarks
   - Final security scan (no critical/high findings)
   - Release notes drafted

2. **Staging deployment**:
   - Deploy to staging environment
   - Run smoke tests
   - Validate monitoring and alerting
   - Conduct user acceptance testing (if applicable)

3. **Production deployment**:
   - Deploy to production
   - Run production smoke tests
   - Validate monitoring dashboards
   - Confirm alerting is active

4. **Post-deployment**:
   - Monitor error rates for 24 hours
   - Monitor performance metrics
   - Address any immediate issues

5. **Retrospective**:
   - What went well?
   - What could be improved?
   - What did we learn?

6. **Learning capture**:
   - Capture session-level learnings
   - Promote significant learnings to project level
   - Nominate factory-level learnings for CoE review

7. **Close out**:
   - Update all JIRA tickets to final status
   - Update Confluence with release notes
   - Archive recovery checkpoints
   - Update portfolio status

### Agents Involved

| Agent | Role in this stage |
|---|---|
| release-manager | Primary: orchestrates the release |
| qa-engineer | Final testing validation |
| security-reviewer | Final security scan |
| sre-engineer | Monitoring and observability setup |
| devops-engineer | Deployment execution |
| product-manager | Release notes and stakeholder communication |
| memory-agent | Learning capture and promotion |
| integration-agent | Final JIRA/Confluence sync |

### Artifacts Produced

- Release notes (Confluence and GitHub)
- Deployment records
- Monitoring dashboards
- Alerting rules
- Retrospective document
- Learning entries
- Updated portfolio status

### Exit Criteria

- [ ] Production deployment successful
- [ ] Monitoring active and validated
- [ ] No critical issues in first 24 hours
- [ ] Release notes published
- [ ] All JIRA tickets closed
- [ ] Retrospective conducted
- [ ] Learnings captured
- [ ] Portfolio status updated

---

## Stage Transitions

```
Specification --[approved]--> Design --[approved]--> Architecture --[approved]--> Realization --[all modules approved]--> Completion --[deployed + stable]--> DONE
     |                          |                          |                            |                                      |
     |                          |                          |                            |                                      |
     +-- [failed] --> rework    +-- [failed] --> rework    +-- [failed] --> rework      +-- [failed] --> rework                +-- [incident] --> hotfix
```

Each transition requires explicit approval from the approver agent. There is no implicit progression. The factory tracks the current stage in `.claude/recovery/current-stage.json`.
