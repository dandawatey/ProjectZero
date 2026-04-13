# Command Reference

## Phase Sequence
```
/factory-init → /bootstrap-product → /vision-to-prd → /business-docs → /spec → /arch → /implement → /check → /review → /approve → /release → /business-docs → /monitor → /optimize
```

## Factory Commands (run in factory repo)

### /factory-init
- **Phase**: 0
- **Purpose**: Validate factory repo healthy
- **Inputs**: None
- **Outputs**: Validation report
- **Next**: /bootstrap-product

### /bootstrap-product
- **Phase**: 1
- **Purpose**: Create product repo, configure integrations, load BMAD/PRD
- **Inputs**: Product name, BMAD/PRD (or triggers /vision-to-prd if none)
- **Outputs**: Initialized product repo with .claude OS
- **Next**: /vision-to-prd (if no PRD) or /spec

### /factory-audit
- **Phase**: Any
- **Purpose**: Check factory for product-state leakage
- **Inputs**: None
- **Outputs**: Health report

### /factory-upgrade
- **Phase**: Any
- **Purpose**: Add new agents, skills, workflows, governance
- **Inputs**: Upgrade spec
- **Outputs**: Updated factory

## Product Commands (run in product repo)

### /vision-to-prd
- **Phase**: 2a
- **Purpose**: Generate PRD + BMAD from raw product vision
- **Inputs**: Vision text (any format)
- **Outputs**: Structured PRD, BMAD
- **Temporal**: VisionToPRDWorkflow
- **Next**: /business-docs --phase discovery

### /business-docs
- **Phase**: 2b (discovery) or 7 (planning)
- **Purpose**: Generate business document suite
- **Inputs**: `--phase discovery` or `--phase planning`
- **Outputs (discovery)**: TAM-SAM-SOM, competitive analysis, team composition, business model
- **Outputs (planning)**: Financial projections, costing, GTM, pitch deck, data room
- **Temporal**: BusinessDocsWorkflow
- **Next**: /spec (after discovery) or operations (after planning)

### /setup
- **Phase**: 1
- **Purpose**: Configure dev environment
- **Inputs**: None
- **Outputs**: Environment validation report

### /spec
- **Phase**: 3
- **Purpose**: Create specifications from PRD
- **Inputs**: PRD in memory
- **Outputs**: Approved specs, epics, stories with acceptance criteria
- **Temporal**: FeatureDevelopmentWorkflow (intake + spec stages)
- **Next**: /arch

### /arch
- **Phase**: 4
- **Purpose**: Design system architecture
- **Inputs**: Approved specifications
- **Outputs**: Architecture doc, API contracts, DB schema, tech stack
- **Temporal**: FeatureDevelopmentWorkflow (design + architecture stages)
- **Next**: /implement

### /implement
- **Phase**: 5
- **Purpose**: Start feature development workflow
- **Inputs**: Feature from backlog
- **Outputs**: Implemented feature (code + tests + artifacts)
- **Temporal**: FeatureDevelopmentWorkflow (all 10 stages)
- **Next**: /check

### /check
- **Phase**: 6
- **Purpose**: Run quality validation
- **Inputs**: Implemented code
- **Outputs**: QA report (tests, coverage, lint, security)
- **Temporal**: QAValidationWorkflow
- **Next**: /review

### /review
- **Phase**: 6
- **Purpose**: Deep code review
- **Inputs**: Checked code
- **Outputs**: Review report
- **Temporal**: MakerCheckerReviewerWorkflow
- **Next**: /approve

### /approve
- **Phase**: 6
- **Purpose**: Final authorization (human signal)
- **Inputs**: Reviewed work
- **Outputs**: Approval/rejection
- **Next**: /release

### /release
- **Phase**: 6
- **Purpose**: Deploy to production
- **Inputs**: Approved work
- **Outputs**: Deployed app, release notes, changelog
- **Temporal**: DeploymentReadinessWorkflow + ReleaseGovernanceWorkflow
- **Next**: /monitor

### /monitor
- **Phase**: 8
- **Purpose**: Post-release health check
- **Inputs**: Deployed app
- **Outputs**: Health report, alerts
- **Next**: /optimize (if issues)

### /optimize
- **Phase**: 8
- **Purpose**: Plan improvements
- **Inputs**: Monitoring data
- **Outputs**: Optimization tickets → new /implement cycles

## Recovery Commands

### /resume
- **Purpose**: Resume interrupted work from last Temporal checkpoint
- **When**: IDE crash, context overflow, network failure

### /recover-ticket
- **Purpose**: Recover specific failed ticket
- **When**: Ticket workflow failed

### /recover-workflow
- **Purpose**: Recover entire failed workflow
- **When**: Workflow-level failure

## UI/Design Commands

### /design-system-init
- **Purpose**: Initialize packages/ui with Storybook + design tokens

### /component-create
- **Purpose**: Create shared UI component with tests + stories

### /component-review
- **Purpose**: Review component for design system compliance

### /story-create
- **Purpose**: Create Storybook stories for component

### /story-validate
- **Purpose**: Validate all stories render + pass a11y

### /ui-audit
- **Purpose**: Audit entire UI for compliance

### /pipeline-create
- **Purpose**: Create async pipeline definition
