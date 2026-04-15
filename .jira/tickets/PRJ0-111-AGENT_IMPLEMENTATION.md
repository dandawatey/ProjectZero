# PRJ0-111: Agent Worker Implementation (MCRA Automation)

**Priority**: P0 (CRITICAL)  
**Status**: Ready to Build  
**Story Points**: 34  
**Epic**: Agent Infrastructure  
**Assigned**: Platform Engineering Team  

## Description

Implement executable agent workers that autonomously build features in new product repos following Maker-Checker-Reviewer-Approver (MCRA) workflow.

Agents work inside product repos (e.g., i-comply), read JIRA tickets, write code via TDD, commit with ticket references, and progress through MCRA gates with automated quality checks + human reviews.

## Acceptance Criteria

### Phase 1: Core Agent Infrastructure (Complete ✅)

- [x] Base agent class (abstract with execute method)
- [x] Agent context management (ticket, repo, workspace)
- [x] Agent result/status tracking
- [x] Maker agents scaffolded (BackendEngineer, FrontendEngineer, DataEngineer)
- [x] Governance agents scaffolded (Checker, Reviewer, Approver)
- [x] Specialist agents scaffolded (TenancyArchitect, ShardingStrategy, EncryptionSpecialist, etc.)
- [x] Agent __init__.py exports ready

### Phase 2: Temporal Workflows (In Progress)

- [ ] FeatureDevelopmentWorkflow (Temporal)
  - [ ] Maker gate activity
  - [ ] Checker gate activity
  - [ ] Reviewer gate activity
  - [ ] Approver gate activity
  - [ ] Gate-to-gate routing logic
  - [ ] Error handling + retry logic

- [ ] EnterpriseBootstrapWorkflow
  - [ ] GitHub repo creation
  - [ ] JIRA project setup
  - [ ] Ticket generation (map PRJ0-98..PRJ0-110 to product-specific)
  - [ ] Agent assignment
  - [ ] MCRA setup
  - [ ] Start P0 workflows in parallel

### Phase 3: Agent Tools (To Do)

- [ ] Git operations
  - [ ] Clone repo
  - [ ] Create branch
  - [ ] Commit with message
  - [ ] Push to remote
  - [ ] Handle conflicts

- [ ] GitHub integration
  - [ ] Create PR
  - [ ] Post check results
  - [ ] Post review comments
  - [ ] Merge PR
  - [ ] Close PR

- [ ] JIRA integration
  - [ ] Read ticket details
  - [ ] Update ticket status
  - [ ] Add comments
  - [ ] Close ticket
  - [ ] Link PR to ticket

- [ ] Code generation
  - [ ] Prompt templates (test, implementation, refactor)
  - [ ] Claude API integration (call /api/v1/chat for code)
  - [ ] Test framework setup (pytest)
  - [ ] Coverage analysis
  - [ ] Linting (ruff)
  - [ ] Type checking (pyright)
  - [ ] Security scanning (OWASP ZAP integration)

### Phase 4: Agent Skills (To Do)

- [ ] `/agent-work` skill
  - [ ] Trigger FeatureDevelopmentWorkflow
  - [ ] Accept ticket, product, repo, user
  - [ ] Return workflow ID + status

- [ ] `/agent-status` skill
  - [ ] Show workflow progress
  - [ ] Current gate, current agent
  - [ ] ETA to completion
  - [ ] Blockers/errors if any

- [ ] `/mcra-status` skill
  - [ ] Show all active MCRA workflows
  - [ ] Status per ticket/gate
  - [ ] Waiting for review/approval list

- [ ] `/bootstrap-product` enhancement
  - [ ] Add `--enterprise-features` flag
  - [ ] Generate agent config in CLAUDE.md
  - [ ] Create JIRA tickets
  - [ ] Assign agents
  - [ ] Start P0 workflows

### Phase 5: Testing (To Do)

- [ ] Unit tests
  - [ ] Agent base class
  - [ ] Maker agent TDD cycle
  - [ ] Checker gate logic
  - [ ] Reviewer gate logic
  - [ ] Approver gate logic

- [ ] Integration tests
  - [ ] FeatureDevelopmentWorkflow end-to-end
  - [ ] GitHub PR creation + closure
  - [ ] JIRA ticket updates
  - [ ] Agent routing + assignment

