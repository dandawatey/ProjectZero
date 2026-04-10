# 08 - JIRA, Confluence, and GitHub Integration Model

## Overview

The factory integrates with three external tools: JIRA (work tracking), Confluence (documentation), and GitHub (source control). All integrations are optional -- the factory operates in local-first mode and syncs to external systems when available. The integration-agent manages all synchronization.

## JIRA Integration

### Project Structure

The factory uses a standard JIRA hierarchy:

```
Project (e.g., MYP - MyProduct)
  |
  +-- Epic (MYP-10: User Management Module)
  |     |
  |     +-- Story (MYP-11: User Registration)
  |     |     +-- Subtask (MYP-12: Implement registration API)
  |     |     +-- Subtask (MYP-13: Implement registration UI)
  |     |     +-- Subtask (MYP-14: Write registration tests)
  |     |
  |     +-- Story (MYP-15: User Authentication)
  |           +-- Subtask (MYP-16: Implement login API)
  |           +-- Subtask (MYP-17: Implement login UI)
  |
  +-- Epic (MYP-20: Billing Module)
        |
        +-- Story (MYP-21: Subscription Management)
        +-- Story (MYP-22: Payment Processing)
```

### Issue Types

| Type | Mapped From | Created During | Fields |
|---|---|---|---|
| Epic | Module specification | `/spec` stage | Summary, Description, Module, Priority |
| Story | User story with acceptance criteria | `/spec` stage | Summary, Description, Acceptance Criteria, Story Points, Epic Link |
| Task | Implementation work item | `/implement` stage | Summary, Description, Story Link, Assignee (agent) |
| Subtask | Granular work within a task | `/implement` stage | Summary, Description, Task Link |
| Bug | Defect found during testing | `/check` or `/review` stage | Summary, Description, Steps to Reproduce, Severity, Story Link |

### Workflow States

```
Backlog --> To Do --> In Progress --> In Review --> Done
                        |               |
                        |               +-- Blocked
                        +-- Needs Info
```

State transitions are managed by the factory:
- **Backlog -> To Do**: When the story is planned for the current sprint
- **To Do -> In Progress**: When `/implement` starts work on the ticket
- **In Progress -> In Review**: When the maker hands to checker
- **In Review -> Done**: When the approver approves
- **In Review -> In Progress**: When checker/reviewer sends back to maker
- **Any -> Blocked**: When a dependency is unmet or an integration fails
- **Any -> Needs Info**: When the product-manager flags ambiguity

### JIRA Sync Mechanism

The integration-agent synchronizes between local state and JIRA:

```
Local State                          JIRA
.claude/delivery/jira/issues/    <-->  JIRA REST API
.claude/delivery/jira/state/     <-->  Board state
.claude/delivery/jira/sync_queue/ -->  Pending updates
.claude/delivery/jira/logs/      <--  Sync audit trail
.claude/delivery/jira/mappings/  <-->  Local ID <-> JIRA ID
```

**Local issue format** (`.claude/delivery/jira/issues/{ticket-id}.json`):
```json
{
  "local_id": "MYP-11",
  "jira_id": "10042",
  "type": "story",
  "summary": "As a user, I can register an account",
  "description": "...",
  "status": "in-progress",
  "epic_link": "MYP-10",
  "acceptance_criteria": [
    "Given a valid email and password, when I submit the registration form, then my account is created",
    "Given an email that already exists, when I submit the registration form, then I see an error message"
  ],
  "story_points": 5,
  "sprint": "Sprint 1",
  "assignee": "backend-engineer",
  "created_at": "2026-01-20T10:00:00Z",
  "updated_at": "2026-01-22T14:30:00Z",
  "sync_status": "synced",
  "last_synced_at": "2026-01-22T14:30:00Z"
}
```

### Sync Queue

When the factory modifies a ticket locally, it queues a sync operation:

```json
{
  "operation": "update",
  "ticket_id": "MYP-11",
  "fields": {
    "status": "in-review"
  },
  "queued_at": "2026-01-22T14:30:00Z",
  "retries": 0
}
```

The integration-agent processes the sync queue on a best-effort basis. If JIRA is unavailable, operations remain queued until connectivity is restored.

### Sprint Management

The factory tracks sprints locally:
- Sprint planning: `/story-create` assigns stories to sprints
- Sprint progress: Updated as stories move through states
- Sprint reports: Generated at sprint end in `.claude/reports/`

---

## Confluence Integration

### Project Hub Structure

When `/setup confluence` runs, it creates the following page hierarchy in Confluence:

```
Product Hub (parent page)
  |
  +-- Overview
  |     Product description, team, links, status
  |
  +-- Architecture
  |     +-- Architecture Overview
  |     +-- ADR-001: {decision}
  |     +-- ADR-002: {decision}
  |     +-- ...
  |
  +-- Modules
  |     +-- User Management
  |     |     +-- Specification
  |     |     +-- Data Model
  |     |     +-- API Contract
  |     |     +-- Architecture
  |     +-- Billing
  |     |     +-- Specification
  |     |     +-- ...
  |
  +-- Sprints
  |     +-- Sprint 1 Report
  |     +-- Sprint 2 Report
  |
  +-- Risks
  |     Risk register with status and mitigations
  |
  +-- Decisions
  |     Decision log (non-architectural decisions)
  |
  +-- Releases
        +-- v1.0.0 Release Notes
        +-- v1.1.0 Release Notes
```

### Page Sync Mechanism

