# Agent MCRA Workflow — How Agents Build Features in New Products

## Overview

When a new product is bootstrapped (e.g., `i-comply`), it inherits:
1. Full agent team definitions
2. MCRA workflow automation
3. Feature ticket routing to agents
4. Automatic code generation, testing, review, approval

Agents work INSIDE the product repo following 4-gate MCRA pattern:
- **Maker** (developer agent) → writes tests + code
- **Checker** (governance agent) → validates quality gates
- **Reviewer** (senior engineer) → code/architecture review
- **Approver** (CTO/CEO) → business sign-off + merge

---

## Agent Responsibilities in MCRA

### Maker (Feature Agent)
**Agents**: Backend Engineer, Frontend Engineer, Data Engineer, etc. (specialized agents: Tenancy-Architect, Sharding-Strategy, etc.)

**Gate Entry**: JIRA ticket created (PRJ0-98, ICOMPLY-1, etc.)

**Activities**:
1. Read ticket from JIRA (acceptance criteria, acceptance criteria, story points)
2. Clone product repo (git clone, checkout feature branch)
3. **TDD First**: Write failing test cases (pytest, unit + integration tests)
4. **Implement**: Write minimum code to pass tests
5. **Refactor**: Clean code, improve performance, add docstrings
6. **Commit**: Frequent commits referencing ticket ID
7. **Push**: Push to feature branch (not main)
8. **Open PR**: Create pull request with description + test evidence
9. **Route to Checker**: Notify Checker gate
10. **Respond to feedback**: Address review comments, update PR

**Output**:
- Feature branch with code + tests
- PR with ≥80% coverage, passing linting/types
- Commit history referencing ticket
- Description linking to ticket acceptance criteria

**Tools/Capabilities**:
- Git (clone, branch, commit, push)
- Python/TypeScript (code generation)
- pytest/Jest (test framework)
- pyright/tsc (type checking)
- ruff/eslint (linting)
- JIRA API (read ticket, update status)
- GitHub API (create PR, respond to review)

---

### Checker (Governance Agent)
**Agent**: Checker (governance-team/checker.md)

**Gate Entry**: Maker opens PR, requests review

**Activities**:
1. Read PR (commits, code, test files)
2. **Run automated checks** (/check equivalent):
   - Run full test suite
   - Calculate coverage (≥80%? ✅/❌)
   - Run linting (zero errors? ✅/❌)
   - Run type checking (zero errors? ✅/❌)
   - Security scan (OWASP, dependencies)
   - Check ticket reference in commits
3. **Generate report**: Pass/fail summary
4. **If FAIL**: Comment on PR with failures, request fixes
5. **If PASS**: Approve and route to Reviewer
6. **Block merge**: Until Checker gate passes

**Output**:
- Automated check results (GitHub check run)
- Pass/fail status on PR
- Detailed error messages if failed

**Tools**:
- pytest, pyright, ruff
- OWASP ZAP (security scan)
- GitHub API (check runs, comments)
- Coverage tools

---

### Reviewer (Senior Engineer Agent)
**Agents**: Reviewer (governance-team/reviewer.md), specialized agents (e.g., Tenancy-Architect for PRJ0-98)

**Gate Entry**: Checker gate passed, PR ready for review

**Activities**:
1. Read PR (code changes, test coverage, architecture)
2. **Code review**:
   - Does code match acceptance criteria?
   - Is implementation efficient?
   - Are error cases handled?
   - Is code maintainable?
3. **Architecture review** (if applicable):
   - Does design match ADR?
   - Are constraints respected (tenant isolation, data residency)?
   - Any technical debt introduced?
4. **Test review**:
   - Are tests comprehensive?
   - Do tests cover edge cases?
   - Is coverage ≥80%?
5. **Comment or approve**:
   - If issues: Comment with specific feedback + request changes
   - If OK: Approve PR, route to Approver
6. **Iterate**: Respond to maker's changes, re-review

**Output**:
- PR review comments (specific, actionable)
- Approval status (GitHub review)
- Recommendation to Approver

**Tools**:
- GitHub API (PR review, comments)
- AST parsing (code analysis)
- ADR repository (architecture decisions)

---

### Approver (Leadership Gate)
**Agents**: Approver (governance-team/approver.md), CTO/CEO agents (cxo-team)

**Gate Entry**: Reviewer approved, ready for final sign-off

**Activities**:
1. Read PR + reviews (Maker work, Checker results, Reviewer approval)
2. **Verify**:
   - Does implementation match business requirements (ticket)?
   - Are governance rules respected?
   - Any compliance concerns?
   - Is this the right approach?
3. **Decision**:
   - **APPROVE**: Merge to main, deploy, close ticket
   - **REQUEST CHANGES**: Comment with concerns, route back to Maker
   - **REJECT**: Close PR, flag as blocked on Jira, explain why
4. **Merge**: If approved, merge PR to main (trigger deployment)
5. **Close ticket**: Update JIRA status to Done
6. **Notify**: Alert team of completion

**Output**:
- Final approval status (GitHub)
- JIRA ticket closure
- Merge commit to main