- [ ] E2E test
  - [ ] Bootstrap i-comply-v2 with agents
  - [ ] Route ICOMPLY-1 to Backend Engineer
  - [ ] Watch TDD cycle complete
  - [ ] Verify PR opened, merged, ticket closed

### Phase 6: Documentation (To Do)

- [ ] Agent developer guide (how to add new agents)
- [ ] Skill documentation (/agent-work usage)
- [ ] MCRA workflow diagram + flowchart
- [ ] Troubleshooting guide
- [ ] Agent configuration per product

## SPARC Phases

### Specification (DONE)
- Wrote AGENT_MCRA_WORKFLOW.md (gate responsibilities)
- Wrote AGENT_IMPLEMENTATION_ROADMAP.md (6-phase plan)
- Defined agent base classes + roles
- Defined MCRA workflow steps

### Pseudocode (IN PROGRESS)
- Designed Temporal workflow structure
- Designed agent execute() flow
- Designed gate-to-gate routing
- Designed error handling (retry, block, escalate)

### Architecture (TO DO)
- Finalize Temporal activity definitions
- Define GitHub API integration layer
- Define JIRA API integration layer
- Define Claude API integration for code generation
- Define skill registration + routing

### Refinement (TO DO)
- Implement agent tools (Git, GitHub, JIRA, Claude)
- Implement Temporal workflow activities
- Implement skill CLI hooks
- Test each gate in isolation
- Test workflows end-to-end

### Completion (TO DO)
- PR review + approval
- E2E test on i-comply-v2
- Deploy to production
- Monitor agent performance
- Gather feedback

## Definition of Done

- [ ] All 6 phases complete
- [ ] FeatureDevelopmentWorkflow tested end-to-end (ICOMPLY-1 → merged)
- [ ] EnterpriseBootstrapWorkflow tested (bootstrap product → agents ready)
- [ ] All 3 Checker/Reviewer/Approver gates working
- [ ] `/agent-work` skill callable and working
- [ ] `/bootstrap-product --enterprise-features` working
- [ ] Unit + integration test coverage ≥80%
- [ ] Documentation complete
- [ ] Commit message references PRJ0-111
- [ ] PR reviewed and approved
- [ ] Merged to main

## Dependencies

- Temporal server running (in platform/backend)
- JIRA integration configured (API token, project key)
- GitHub integration configured (OAuth app, personal access token)
- Claude API accessible (for code generation)
- SQLAlchemy models for agent state (if persisting)

## Blockers

None currently. Ready to build.

## Related Tickets

- PRJ0-98: Tenant Isolation (will be built by agents)
- PRJ0-99: Multi-DB Routing (will be built by agents)
- PRJ0-100: Encryption (will be built by agents)
- PRJ0-101..PRJ0-110: All enterprise features (will be built by agents)

## Success Criteria

✅ **Agent workers autonomous**: No human code writes, agents TDD → PR → merged  
✅ **MCRA fully enforced**: All 4 gates working, no merge without all gates passed  
✅ **New products ready**: Bootstrap product → agents immediately available + configured  
✅ **Parallel execution**: P0 tickets (3) can work simultaneously with dependency ordering  
✅ **Scalable**: Add new agents without changing core workflow logic  

## Timeline

| Phase | Duration | Cumulative |
|-------|----------|-----------|
| Phase 1 (Core infrastructure) | 2w | 2w ✅ DONE |
| Phase 2 (Temporal workflows) | 1w | 3w |
| Phase 3 (Agent tools) | 2w | 5w |
| Phase 4 (Skills + bootstrap) | 1w | 6w |
| Phase 5 (Testing) | 1w | 7w |
| Phase 6 (Documentation) | 1w | 8w |

**Total**: 8 weeks to full operational agent workforce

## Next Steps

1. **Complete Phase 2**: Finish Temporal workflow activities
2. **Start Phase 3**: Implement agent tools (Git, GitHub, JIRA, Claude)
3. **Parallel Phase 4-5**: Skills + testing
4. **E2E test**: Bootstrap product, build ICOMPLY-1 with agents
5. **Deploy**: Merge to main, ready for production

---

**Owner**: Platform Engineering  
**Contributors**: Claude (agent implementations), Team (testing, integration)
