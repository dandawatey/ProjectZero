# /agent-work

Invoke agents to work on JIRA tickets in product development workflow.

## Usage

```bash
/agent-work \
  --ticket ICOMPLY-1 \
  --product i-comply \
  --repo https://github.com/org/i-comply.git \
  --user <user_id> \
  [--workspace /tmp/agents]
```

## What It Does

Triggers `FeatureDevelopmentWorkflow` (Temporal):

1. **Maker Gate** (Backend Engineer / Specialist)
   - Clones product repo
   - Reads JIRA ticket acceptance criteria
   - Creates feature branch
   - **TDD**: Writes failing tests, implements code, refactors
   - Commits with ticket reference
   - Opens PR on GitHub

2. **Checker Gate** (Automated)
   - Runs pytest (tests must pass)
   - Checks coverage ≥80%
   - Runs ruff (linting)
   - Runs pyright (type checking)
   - Runs OWASP ZAP (security scan)
   - Verifies ticket reference in commits
   - Blocks PR if any gate fails

3. **Reviewer Gate** (Code Review Agent)
   - Reviews code quality
   - Reviews architecture decisions
   - Reviews test coverage
   - Approves or requests changes

4. **Approver Gate** (Leadership)
   - Final business sign-off
   - Governance check
   - Merges PR to main
   - Closes JIRA ticket

## Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `--ticket` | Yes | JIRA ticket ID (e.g., ICOMPLY-1, PRJ0-98) |
| `--product` | Yes | Product name (e.g., i-comply) |
| `--repo` | Yes | Git repo URL |
| `--user` | Yes | User ID triggering the workflow |
| `--workspace` | No | Base path for agent work (default: /tmp/agents) |

## Examples

### Start Backend Engineer on Tenant Isolation

```bash
/agent-work \
  --ticket ICOMPLY-1 \
  --product i-comply \
  --repo https://github.com/dandawatey/i-comply.git \
  --user yogesh@example.com
```

**Workflow**:
```
Backend Engineer TDD cycle starts
  → Creates feature branch: icomply-1-tenant-isolation
  → Writes tests/test_tenant_isolation.py
  → Implements src/tenancy.py
  → Commits "feat: tenant isolation (ICOMPLY-1)"
  → Opens PR

Checker gate verifies:
  ✓ pytest: 42 passed
  ✓ coverage: 85% (≥80%)
  ✓ lint: 0 errors
  ✓ types: 0 errors
  ✓ security: 0 issues
  ✓ ticket ref: ICOMPLY-1 found

Reviewer approves:
  ✓ Code quality: "Looks good"
  ✓ Architecture: "Matches ADR"
  ✓ Tests: "Comprehensive coverage"

Approver signs off:
  ✓ Business req: "Tenant isolation required for compliance"
  ✓ Governance: "No security issues"
  → PR merged to main
  → ICOMPLY-1 closed as Done
```

### Monitor Workflow Progress

```bash
/agent-status --ticket ICOMPLY-1 --product i-comply
```

**Output**:
```
Feature Development Workflow: ICOMPLY-1
Status: IN_PROGRESS
Current Gate: MAKER
Agent: Backend Engineer
  - Progress: TDD cycle, writing tests
  - ETA: 2h
  - Branch: icomply-1-tenant-isolation

Next: Checker gate (automated quality)
```

## Agents Assigned by Ticket Type

| Ticket Type | Maker Agent | Reviewer | Approver |
|-------------|------------|----------|----------|
| Tenant Isolation | Backend Eng + Tenancy-Architect | Reviewer + Tenancy-Architect | CTO |
| Multi-DB Routing | Data Eng + Sharding-Strategy | Reviewer + Architect | CTO |
| Encryption | Backend Eng + Encryption-Specialist | Security Reviewer | CTO |
| Compliance | QA Eng + Compliance-Test-Engineer | Reviewer | Approver |
| Multi-Geography | DevOps + Geo-Failover-Architect | SRE Reviewer | CTO |
| Backup/DR | DevOps + DR-Orchestrator | SRE Reviewer | CTO |
| Networking | DevOps + Network-Security-Architect | Security Reviewer | CTO |

## Output

On completion, agents produce:

- ✅ Git commits (with ticket references)
- ✅ PR on GitHub (with description + test evidence)
- ✅ Test file (pytest, ≥80% coverage)
- ✅ Implementation file(s) (code for feature)
- ✅ Merged to main branch
- ✅ JIRA ticket closed (status: Done)

## Troubleshooting

### Checker Gate Failed

Check PR comments for specific failure:

```
✗ coverage: 73% (require ≥80%)
✗ lint: 2 errors found
```

Maker automatically gets looped back to fix issues.

### Reviewer Requested Changes

Check PR review comments. Maker will update code and resubmit.

### Approver Rejected

Check Approver comments. Usually governance or business requirement issue.
Contact Approver for more details.

## Configuration

Agents configured per product in `CLAUDE.md`:

```yaml
agents:
  enabled: true
  mcra_workflow: true
  maker_agents:
    - backend-engineer
    - frontend-engineer
    - tenancy-architect      # From enterprise framework
    - sharding-strategy
    - encryption-specialist

jira_integration:
  enabled: true
  project_key: ICOMPLY

github_integration:
  enabled: true
  org: dandawatey
  repo: i-comply
```

## See Also

- `/bootstrap-product` — Bootstrap new product with enterprise agents
- `/agent-status` — Check agent workflow progress
- `/mcra-status` — See MCRA workflow status across all tickets
