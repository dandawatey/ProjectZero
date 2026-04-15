# Agent Implementation Roadmap — Making Agents Work in MCRA

## Current State
- ✅ Agent definitions exist (AGENT_REGISTRY.md)
- ✅ Enterprise gap tickets created (PRJ0-98..PRJ0-110)
- ✅ MCRA workflow documented
- ❌ Agent workers not implemented (can't actually execute)

## What's Missing

### 1. Agent Worker Implementation (Python + Temporal)
Each agent needs executable code:
```
.claude/agents/
  backend-engineer/
    worker.py          ← Temporal activity implementation
    tools.py           ← Git, JIRA, GitHub, code generation
    prompts.py         ← LLM prompts for code generation
  
  tenancy-architect/
    worker.py          ← Specialized for multi-tenancy
    rls-templates.py   ← RLS policy templates
    test-templates.py  ← Tenant isolation test templates
```

### 2. Agent Router (JIRA → Agent Assignment)
```
JIRA ticket created → Analyze ticket → Match to agent skills → Assign
  
Example:
- Title: "Tenant Isolation (RLS + Audit)"
- Tags: [multi-tenancy, security, database]
→ Route to: Backend Engineer + Tenancy-Architect
```

### 3. MCRA Workflow Orchestration (Temporal)
```
Temporal workflow: feature_development_workflow
  • Maker gate: Agent writes code (TDD)
  • Checker gate: Automated quality checks (/check)
  • Reviewer gate: Code review (human or agent)
  • Approver gate: Final sign-off (human or agent)
```

### 4. API/CLI Integration
```
/agent-work --ticket ICOMPLY-1 --product i-comply
→ Triggers Temporal workflow
→ Agents start working
→ Monitor progress with /agent-status
```

### 5. GitHub/JIRA Integration
```
Agent operations:
  • git clone product repo
  • Create feature branch
  • Commit with ticket ref
  • Push to GitHub
  • Create PR
  • Update JIRA status
  • Listen for PR review feedback
```

---

## Implementation Phases

### Phase 1: Proof of Concept (2 weeks)
**Goal**: Get ONE agent working end-to-end on ONE ticket

**Scope**:
- Implement Backend Engineer worker (Python)
- Temporal activity: write_tests + implement_feature
- GitHub integration: clone, branch, commit, push, PR
- JIRA integration: read ticket, update status
- Test on i-comply: ICOMPLY-1 (Tenant Isolation)

**Deliverable**:
- Backend Engineer can automatically:
  1. Read ICOMPLY-1 from JIRA
  2. Clone i-comply repo
  3. Create feature branch
  4. Write test_tenant_isolation.py (TDD)
  5. Implement src/tenancy.py
  6. Commit + push
  7. Open PR

**Success**: PR created, test results visible on GitHub

### Phase 2: Checker Gate (1 week)
**Goal**: Automate quality validation

**Scope**:
- Implement Checker worker
- Temporal activity: run_checks (pytest, ruff, pyright, security scan)
- GitHub integration: Post check results on PR
- Block PR if ≥80% coverage, lint/types fail

**Deliverable**:
- Checker automatically validates PR from Maker
- GitHub check run shows pass/fail
- PR blocked if Checker gate fails

**Success**: Checker blocks bad code, approves good code

### Phase 3: Reviewer + Approver Gates (2 weeks)
**Goal**: Code review + business approval automation

**Scope**:
- Implement Reviewer worker (specialized agents for tenancy, encryption, sharding)
- Implement Approver worker
- GitHub integration: PR review comments
- JIRA integration: Mark ticket as "In Review", "Done"
- Temporal: route Reviewer agent based on ticket type

**Deliverable**:
- Reviewer automatically reviews PR (code + architecture)
- Approver automatically signs off (business check)
- PR auto-merged when all gates pass
- JIRA ticket auto-closed

**Success**: End-to-end feature goes from ticket → merged in main

### Phase 4: Specialized Agents (3 weeks)
**Goal**: Domain-specific agents for enterprise capabilities

**Scope**:
- Implement Tenancy-Architect worker
- Implement Sharding-Strategy worker
- Implement Encryption-Specialist worker
- Implement Audit-Log-Architect worker
- Implement Compliance-Test-Engineer worker
- Implement Geo-Failover-Architect worker
- Implement DR-Orchestrator worker
- Implement Network-Security-Architect worker

**Each agent**:
- LLM prompts for their domain (e.g., tenancy.prompts: "Design RLS policies for tables: users, customer_data, api_keys")
- Code templates (e.g., rls-templates.py: RLS policy templates)
- Test templates (e.g., test-templates.py: tenant isolation test cases)
- Integration into workflows (routed based on ticket type)

**Deliverable**:
- Each specialized agent can independently:
  1. Design solution (generate ADR)
  2. Write tests (domain-specific)
  3. Implement solution
  4. Validate isolation/security

**Success**: PRJ0-98 (Tenant Isolation) fully built by Tenancy-Architect + Backend Engineer

### Phase 5: Parallel Execution (2 weeks)
**Goal**: Multiple agents working simultaneously

**Scope**:
- Implement dependency tracking (PRJ0-98 blocks PRJ0-99, PRJ0-99 blocks PRJ0-100)
- Implement ticket queue/backlog system
- Implement agent scheduling (don't overload 1 agent)
- Implement progress monitoring dashboard

**Deliverable**:
- ICOMPLY-1, ICOMPLY-2, ICOMPLY-3 can start in sequence
- P0 tickets complete in 6 weeks (not 18)
- Dashboard shows: ticket → agent → status → ETA

**Success**: All 3 P0 tickets executed in parallel with dependencies respected

### Phase 6: Product Bootstrap Integration (1 week)
**Goal**: New products inherit full MCRA + agent team

**Scope**:
- Extend `/bootstrap-product` command
- Add option: `--enterprise-features` (tenant-isolation, multi-db, encryption, etc.)
- Auto-generate JIRA tickets (ICOMPLY-1..ICOMPLY-13)
- Auto-assign agents to tickets
- Auto-start Temporal workflows

**Deliverable**:
```bash
/bootstrap-product \
  --name my-product \
  --enterprise-features tenant-isolation,multi-db,encryption,compliance
  
→ Creates my-product repo
→ Generates JIRA tickets (MY-PRODUCT-1..MY-PRODUCT-13)
→ Assigns agents
→ Starts feature_development_workflow for P0
→ Dashboard shows: P0 agents working, ETA 6 weeks
```

**Success**: New product immediately inherits agent team + MCRA workflow

---

## Technical Stack

### Required
- **Temporal**: Workflow orchestration (already in factory)
- **Python**: Agent worker code
- **JIRA SDK**: Read tickets, update status
- **GitHub SDK**: Clone, branch, commit, push, PR, merge
- **LLM Integration**: Claude API for code generation (via /api/v1/chat)
- **SQLAlchemy**: Database operations (for agents working with schemas)

### Optional but Recommended
- **Langchain**: LLM prompting + chaining
- **Pydantic**: Data validation
- **Pytest**: Test framework (agents will use this)

---

## Success Metrics

| Phase | Metric | Target |
|-------|--------|--------|
| Phase 1 | Backend Engineer can write + test feature | 1 PR per day |
| Phase 2 | Checker blocks 100% of failed code | 0 bad merges |
| Phase 3 | Reviewer + Approver gates working | 4-gate MCRA in use |
| Phase 4 | Specialized agents can design solutions | Design review pass rate ≥90% |
| Phase 5 | P0 3 tickets in parallel (6w total) | Faster than sequential |
| Phase 6 | New product = working agent team | 0 manual setup required |

---

## Estimated Timeline

| Phase | Duration | Cumulative |
|-------|----------|-----------|
| Phase 1 (Backend Eng worker) | 2 weeks | 2 weeks |
| Phase 2 (Checker gate) | 1 week | 3 weeks |
| Phase 3 (Reviewer + Approver) | 2 weeks | 5 weeks |
| Phase 4 (Specialized agents) | 3 weeks | 8 weeks |
| Phase 5 (Parallel execution) | 2 weeks | 10 weeks |
| Phase 6 (Bootstrap integration) | 1 week | 11 weeks |

**Total**: 11 weeks to full operational MCRA agent workflow

---

## Next Decision

### A. Build Agent Workers (11 weeks)
- Implement full MCRA workflow with agents
- Agents automatically build all 13 enterprise features (P0-P3)
- New products = zero manual setup
- Long-term scalability

### B. Agents as Guides Only (Now)
- Keep agents as "role definitions" + documentation
- Manually scaffold features per ticket (existing workflow)
- Agents inform architecture decisions
- Faster initial delivery, more manual work per product

### C. Hybrid (6 weeks)
- Implement 1-2 critical agent workers (Backend Engineer, Tenancy-Architect)
- Prove pattern works on ICOMPLY-1
- Scale to remaining agents
- Balance speed + automation

**Recommendation**: **Option C (Hybrid)**
- Unblock i-comply product build NOW (manual ICOMPLY-1)
- Build agent automation in parallel (Phase 1-2)
- By week 6: agents fully operational for ICOMPLY-2, ICOMPLY-3
- By week 11: agents operational for all new products

---

## First Step

Start with Backend Engineer worker (Phase 1):

```python
# .claude/agents/engineering-team/backend-engineer-worker.py

class BackendEngineerWorker:
    """Temporal activity: Backend Engineer works on tickets"""
    
    async def work_on_ticket(self, ticket_id: str, product_name: str):
        """
        TDD cycle:
        1. Read ticket from JIRA
        2. Clone product repo
        3. Write test file (make it fail)
        4. Write implementation (make tests pass)
        5. Commit with ticket ref
        6. Push to GitHub
        7. Create PR
        8. Wait for review
        """
        # Implementation
```

**Assignment**: Who builds this?
- Human engineer? (1 week, then ongoing MCRA management)
- Bootstrap with Claude? (1 day design + scaffolding, human finishes)