**Tools**:
- GitHub API (merge, close PR)
- JIRA API (update status, close ticket)
- Slack (notifications)

---

## Workflow Diagram

```
JIRA Ticket Created (e.g., PRJ0-98: Tenant Isolation)
    ↓
[MAKER GATE] Backend Engineer + Tenancy-Architect
    • Read ticket acceptance criteria
    • Create feature branch (git checkout -b prj0-98-tenant-isolation)
    • TDD: Write test_tenant_isolation.py (FAILING)
    • Implement: src/tenancy.py (make tests PASS)
    • Refactor: Clean code, add docstrings
    • Commit: "feat: tenant isolation RLS + audit (PRJ0-98)"
    • Push: git push origin prj0-98-tenant-isolation
    • Open PR: Link to PRJ0-98, describe changes
    • Route to Checker
    ↓
[CHECKER GATE] Checker Agent
    • Run: pytest tests/test_tenant_isolation.py
    • Coverage: 85% ✅
    • Lint: ruff check src/tenancy.py ✅
    • Types: pyright src/tenancy.py ✅
    • Security: OWASP ZAP scan ✅
    • Commit ref: PRJ0-98 found ✅
    • Result: ALL PASS ✅
    • Route to Reviewer
    ↓
[REVIEWER GATE] Reviewer Agent + Tenancy-Architect
    • Code review: "Looks good. RLS policies correct. Edge cases handled."
    • Architecture review: "Matches ADR-tenancy-model. Good use of contextvars."
    • Test review: "Coverage 85%, all edge cases tested. Excellent."
    • Decision: APPROVE ✅
    • Route to Approver
    ↓
[APPROVER GATE] Approver Agent (CTO)
    • Business check: "Tenant isolation required for compliance. ✅"
    • Governance check: "No security issues. Audit logging enabled. ✅"
    • Decision: APPROVE ✅
    • Merge to main
    • Close PRJ0-98 ✅
    • Deploy to staging
    ↓
[DONE] Feature Complete
    • Tenant isolation live in product
    • Tests passing, audit log active
    • Ready for P1 tickets (PRJ0-99, PRJ0-100)
```

---

## Feature Workflow Integration

### 1. Bootstrap New Product (e.g., i-comply)

```bash
/bootstrap-product \
  --name i-comply \
  --enterprise-features tenant-isolation,multi-db,encryption
```

**Generates**:
- New git repo (i-comply)
- CLAUDE.md inherited from factory
- Agent team definitions copied
- MCRA workflow automation installed
- Initial JIRA tickets seeded (PRJ0-98 → ICOMPLY-1, etc.)

### 2. Feature Development Workflow

**Trigger**: New JIRA ticket created (ICOMPLY-1: Tenant Isolation)

**Automation**:
1. Temporal workflow started: `feature_development_workflow(ticket_id="ICOMPLY-1")`
2. Agent router determines who works on it:
   - ICOMPLY-1 is about "Tenant Isolation" → assign to Backend Engineer + Tenancy-Architect
3. Maker gate begins:
   - Agent clones i-comply repo
   - Reads ICOMPLY-1 acceptance criteria
   - Creates feature branch
   - Writes tests (TDD)
   - Implements feature
   - Opens PR
4. Checker gate automated:
   - Runs /check command
   - Tests pass? Coverage ≥80%? Lint/types clean? ✅
   - Approve or request fixes
5. Reviewer gate:
   - Reviewer agent (or human) reviews code
   - Approves or requests changes
6. Approver gate:
   - Final sign-off
   - Merge + deploy
   - JIRA closure

### 3. Parallel Execution (P0 Phase)

P0 has 3 tickets: PRJ0-98, PRJ0-99, PRJ0-100
- Mapped to: ICOMPLY-1, ICOMPLY-2, ICOMPLY-3

**Execution Strategy**:
```
Time 0:  ICOMPLY-1 → Maker (Backend Eng + Tenancy-Architect)
         ICOMPLY-2 → Maker (Data Eng + Sharding-Strategy)  [waiting on ICOMPLY-1]
         ICOMPLY-3 → Maker (Backend Eng + Encryption-Spec) [waiting on ICOMPLY-1]

Time +2w: ICOMPLY-1 DONE ✅
          ICOMPLY-2 → Maker (now has RLS from ICOMPLY-1)
          ICOMPLY-3 → Maker (now has audit logs from ICOMPLY-1)

Time +4w: ICOMPLY-2 DONE ✅ (sharding built on isolation)
Time +6w: ICOMPLY-3 DONE ✅ (encryption built on isolation + sharding)

P0 COMPLETE: 6 weeks. Move to P1.
```

**Tickets Unblock**: Dependencies defined in .jira/tickets/ENTERPRISE_GAPS_P0_P3.md

---

## Agent Implementation Requirements

For agents to WORK in MCRA, each agent needs:

