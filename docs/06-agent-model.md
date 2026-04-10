# Agent Model

## Overview

ProjectZeroFactory uses specialized agents that collaborate through a governed workflow. Each agent has a defined mission, scope, and handoff protocol. No agent operates in isolation — all work flows through the maker-checker-reviewer-approver chain.

## Agent Registry

### Product Manager
- **Purpose**: Translates business requirements (BMAD/PRD) into actionable specifications
- **Scope**: Requirements intake, specification writing, backlog prioritization, acceptance criteria
- **Inputs**: Raw BMAD document, PRD, stakeholder requirements
- **Outputs**: Structured specifications, prioritized stories with acceptance criteria
- **Handoff**: Sends approved specifications → Architect

### Architect
- **Purpose**: Designs system architecture, defines module boundaries, creates technical contracts
- **Scope**: System design, module decomposition, tech stack selection, API contracts, DB schemas
- **Inputs**: Approved specifications from Product Manager
- **Outputs**: Architecture document, module definitions, api-contract.yaml, db-schema.sql, frontend-types.ts
- **Handoff**: Sends approved architecture → Engineers (via Ralph Controller)

### Backend Engineer
- **Purpose**: Implements server-side code following TDD
- **Scope**: APIs, business logic, database operations, background jobs
- **Inputs**: Architecture docs, assigned tickets with acceptance criteria
- **Outputs**: Working code with passing tests, API documentation
- **Handoff**: Sends completed work → Checker

### Frontend Engineer
- **Purpose**: Implements UI using the design system
- **Scope**: Components, pages, state management, Storybook stories
- **Inputs**: Architecture docs, design specs, assigned tickets
- **Outputs**: Working UI with tests and Storybook stories
- **Handoff**: Sends completed work → Checker

### Data Engineer
- **Purpose**: Implements data pipelines and analytics infrastructure
- **Scope**: ETL pipelines, data models, analytics, data quality
- **Inputs**: Data requirements, architecture docs
- **Outputs**: Pipeline code, schemas, data quality tests
- **Handoff**: Sends completed work → Checker

### DevOps Engineer
- **Purpose**: Configures infrastructure, CI/CD, and deployment
- **Scope**: CI/CD pipelines, IaC, environments, monitoring setup
- **Inputs**: Architecture docs, deployment requirements
- **Outputs**: Pipeline configs, infrastructure code, deployment scripts
- **Handoff**: Sends completed work → Checker

### QA Engineer
- **Purpose**: Validates quality through comprehensive testing
- **Scope**: Test plans, integration tests, e2e tests, quality reports
- **Inputs**: Specifications, acceptance criteria, implemented code
- **Outputs**: Test suites, quality reports, bug reports
- **Handoff**: Sends quality report → Reviewer

### Security Reviewer
- **Purpose**: Reviews code and architecture for security vulnerabilities
- **Scope**: OWASP Top 10, dependency audit, auth/authz review, secret scanning
- **Inputs**: Code changes, architecture docs
- **Outputs**: Security findings, remediation recommendations
- **Authority**: Can BLOCK approval if critical security issues found

### UX Reviewer
- **Purpose**: Reviews UI for usability, accessibility, and design compliance
- **Scope**: Usability review, WCAG 2.1 AA compliance, design system adherence
- **Inputs**: UI components, Storybook stories, user flows
- **Outputs**: UX findings, accessibility report
- **Authority**: Can BLOCK approval if accessibility violations found

### SRE Engineer
- **Purpose**: Ensures system reliability and operational readiness
- **Scope**: Monitoring, alerting, SLO definition, runbooks, capacity planning
- **Inputs**: Architecture docs, deployment configs
- **Outputs**: Monitoring setup, alerting rules, runbooks, SLO definitions

### FinOps Analyst
- **Purpose**: Tracks and optimizes cloud costs
- **Scope**: Cost tracking, budget alerts, rightsizing, optimization
- **Inputs**: Infrastructure configs, usage data
- **Outputs**: Cost reports, optimization recommendations

### Checker (First Gate)
- **Purpose**: First validation gate — verifies basic quality
- **Scope**: Compilation, test execution, linting, security scanning, ticket compliance
- **Inputs**: Completed work from any engineer
- **Outputs**: Pass/fail report with specific findings
- **Handoff**: If pass → Reviewer. If fail → back to Maker with findings

### Reviewer (Second Gate)
- **Purpose**: Deep quality review
- **Scope**: Code quality, architecture alignment, test coverage, documentation
- **Inputs**: Checked work (passed Checker)
- **Outputs**: Review comments, approval or rejection
- **Handoff**: If pass → Approver. If fail → back to Maker with specific feedback

### Approver (Final Gate)
- **Purpose**: Final authorization before merge/deploy
- **Scope**: Business requirements validation, governance compliance, merge authorization
- **Inputs**: Reviewed work (passed Reviewer)
- **Outputs**: Approval or rejection, merge authorization
- **Handoff**: If approved → Release Manager or merge

### Release Manager
- **Purpose**: Orchestrates the release process
- **Scope**: Release branching, changelog, final validation, deployment, rollback
- **Inputs**: Approved work ready for release
- **Outputs**: Release notes, deployment execution, rollback plan

### Ralph Controller (Orchestrator)
- **Purpose**: Master orchestrator — routes work, tracks progress, manages flow
- **Scope**: Queue management, agent assignment, progress tracking, block detection, recovery triggering
- **Inputs**: Commands from user, state from all agents, queue state
- **Outputs**: Agent assignments, status reports, escalations
- **States**: IDLE → PLANNING → ASSIGNING → MONITORING → RECOVERING → REPORTING → IDLE
- **Rule**: Ralph NEVER does implementation work — only orchestrates

### Integration Agent
- **Purpose**: Manages external system synchronization
- **Scope**: JIRA ticket sync, Confluence page updates, GitHub PR management
- **Inputs**: Work items from other agents
- **Outputs**: Synced external state, conflict reports

### Plugin Validator
- **Purpose**: Validates required plugins and skills are available
- **Inputs**: Factory requirements from settings.json
- **Outputs**: Validation report listing available/missing plugins

### Repo Validator
- **Purpose**: Validates repository structure matches factory template
- **Inputs**: Repository path
- **Outputs**: Structural validation report with missing items

### Readiness Validator
- **Purpose**: Validates readiness to enter next stage
- **Inputs**: Current state, target stage requirements
- **Outputs**: Readiness report with pass/fail and blockers list

### Pipeline Agent
- **Purpose**: Manages async pipeline execution
- **Inputs**: Pipeline definitions, trigger events
- **Outputs**: Execution status, pipeline results

### Memory Agent
- **Purpose**: Manages factory memory lifecycle
- **Scope**: Context loading before actions, learning capture after actions, pattern promotion
- **Inputs**: Action context from any agent
- **Outputs**: Relevant memories loaded, new learnings stored
- **Rule**: All memory writes are structured and tagged

## Agent Communication Protocol

1. Agents receive work from the queue (.claude/delivery/queue/)
2. Agents report status updates to Ralph Controller
3. Agents hand off via queue state transitions (active → completed/failed)
4. Agents escalate blocks to Ralph Controller
5. All agent actions are logged in .claude/reports/audit-log.md

## Agent Learning Contract

Every agent MUST:
- Read relevant memory from .claude/memory/ before starting work
- Write structured learnings to .claude/learning/ after completing work
- Never self-mutate (change own definition) without approval
- Promote learnings only through the memory-agent approval process
