# 05 - Stage-by-Stage Workflow

## The 8-Phase Model

All phases are Temporal workflows. All transitions are Temporal signals. No phase can be skipped.

```
Phase 0 --> 1 --> 2a/2b --> 3 --> 4 --> 5 --> 6 --> 7 --> 8
```

---

## Phase 0: Factory Init

**Objective**: Validate all integrations. Initialize factory state. Confirm readiness.

**Command**: `/factory-init`

**Temporal Workflow**: `FactoryInitWorkflow`

**Agents**: Factory orchestrator

**What Happens**:
1. `ValidateGitHubActivity` -- token, org, perms
2. `ValidateJiraActivity` -- token, project perms
3. `ValidateConfluenceActivity` -- token, space perms
4. `ValidateTemporalActivity` -- server connection, namespace
5. `ValidatePostgresActivity` -- connection, schema, migrations
6. `ValidateRedisActivity` -- connection, read/write
7. `ValidateAnthropicActivity` -- API key, model access
8. `InitializeStoresActivity` -- create Postgres tables, Redis keys
9. `WriteFactoryStateActivity` -- record factory version, config

**Artifacts**: Factory state in Postgres. Integration validation records.

**Exit Criteria**: All 7 integrations validated. Stores initialized. Factory state = READY.

---

## Phase 1: Product Creation

**Objective**: Create a new product as a separate repo with all supporting infrastructure.

**Command**: `/bootstrap-product --name "X" --type saas --stack "nextjs,fastapi,postgresql"`

**Temporal Workflow**: `BootstrapProductWorkflow`

**Agents**: Factory orchestrator, integration agents

**What Happens**:
1. `CreateGitHubRepoActivity` -- new repo in org, initial structure
2. `CreateJiraProjectActivity` -- project with board, initial epics structure
3. `CreateConfluenceSpaceActivity` -- space with standard page hierarchy
4. `ScaffoldProductActivity` -- generate project scaffold based on type + stack
5. `InitProductStateActivity` -- create product record in Postgres
6. `CommitAndPushActivity` -- initial commit to product repo

**Artifacts**: GitHub repo. JIRA project. Confluence space. Product record in Postgres.

**Exit Criteria**: Repo exists and is accessible. JIRA project has board. Confluence space has page hierarchy. Product state = CREATED.

---

## Phase 2a: Vision-to-PRD

**Objective**: Transform a vision statement into a structured PRD and BMAD.

**Command**: `/vision-to-prd`

**Temporal Workflow**: `VisionToPrdWorkflow`

**Agents**: Product manager, cofounder, CXO

**What Happens**:
1. `AnalyzeVisionActivity` -- parse vision, identify market, users, value prop
2. `GenerateBmadActivity` -- business model, personas, metrics, risks, constraints
3. `GeneratePrdActivity` -- features, user stories, acceptance criteria, NFRs
4. `ValidateBmadActivity` -- completeness, consistency, measurability checks
5. `PublishToConfluenceActivity` -- BMAD + PRD pages
6. `CommitToProductRepoActivity` -- store in product repo

**Artifacts**: BMAD document. PRD document. Confluence pages.

**Exit Criteria**: BMAD passes validation. PRD has features with acceptance criteria. Both published.

---

## Phase 2b: Business Discovery

**Objective**: Generate business analysis artifacts from BMAD.

**Command**: `/business-docs --phase discovery`

**Temporal Workflow**: `BusinessDocsWorkflow` (mode=discovery)

**Agents**: Cofounder, product manager, FinOps analyst

**What Happens**:
1. `TamAnalysisActivity` -- TAM/SAM/SOM calculations
2. `CompetitiveAnalysisActivity` -- landscape mapping, differentiation
3. `TeamModelActivity` -- roles needed, hiring plan
4. `BusinessModelActivity` -- revenue model, pricing, unit economics
5. `RiskAssessmentActivity` -- market, technical, operational risks
6. `PublishToConfluenceActivity` -- all docs to Confluence

**Artifacts**: TAM analysis. Competitive landscape. Team model. Business model. Risk assessment.

**Exit Criteria**: All discovery documents generated and published.

---

## Phase 3: Specification

**Objective**: Decompose BMAD/PRD into implementable modules, epics, stories, contracts.

**Command**: `/spec`

**Temporal Workflow**: `SpecificationWorkflow`

**Agents**: Product manager, architect (advisory), checker, approver