### 1. Agent Code (Python)
```python
class BackendEngineer(Agent):
    """Agent: Backend Engineer"""
    
    async def work_on_ticket(self, ticket: JiraTicket):
        # Clone product repo
        repo = await git_clone(ticket.product_repo)
        
        # TDD: Write tests
        test_file = await self.write_tests(ticket.acceptance_criteria)
        await subprocess_run(f"pytest {test_file} -v")  # Should FAIL
        
        # Implement
        impl_file = await self.write_implementation(ticket.acceptance_criteria)
        result = await subprocess_run(f"pytest {test_file} -v")  # Should PASS
        
        # Commit
        await git_commit(f"feat: {ticket.title} ({ticket.id})")
        await git_push()
        
        # Open PR
        pr = await github.create_pr(...)
        await jira.update_status(ticket.id, "In Review")
```

### 2. Temporal Workflow
```python
@workflow
async def feature_development_workflow(ticket_id: str):
    ticket = await jira.get_ticket(ticket_id)
    
    # Maker gate
    maker = select_maker_agent(ticket)
    await maker.work_on_ticket(ticket)
    
    # Checker gate
    checker = Checker()
    result = await checker.run_checks(ticket)
    if not result.passed:
        await maker.fix_issues(result.errors)
        await workflow.wait(timeout=3600)  # Wait for fixes
    
    # Reviewer gate
    reviewer = select_reviewer_agent(ticket)
    await reviewer.review_pr(ticket)
    
    # Approver gate
    approver = Approver()
    await approver.approve_and_merge(ticket)
```

### 3. Agent Skills (CLI)
```bash
/agent-work \
  --ticket PRJ0-98 \
  --product i-comply \
  --agent backend-engineer
  
# Triggers: Backend Engineer starts TDD cycle on i-comply repo for PRJ0-98
```

### 4. Integration Points
- **JIRA**: Read tickets, update status
- **GitHub**: Clone repos, create PRs, merge
- **Git**: Commits, branches, push
- **Slack**: Notify team of progress
- **Temporal**: Workflow orchestration

---

## Configuration (Per New Product)

Each new product's CLAUDE.md includes:

```yaml
agents:
  enabled: true
  mcra_workflow: true
  maker_agents:
    - backend-engineer
    - frontend-engineer
    - tenancy-architect      # From enterprise framework
    - sharding-strategy      # From enterprise framework
  checker: checker            # Governance gate
  reviewer: reviewer          # Governance gate
  approver: approver          # Governance gate

jira_integration:
  enabled: true
  project_key: ICOMPLY
  board: i-comply Feature Board

github_integration:
  enabled: true
  org: dandawatey
  repo: i-comply
  pr_template: |
    ## Ticket: ${ticket_id}
    ${ticket_description}
    
    ### Acceptance Criteria
    ${ticket_acceptance_criteria}
    
    ### Test Evidence
    - Coverage: ${coverage_pct}%
    - Tests passed: ${test_count}
    - Lint: ${lint_status}
    - Types: ${types_status}
```

---

## Summary: What Gets Built Per Ticket

For **PRJ0-98 → ICOMPLY-1** (Tenant Isolation):

| Phase | Who | What | Duration |
|-------|-----|------|----------|
| Maker | Backend Eng + Tenancy-Arch | Write tests, implement RLS + audit logging | 1.5w |
| Checker | Checker Agent | Run /check, verify ≥80% coverage + linting/types | 1d |
| Reviewer | Reviewer + Tenancy-Arch | Code + architecture review | 1-2d |
| Approver | CTO/CEO | Final approval, merge, deploy | 1d |

**Deliverable**: `i-comply` repo has full tenant isolation (RLS, audit logs, context middleware) + tests + documentation.

**Result**: Next ticket (ICOMPLY-2) can build on this foundation (multi-DB sharding).

---

## Next Steps

**To operationalize agents in MCRA**:

1. **Implement agent workers** (Python + Temporal activities)
2. **Wire JIRA → agent router** (ticket type → agent assignment)
3. **Extend product bootstrap** (inherit agents + MCRA workflow)
4. **Create skills** (/agent-work, /start-feature, /mcra-status)
5. **Test on i-comply** (bootstrap product, route ICOMPLY-1 to agents)

**Estimate**: 4-6 weeks to full operational MCRA workflow.

---

## Success Criteria

✅ **Agents automatically build enterprise features in new products**
- New ticket → Agent picks up
- TDD → Implement → PR → Reviewer → Approver → Merged
- All 13 enterprise capabilities (P0-P3) built by agents
- ≥80% coverage, zero linting/type errors
- Ticket references in every commit
- Zero manual code writes

✅ **Maker-Checker-Reviewer-Approver workflow enforced**
- Checker gate blocks bad code
- Reviewer gate enforces architecture
- Approver gate enforces business rules
- Every feature traced to JIRA ticket

✅ **Parallel execution possible**
- P0 3 tickets in parallel (dependencies respected)
- 6 weeks to P0 complete
- Then P1 (4 weeks), P2 (6 weeks)

✅ **Scalable to any new product**
- `/bootstrap-product --enterprise-features` scaffolds agents
- Agents ready to work immediately
- MCRA workflow inherited, not recreated
