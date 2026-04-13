# Master Workflow — Complete Phase Sequence

## Architecture
```
React (Control Tower) → FastAPI (Business Truth) → Postgres (State) → Temporal (Execution) → Agents (Work)
```

## Rule
ALL work executes as Temporal workflows. No direct implementation. Feature = workflow.

## Complete Phase Sequence

### Phase 0: Factory Setup (once)
```
/factory-init → validate factory repo
```

### Phase 1: Product Creation
```
/bootstrap-product → create product repo → configure integrations
  └── detect: has PRD?
       ├── YES → proceed to Phase 2b
       └── NO  → Phase 2a
```

### Phase 2a: Vision → PRD (if no PRD)
```
/vision-to-prd
  ├── intake vision (any format)
  ├── ask 5-7 questions (max 3 follow-ups)
  ├── generate PRD + BMAD
  └── user approves
Temporal: VisionToPRDWorkflow
```

### Phase 2b: Business Discovery (before build)
```
/business-docs --phase discovery
  ├── TAM-SAM-SOM analysis
  ├── competitive analysis
  ├── team composition
  └── business model canvas
Temporal: BusinessDocsWorkflow (phase=discovery)
```

### Phase 3: Specification
```
/spec
  ├── extract features from PRD
  ├── create epics + stories
  ├── define acceptance criteria
  ├── prioritize backlog
  └── approve spec package
Temporal: FeatureDevelopmentWorkflow (intake + specification stages)
```

### Phase 4: Architecture
```
/arch
  ├── system design + module boundaries
  ├── API contracts + DB schema
  ├── tech stack selection
  └── approve architecture
Temporal: FeatureDevelopmentWorkflow (design + architecture stages)
```

### Phase 5: Feature Development (per feature, repeat)
```
/implement
  ├── select feature from backlog
  └── start feature_development_workflow
      ├── 1. intake
      ├── 2. specification
      ├── 3. design
      ├── 4. architecture
      ├── 5. implementation (TDD)
      ├── 6. testing
      ├── 7. review (MakerCheckerReviewerWorkflow)
      ├── 8. approval (human signal)
      ├── 9. release readiness
      └── 10. completion
Temporal: FeatureDevelopmentWorkflow
```

### Phase 6: Quality & Release
```
/check   → QAValidationWorkflow
/review  → code review
/approve → final authorization
/release → DeploymentReadinessWorkflow + ReleaseGovernanceWorkflow
```

### Phase 7: Business Planning (after build)
```
/business-docs --phase planning
  ├── financial projections
  ├── build & run costing
  ├── GTM strategy
  ├── pitch deck
  └── investor data room
Temporal: BusinessDocsWorkflow (phase=planning)
```

### Phase 8: Operations
```
/monitor  → health, errors, performance
/optimize → improvements → new feature workflows
```

## Interaction Modes

Every phase supports four interaction modes: `chat`, `brainstorm`, `plan`, `implement`. Mode is set per workflow step and switchable via React UI or Temporal signal. Agents adapt behavior to the active mode (e.g., brainstorm explores alternatives, implement produces artifacts).

## Brain as Data Layer

All phases read from and write to the Brain (`/api/v1/brain/`). Before entering any phase, the orchestrating agent queries Brain for relevant memories, decisions, and patterns. After completing a phase, results and learnings are written back. Brain (Postgres-backed) is the persistent cross-session, cross-product memory layer.

## Workflow Registry

| Workflow | Class | When |
|----------|-------|------|
| Vision → PRD | VisionToPRDWorkflow | No PRD, have vision |
| Business Docs | BusinessDocsWorkflow | Discovery or planning phase |
| Feature Development | FeatureDevelopmentWorkflow | Per feature |
| Bug Fix | BugFixWorkflow | Bug found |
| QA Validation | QAValidationWorkflow | Quality gate |
| Deployment Readiness | DeploymentReadinessWorkflow | Pre-deploy |
| Release Governance | ReleaseGovernanceWorkflow | Release |
| Maker-Checker-Reviewer | MakerCheckerReviewerWorkflow | Any approval (child) |

## Command Registry

| # | Command | Phase | Scope |
|---|---------|-------|-------|
| 1 | /factory-init | 0 | Factory |
| 2 | /bootstrap-product | 1 | Factory |
| 3 | /vision-to-prd | 2a | Product |
| 4 | /business-docs | 2b/7 | Product |
| 5 | /setup | 1 | Product |
| 6 | /spec | 3 | Product |
| 7 | /arch | 4 | Product |
| 8 | /implement | 5 | Product |
| 9 | /check | 6 | Product |
| 10 | /review | 6 | Product |
| 11 | /approve | 6 | Product |
| 12 | /release | 6 | Product |
| 13 | /monitor | 8 | Product |
| 14 | /optimize | 8 | Product |
| 15 | /resume | Any | Recovery |
| 16 | /factory-audit | Any | Factory |
| 17 | /factory-upgrade | Any | Factory |
