# 14 - Command Reference

## Overview

Commands are the user interface to the factory. They are invoked with a slash prefix in Claude Code. Each command is defined in `.claude/commands/` and orchestrates one or more workflows.

---

## Factory Setup Commands

### /factory-init

**Purpose**: Initialize the factory in a freshly cloned repository. Validates the `.claude/` structure, creates empty stores, and prepares the factory for product bootstrapping.

**Inputs**: None (operates on the current directory).

**Outputs**:
- Validated `.claude/` directory structure
- Initialized memory, recovery, and learning stores
- Factory version recorded in `.claude/core/`

**When to use**: Immediately after cloning the ProjectZeroFactory template, before anything else.

**Prerequisite**: The current directory must contain a `.claude/` directory from the factory template.

---

### /bootstrap-product

**Purpose**: Configure the factory for a specific product. Sets the product name, type, technology stack, and creates the initial project structure.

**Inputs**:
- `--name` (required): Product name
- `--type` (required): Product type (`saas`, `internal-tool`, `platform`, `mobile`, `api`)
- `--stack` (required): Comma-separated technology stack (e.g., `nextjs,fastapi,postgresql`)

**Outputs**:
- Product-specific directory structure in the source tree
- `package.json` and/or `pyproject.toml` initialized
- `.claude/modules/` prepared for module definitions
- `.claude/design-system/` initialized (if frontend stack)
- Initial git commit

**When to use**: After `/factory-init`, before configuring integrations.

---

### /setup

**Purpose**: Configure and validate integrations and factory components.

**Subcommands**:
- `/setup jira` -- Configure and test JIRA integration
- `/setup confluence` -- Configure and test Confluence integration, create project hub
- `/setup github` -- Configure and test GitHub integration
- `/setup validate` -- Run the readiness-validator agent across all factory components

**Inputs**: Reads configuration from `.env`.

**Outputs**:
- Integration connection test results
- Confluence project hub created (for `/setup confluence`)
- Readiness report (for `/setup validate`)

**When to use**: After `/bootstrap-product`, when configuring external integrations. Can be run at any time to re-validate.

---

## SPARC Workflow Commands

### /spec

**Purpose**: Run the Specification stage. Produces module definitions, epics, user stories, and API contracts from the BMAD/PRD.

**Inputs**:
- `--type bmad` -- Create or load a BMAD document
- `--type prd` -- Load a PRD document
- `--input {path}` -- Path to an existing document to load
- (No arguments) -- Run the full specification workflow

**Outputs**:
- Module specifications in `.claude/modules/{name}/spec.md`
- Epic definitions in `.claude/delivery/epics/`
- Story definitions in `.claude/delivery/features/`
- API contracts in `.claude/contracts/`
- JIRA epics and stories (or local equivalents)
- Confluence specification pages

**When to use**: At the start of a new product (after setup) or when adding a major new feature area.

---

### /arch

**Purpose**: Run the Architecture stage. Produces architecture decisions, data models, infrastructure requirements, and security architecture.

**Inputs**:
- `--stage design` -- Run only the Design sub-stage (pseudocode, data models, UI flows)
- (No arguments) -- Run the full Architecture stage (design + architecture decisions + infrastructure)

**Outputs**:
- Data models in `.claude/modules/{name}/data-model.md`
- Pseudocode in `.claude/modules/{name}/pseudocode.md`
- UI flows in `.claude/modules/{name}/ui-flows.md`
- ADRs in `.claude/knowledge/adrs/`
- Architecture documents in `.claude/modules/{name}/architecture.md`
- Infrastructure requirements in `.claude/devops/`

**When to use**: After the specification is approved.

---

### /implement

**Purpose**: Implement a specific ticket (story or task). Creates a branch, writes tests (TDD), implements code, and passes through the governance chain.

**Inputs**:
- `{ticket-id}` (required): The JIRA ticket ID to implement (e.g., `MYP-13`)
- `--mode prototype` -- Skip governance chain (code cannot be promoted without full review)
- `--mode hotfix` -- Reduced governance for urgent fixes

