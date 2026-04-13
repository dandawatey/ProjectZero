# 04 - Governance Model

## Core Rule

All governance is enforced through Temporal workflows. Not documentation. Not honor system. Temporal.

If a governance gate fails, the workflow blocks. No workaround. No override. Fix the issue, signal the workflow, continue.

## Integration Gate

Before ANY workflow executes, the integration gate validates:

| Integration | What's Checked | Failure = |
|---|---|---|
| GitHub | Token valid, org access, repo perms | All workflows blocked |
| JIRA | Token valid, project access, write perms | All workflows blocked |
| Confluence | Token valid, space access, write perms | All workflows blocked |
| Temporal | Server reachable, namespace exists | All workflows blocked |
| Postgres | Connected, schema current, migrations applied | All workflows blocked |
| Redis | Connected, read/write operational | All workflows blocked |
| Anthropic | API key valid, model accessible | All workflows blocked |

No keys = no workflows. Period.

Integration gate runs at `/factory-init` and is re-validated at workflow start. Stale tokens caught at execution time, not just init time.

## BMAD Before Build

No development workflow starts without a validated BMAD (Business Model Architecture Document).

Two paths to BMAD:
1. **Bring your own**: Load existing BMAD/PRD via `/spec --type bmad --input path/to/bmad.md`
2. **Generate**: Run `/vision-to-prd` -- Temporal workflow generates PRD + BMAD from a vision statement

BMAD validation (Temporal activity):
- All required sections present (business context, personas, value prop, metrics, risks)
- No contradictions between sections
- Success metrics have concrete targets
- Technical constraints compatible with chosen stack

Failed BMAD validation = workflow blocks until BMAD is fixed and re-validated.

## SPARC Stages = Temporal Workflow Stages

The 8-phase model maps to Temporal workflows. Each phase is a workflow (or set of workflows). Phase transitions are Temporal signals.

```
Phase 0 (Factory Init)     = FactoryInitWorkflow
Phase 1 (Product Creation) = BootstrapProductWorkflow
Phase 2a (Vision-to-PRD)   = VisionToPrdWorkflow
Phase 2b (Business Disc.)  = BusinessDocsWorkflow (discovery)
Phase 3 (Specification)    = SpecificationWorkflow
Phase 4 (Architecture)     = ArchitectureWorkflow
Phase 5 (Implementation)   = ImplementationWorkflow (per story)
Phase 6 (Quality+Release)  = ReleaseWorkflow
Phase 7 (Business Plan)    = BusinessDocsWorkflow (planning)
Phase 8 (Operations)       = MonitorWorkflow, OptimizeWorkflow
```

**Temporal enforces ordering.** You cannot start Phase 5 without Phase 4 completion signal. You cannot start Phase 4 without Phase 3 completion signal. No skipping.

## TDD Enforcement

Implementation workflows (Phase 5) enforce TDD:

1. `WriteTestsActivity` -- agent writes tests FIRST
2. `RunTestsActivity` -- confirms tests fail (red)
3. `ImplementActivity` -- agent writes implementation
4. `RunTestsActivity` -- confirms tests pass (green)
5. `RefactorActivity` -- agent refactors, tests still green
6. `CoverageCheckActivity` -- validates coverage >= threshold (default 80%)

If `CoverageCheckActivity` fails, workflow blocks. No merge. No PR. Write more tests.

## No Ticket No Work

Every workflow step creates or updates JIRA tickets. Enforced by Temporal activities.

- `/spec` creates epics and stories in JIRA
- `/implement` requires a ticket ID, creates branch `feature/{TICKET-ID}-{desc}`
- Every commit message includes ticket reference
- Every PR references a ticket
- `/release` updates all tickets to Done

No ticket ID = `ImplementationWorkflow` refuses to start.

Branch naming enforced: `{type}/{ticket-id}-{description}`. Temporal activity validates before creating branch.

## Maker-Checker-Reviewer-Approver

The governance chain is a **Temporal child workflow** with signal-based gates.

```
ImplementationWorkflow
  |
  +-- starts --> GovernanceChainWorkflow (child)
       |
       +-- MakerActivity: agent produces artifact
       |
       +-- CheckerActivity: validates against spec
       |     |-- FAIL --> signal: return to Maker (max 3 retries)
       |     +-- PASS --> continue
       |
       +-- ReviewerActivity: quality, security, standards
       |     |-- BLOCK --> signal: return to Maker (critical issue)
       |     |-- REQUEST_CHANGES --> signal: return to Maker (max 3 retries)
       |     +-- APPROVE --> continue
       |
       +-- ApproverActivity: final sign-off
             |-- REJECTED --> signal: return to Maker (with rationale)
             +-- APPROVED --> signal: parent workflow continues
```

### Bounded Retries

- Maker-Checker loop: max 3 attempts
- Maker-Reviewer loop: max 3 attempts
- Total chain iterations: max 5
- Exhausted retries = workflow pauses + escalation alert in Control Tower

### Signal-Based Gates

Each gate is a Temporal signal. External reviewers (humans) can also send signals through the Control Tower API. This enables human-in-the-loop governance when needed.

## Stage Gates

Temporal enforces stage completion before allowing progression:

### Phase 3 (Spec) Exit Gate
- All modules defined with boundaries
- All stories have acceptance criteria
- All contracts defined
- JIRA tickets created
- Checker + Approver signed off

### Phase 4 (Arch) Exit Gate
- All ADRs documented
- Infrastructure requirements defined
- Security architecture reviewed
- Checker + Approver signed off

### Phase 5 (Implement) Exit Gate (per module)
- All stories implemented
- All tests pass
- Coverage >= threshold
- No critical security findings
- All governance chains completed
- All JIRA tickets updated

### Phase 6 (Release) Exit Gate
- All module gates passed
- Full integration test suite green
- Final security scan clean
- Performance benchmarks met
- Release notes published
- Production deployment successful
- Monitoring active

Each gate = Temporal activity that checks conditions. Conditions not met = workflow blocks.

## Governance Exceptions

Two modes, both logged:

### Prototype Mode
```
/implement --mode prototype TICKET-99
```
Skips checker and reviewer. Code CANNOT be promoted to production. Temporal tags the workflow as prototype. Release workflow rejects prototype code.

### Hotfix Mode
```
/implement --mode hotfix TICKET-100
```
Accelerated chain (reduced reviewer scope). Post-deployment, Temporal schedules a full review workflow within 48 hours. If full review not completed in 48h, alert fires.

All exceptions recorded in Postgres audit trail. Visible in Control Tower.

## Audit Trail

Every governance decision is a Temporal event. Immutable. Queryable.

Stored:
- Which agent made the decision
- Which gate was applied
- Pass or fail
- Rationale (for failures and rejections)
- Timestamp
- Workflow ID (traceable to specific feature/ticket)

Accessible via:
- Temporal UI (raw workflow history)
- Control Tower (governance dashboard)
- Postgres queries (for reporting)
- Confluence (auto-published governance reports)