**What Happens**:
1. `LoadContextActivity` -- read BMAD, PRD from product repo
2. `DecomposeModulesActivity` -- identify bounded contexts
3. `DefineContractsActivity` -- API contracts between modules
4. `CreateEpicsActivity` -- group stories into epics
5. `CreateStoriesActivity` -- user stories with Given/When/Then acceptance criteria
6. `IdentifyCrossCuttingActivity` -- auth, logging, monitoring, error handling
7. `CreateJiraTicketsActivity` -- epics + stories in JIRA
8. `PublishToConfluenceActivity` -- specification docs
9. `GovernanceChainWorkflow` -- checker validates, approver signs off

**Artifacts**: Module specs. API contracts. JIRA epics + stories. Confluence spec pages.

**Exit Criteria**: All modules defined. All stories have acceptance criteria. All contracts documented. Checker passed. Approver approved. JIRA synced.

---

## Phase 4: Architecture

**Objective**: Make all technical decisions. Document as ADRs. Define infrastructure and security.

**Command**: `/arch`

**Temporal Workflow**: `ArchitectureWorkflow`

**Agents**: Architect, security reviewer, SRE, DevOps, FinOps, checker, approver

**What Happens**:
1. `LoadSpecActivity` -- read module specs and contracts
2. `SelectPatternsActivity` -- API style, DB strategy, caching, auth approach
3. `CreateAdrsActivity` -- architecture decision records
4. `DefineInfraActivity` -- compute, storage, networking, CI/CD
5. `DefineSecurityActivity` -- auth mechanism, encryption, OWASP mitigation
6. `DefineObservabilityActivity` -- logging, metrics, tracing, dashboards, runbooks
7. `CostEstimateActivity` -- FinOps cost projections
8. `PublishToConfluenceActivity` -- architecture docs
9. `GovernanceChainWorkflow` -- checker validates, security reviewer checks, approver signs off

**Artifacts**: ADRs. Infrastructure spec. Security architecture. Observability plan. Cost estimate. Confluence pages.

**Exit Criteria**: All ADRs documented. Infra defined. Security reviewed. Observability defined. Checker passed. Approver approved.

---

## Phase 5: Implementation

**Objective**: Build the software. TDD. Governance chain per story.

**Command**: `/implement {TICKET-ID}`

**Temporal Workflow**: `ImplementationWorkflow` (one per story)

**Agents**: Backend engineer, frontend engineer, data engineer, QA, security reviewer, UX reviewer, checker, reviewer, approver, release manager

**What Happens (per story)**:
1. `CreateBranchActivity` -- `feature/{TICKET-ID}-{desc}`
2. `WriteTestsActivity` -- unit + integration + E2E tests (TDD: tests first)
3. `RunTestsActivity` -- confirm tests fail (red)
4. `ImplementActivity` -- write code following pseudocode, data models, ADRs
5. `RunTestsActivity` -- confirm tests pass (green)
6. `RefactorActivity` -- clean up, tests still green
7. `CoverageCheckActivity` -- validate >= 80%
8. `GovernanceChainWorkflow` (child workflow):
   - Checker: validates against spec + contract
   - Reviewer: code quality, security, performance
   - Approver: final sign-off
9. `CreatePrActivity` -- PR with ticket ref, description, test evidence
10. `UpdateJiraActivity` -- ticket status to Done

**Artifacts**: Source code. Tests. Git branch. PR. Updated JIRA ticket.

**Exit Criteria (per story)**: All acceptance criteria met. All tests pass. Coverage >= 80%. Governance chain complete. PR created. JIRA updated.

**Exit Criteria (per module)**: All stories done. Module integration tests pass. Module gate checklist complete. `/approve --module {name}` passed.

### The 10-Stage Feature Development Workflow (Detail)

For a single feature/story, the full workflow within Phase 5:

| Stage | Activity | Agent | Gate |
|---|---|---|---|
| 1 | Create branch | Release manager | Branch name matches `{type}/{ticket}-{desc}` |
| 2 | Write failing tests | QA + Engineering | Tests exist and fail |
| 3 | Implement code | Engineering | Tests pass |
| 4 | Refactor | Engineering | Tests still pass |
| 5 | Coverage check | QA | Coverage >= threshold |
| 6 | Self-check | Engineering | Lint, format, no TODOs |
| 7 | Checker validation | Checker | Matches spec + contract |
| 8 | Review | Reviewer + Security | Quality, security, perf |
| 9 | Approval | Approver | Final sign-off |
| 10 | PR + JIRA sync | Release manager + Integration | PR created, ticket updated |