**Outputs**:
- Feature branch created
- Test files written
- Implementation code written
- Governance chain results (checker, reviewer, approver)
- Recovery checkpoint saved

**When to use**: During the Realization stage, for each story or task.

---

### /check

**Purpose**: Run the checker agent on a specific artifact or the current working state.

**Inputs**:
- `{ticket-id}` -- Check a specific ticket's artifacts
- (No arguments) -- Check whatever is currently in progress

**Outputs**:
- Check result: PASS or FAIL with specific findings

**When to use**: Manually trigger a check. Usually invoked automatically by `/implement`.

---

### /review

**Purpose**: Run the reviewer agent on a specific artifact.

**Inputs**:
- `{ticket-id}` -- Review a specific ticket's artifacts
- `--security` -- Include security review
- `--ux` -- Include UX review (for UI artifacts)

**Outputs**:
- Review result: APPROVE, REQUEST_CHANGES, or BLOCK
- Review comments with line references

**When to use**: Manually trigger a review. Usually invoked automatically by `/implement` after checker passes.

---

### /approve

**Purpose**: Run the approver agent for final sign-off.

**Inputs**:
- `{ticket-id}` -- Approve a specific ticket
- `--module {name}` -- Approve an entire module (runs module gate checklist)

**Outputs**:
- Approval result: APPROVED or REJECTED
- Module gate checklist results (for `--module`)

**When to use**: After review passes (for tickets) or when all stories in a module are complete (for modules).

---

### /release

**Purpose**: Orchestrate a release from approved code to production deployment.

**Inputs**:
- `--version {semver}` -- Release version (e.g., `1.0.0`)
- `--rollback {version}` -- Roll back to a previous version

**Outputs**:
- Release branch and tag
- Release notes
- Deployment to staging and production
- Monitoring activation

**When to use**: When all modules are approved and ready for deployment.

---

### /monitor

**Purpose**: Check the health and status of the deployed product and factory systems.

**Inputs**:
- `--pipeline` -- Show pipeline mode status (workers, queues, running pipelines)
- `--health` -- Show service health metrics
- (No arguments) -- Show overall status

**Outputs**:
- Health status report
- Active alerts
- Resource utilization
- Pipeline status (if applicable)

**When to use**: After deployment and during ongoing operations.

---

### /optimize

**Purpose**: Run optimization analysis on infrastructure costs and performance.

**Inputs**:
- `--cost` -- FinOps analysis (cost optimization recommendations)
- `--performance` -- Performance optimization recommendations
- (No arguments) -- Run both

**Outputs**:
- Cost report with optimization recommendations
- Performance report with bottleneck identification

**When to use**: Post-launch or on a regular cadence.

---

## Pipeline Commands

### /pipeline-create

**Purpose**: Create a Dagster pipeline for parallel implementation of multiple tickets.

**Inputs**:
- `--type {type}` -- Pipeline type (`implementation`, `testing`, `deployment`)
- `--tickets {ids}` -- Comma-separated ticket IDs

**Outputs**:
- Pipeline registered with Dagster
- Dependency graph computed
- Pipeline ready for execution

**When to use**: During realization when multiple independent stories can be worked in parallel.

---

## Recovery Commands

### /resume

**Purpose**: Resume work from the last checkpoint after a session interruption.

**Inputs**: None.

**Outputs**: Status report of current state and continuation of in-progress work.

**When to use**: At the start of any new session when work was previously in progress.

---

### /recover-ticket

**Purpose**: Get the full recovery state of a specific ticket.

**Inputs**: `{ticket-id}` -- The ticket to recover.

**Outputs**: Comprehensive status report including progress, governance state, retry state, and recommended next action.

**When to use**: When a specific ticket appears stuck or you need to understand its state.

---

### /recover-workflow

**Purpose**: Get the full recovery state of the entire workflow.