```
Local State                              Confluence
.claude/delivery/confluence/pages/   <-->  Confluence REST API
.claude/delivery/confluence/mappings/<-->  Local page <-> Confluence page ID
.claude/delivery/confluence/sync_queue/ -> Pending updates
.claude/delivery/confluence/logs/    <--  Sync audit trail
.claude/delivery/confluence/payloads/<-->  API request/response payloads
```

**Local page format** (`.claude/delivery/confluence/pages/{page-slug}.md`):
The page content is stored as Markdown locally. When syncing to Confluence, the integration-agent converts Markdown to Confluence Storage Format (XHTML).

### Automatic Page Updates

The factory automatically updates Confluence pages when:
- A specification is completed or updated (module spec pages)
- An ADR is created (architecture section)
- A sprint is completed (sprint report)
- A risk is identified or mitigated (risk register)
- A release is deployed (release notes)

---

## GitHub Integration

### Branch Naming Convention

All branches follow the pattern:
```
{type}/{ticket-id}-{short-description}
```

Types:
- `feature/` -- New feature implementation
- `bugfix/` -- Bug fix
- `hotfix/` -- Production hotfix
- `refactor/` -- Code refactoring
- `test/` -- Test additions or modifications
- `docs/` -- Documentation changes

Examples:
```
feature/MYP-11-user-registration
bugfix/MYP-45-login-timeout
hotfix/MYP-67-payment-crash
```

### Branch-per-Ticket Rule

Every JIRA ticket that involves code changes gets its own branch. This ensures:
- Clean separation of changes
- Easy code review per feature
- Traceable history from ticket to code

### Pull Request Structure

PRs are created by the release-manager agent with:

```markdown
## {ticket-id}: {summary}

### Description
{Story description and implementation approach}

### Changes
- {file1}: {what changed and why}
- {file2}: {what changed and why}

### Acceptance Criteria
- [x] {criterion 1}
- [x] {criterion 2}

### Test Evidence
- Unit tests: {count} passing
- Integration tests: {count} passing
- E2E tests: {count} passing
- Coverage: {percentage}%

### Governance Chain
- Checker: PASS ({timestamp})
- Reviewer: APPROVED ({timestamp})
- Security: CLEAR ({timestamp})
- Approver: APPROVED ({timestamp})

### JIRA: [{ticket-id}]({jira-url})
```

### PR-per-Story Rule

One PR per story. If a story has multiple tasks/subtasks, they are all included in a single PR for the story. This makes review manageable and maintains a clear mapping:
- 1 Story = 1 Branch = 1 PR

### GitHub Sync Mechanism

```
Local State                          GitHub
.claude/delivery/github/branches/<-->  Git branches
.claude/delivery/github/state/   <-->  PR state, review state
.claude/delivery/github/logs/    <--  Sync audit trail
.claude/delivery/github/repos/   <-->  Repository configuration
```

### CI/CD Integration

The factory expects a CI/CD pipeline (GitHub Actions or equivalent) that:
1. Runs on every PR
2. Executes the test suite
3. Reports results back as PR checks
4. Blocks merge if tests fail

The factory configures the pipeline during `/setup github`.

---

## Local-First Fallback

When integrations are unavailable (`ENABLE_LOCAL_FALLBACK=true`), the factory uses local file representations:

### JIRA Fallback
- Tickets are JSON files in `.claude/delivery/jira/issues/`
- Status tracking in `.claude/delivery/jira/state/board-state.json`
- Sprint tracking in `.claude/delivery/jira/state/current-sprint.json`
- The factory operates exactly the same -- agents reference tickets by ID regardless of where they are stored

### Confluence Fallback
- Pages are Markdown files in `.claude/delivery/confluence/pages/`
- Page hierarchy tracked in `.claude/delivery/confluence/mappings/hierarchy.json`
- The factory reads and writes pages locally

### GitHub Fallback
- Git operations happen on the local repository
- PRs are represented as JSON files in `.claude/delivery/github/state/`
- Merge operations happen locally
- When GitHub becomes available, the integration-agent pushes and creates real PRs

### Reconciliation

When integrations become available after a period of local-only operation, the reconciliation system:

1. Compares local state to remote state
2. Identifies drift (tickets updated in JIRA but not locally, or vice versa)
3. Applies a last-writer-wins strategy with manual override for conflicts
4. Logs all reconciliation actions in `.claude/delivery/reconciliation/`
5. Reports any conflicts that require human resolution

The reconciliation process runs automatically when `/setup {integration}` succeeds after a period of fallback.

---

## Integration Configuration Reference

### Required Environment Variables

```env
# JIRA
JIRA_BASE_URL=https://your-org.atlassian.net
JIRA_API_TOKEN=your-token
JIRA_USER_EMAIL=your-email
JIRA_PROJECT_KEY=MYP
JIRA_BOARD_ID=123

# Confluence
CONFLUENCE_BASE_URL=https://your-org.atlassian.net/wiki
CONFLUENCE_API_TOKEN=your-token
CONFLUENCE_SPACE_KEY=MYP

# GitHub
GITHUB_TOKEN=your-token
GITHUB_ORG=your-org
GITHUB_DEFAULT_BRANCH=main
```

### Testing Integration Connectivity

```
/setup jira          # Tests JIRA connection and syncs board state
/setup confluence    # Tests Confluence connection and creates hub
/setup github        # Tests GitHub connection and configures repo
/setup validate      # Runs all integration tests
```

Each setup command reports success or failure with specific error details. Common failures:
- **401 Unauthorized**: Token is invalid or expired
- **403 Forbidden**: Token does not have required permissions
- **404 Not Found**: Project key or space key does not exist
- **Connection timeout**: Network issue, check VPN or firewall