Each stage is a Temporal activity. Failure at any stage blocks progression. Retries bounded (max 3 per gate, max 5 total chain).

---

## Phase 6: Quality + Release

**Objective**: Final validation. Deploy. Establish monitoring.

**Command**: `/release`

**Temporal Workflow**: `ReleaseWorkflow`

**Agents**: Release manager, QA, security reviewer, SRE, DevOps, product manager

**What Happens**:
1. `ValidateModuleGatesActivity` -- all modules passed `/approve`
2. `FullIntegrationTestActivity` -- run complete test suite
3. `FinalSecurityScanActivity` -- no critical/high findings
4. `PerformanceTestActivity` -- benchmarks against NFRs
5. `GenerateReleaseNotesActivity` -- from JIRA tickets + PRs
6. `DeployStagingActivity` -- deploy to staging
7. `SmokeTestActivity` -- validate staging
8. `DeployProductionActivity` -- deploy to production
9. `ValidateMonitoringActivity` -- dashboards, alerts active
10. `PublishReleaseNotesActivity` -- Confluence + GitHub release

**Artifacts**: Release notes. Deployment records. Monitoring dashboards. Alert rules.

**Exit Criteria**: Production deployment successful. Monitoring active. No critical issues. Release notes published. All JIRA tickets closed.

---

## Phase 7: Business Planning

**Objective**: Generate post-build business artifacts for go-to-market and funding.

**Command**: `/business-docs --phase planning`

**Temporal Workflow**: `BusinessDocsWorkflow` (mode=planning)

**Agents**: Cofounder, product manager, sales, marketing, FinOps

**What Happens**:
1. `FinancialModelActivity` -- projections, burn rate, runway, unit economics
2. `GtmStrategyActivity` -- channels, messaging, launch plan, pricing strategy
3. `PitchDeckActivity` -- investor-ready deck from all prior artifacts
4. `PublishToConfluenceActivity` -- all planning docs

**Artifacts**: Financial model. GTM strategy. Pitch deck. Confluence pages.

**Exit Criteria**: All planning documents generated and published.

---

## Phase 8: Operations

**Objective**: Ongoing monitoring, optimization, incident response, learning capture.

**Commands**: `/monitor`, `/optimize`

**Temporal Workflows**: `MonitorWorkflow` (cron), `OptimizeWorkflow`

**Agents**: SRE, DevOps, FinOps, memory/learning agents

**What Happens**:
- `MonitorWorkflow` (cron -- runs continuously):
  1. `CheckErrorRatesActivity` -- alert if above threshold
  2. `CheckPerformanceActivity` -- alert if degraded
  3. `CheckUptimeActivity` -- alert if below SLA
  4. `CheckCostActivity` -- alert if above budget

- `OptimizeWorkflow` (on-demand):
  1. `AnalyzePerformanceActivity` -- identify bottlenecks
  2. `AnalyzeCostActivity` -- identify waste
  3. `AnalyzeArchitectureActivity` -- identify improvement opportunities
  4. `GenerateRecommendationsActivity` -- actionable recommendations
  5. `CaptureLearningsActivity` -- store in Postgres for cross-product learning

**Artifacts**: Monitoring alerts. Optimization recommendations. Learning records.

**Exit Criteria**: None -- ongoing. Operations phase runs until product is decommissioned.

---

## Phase Transitions

```
Phase 0  --[all integrations valid]--> Phase 1
Phase 1  --[product created]---------> Phase 2a or 2b (parallel ok)
Phase 2a --[BMAD+PRD validated]------> Phase 3
Phase 2b --[discovery complete]------> Phase 3 (or parallel with 2a)
Phase 3  --[spec approved]-----------> Phase 4
Phase 4  --[arch approved]-----------> Phase 5
Phase 5  --[all modules approved]----> Phase 6
Phase 6  --[deployed + stable]-------> Phase 7
Phase 7  --[planning complete]-------> Phase 8
Phase 8  --[ongoing]----------------->  (continuous)
```

Every transition = Temporal signal. Current phase tracked in Postgres. Visible in Control Tower. Cannot skip. Cannot regress without explicit recovery workflow.