**Inputs**: None.

**Outputs**: Comprehensive status report covering all modules, stories, active work, blocked items, and integration status.

**When to use**: When starting a fresh session and wanting a complete picture.

---

## Design System Commands

### /design-system-init

**Purpose**: Initialize the design system for a product with a frontend stack.

**Inputs**:
- `--regenerate-tokens` -- Regenerate TypeScript token files from JSON definitions

**Outputs**:
- `.claude/design-system/` populated with default tokens and guidelines
- `packages/ui/` scaffolded with Storybook, base components, and token files

**When to use**: During `/bootstrap-product` (automatic for frontend stacks) or when resetting the design system.

---

### /component-create

**Purpose**: Create a new shared UI component with proper governance.

**Inputs**:
- `--name {ComponentName}` (required): Component name in PascalCase
- `--module {module}` -- The module requesting the component

**Outputs**:
- Component directory in `packages/ui/src/components/`
- Component file, Storybook stories, tests, CSS module
- Registration in component registry

**When to use**: When a new shared component is needed that does not exist in the design system.

---

### /component-review

**Purpose**: Run a comprehensive review of a UI component.

**Inputs**:
- `--name {ComponentName}` (required): Component to review

**Outputs**:
- Code quality review results
- Visual design review results
- Accessibility audit results
- Design system compliance check

**When to use**: After implementing a new component, before marking it as stable.

---

### /ui-audit

**Purpose**: Run a comprehensive UI audit across all components and pages.

**Inputs**:
- `--module {module}` -- Audit a specific module's UI
- (No arguments) -- Audit all UI

**Outputs**:
- Accessibility report (WCAG 2.1 AA compliance)
- Design system compliance report
- Visual consistency report
- Improvement recommendations

**When to use**: Before releases or on a regular cadence.

---

## Story Commands

### /story-create

**Purpose**: Create a new user story with acceptance criteria and add it to the backlog.

**Inputs**:
- `--epic {epic-id}` -- Parent epic
- `--module {module}` -- Target module
- `--title {title}` -- Story summary
- (Interactive) -- If no arguments, enters an interactive story creation flow

**Outputs**:
- Story definition in `.claude/delivery/features/`
- JIRA story created (or local equivalent)
- Story added to the sprint backlog

**When to use**: When adding new stories beyond the initial specification, or during sprint planning.

---

### /story-validate

**Purpose**: Validate that a story is complete, well-formed, and ready for implementation.

**Inputs**:
- `{story-id}` -- The story to validate

**Outputs**:
- Validation result with specific issues (if any)
- Checks: acceptance criteria present, module assigned, epic linked, no ambiguity

**When to use**: Before starting implementation, to ensure the story is implementation-ready.

---

## Command Quick Reference

| Command | Stage | Primary Agent |
|---|---|---|
| `/factory-init` | Setup | repo-validator |
| `/bootstrap-product` | Setup | ralph-controller |
| `/setup` | Setup | integration-agent, readiness-validator |
| `/spec` | Specification | product-manager |
| `/arch` | Design/Architecture | architect |
| `/implement` | Realization | engineering agents |
| `/check` | Realization | checker |
| `/review` | Realization | reviewer |
| `/approve` | Realization/Completion | approver |
| `/release` | Completion | release-manager |
| `/monitor` | Operations | sre-engineer |
| `/optimize` | Operations | finops-analyst |
| `/pipeline-create` | Realization | pipeline-agent |
| `/resume` | Recovery | ralph-controller |
| `/recover-ticket` | Recovery | ralph-controller |
| `/recover-workflow` | Recovery | ralph-controller |
| `/design-system-init` | Setup | frontend-engineer |
| `/story-create` | Specification | product-manager |
| `/story-validate` | Specification | checker |
| `/component-create` | Realization | frontend-engineer |
| `/component-review` | Realization | ux-reviewer |
| `/ui-audit` | Realization/Completion | ux-reviewer |
