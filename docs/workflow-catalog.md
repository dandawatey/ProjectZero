# Workflow Catalog

All Temporal workflows registered in ProjectZeroFactory.

---

## feature_development_workflow

**Purpose**: End-to-end feature delivery from intake to production deployment.

**Stages**: intake -> specification -> design -> architecture -> implementation -> testing -> review -> approval -> release_readiness -> completion

**Trigger**: New feature request (React UI or `/implement` command)

**Task Queue**: `feature-dev-task-queue`

**Involved Agents**: product-manager, spec-writer, ux-designer, architect, security-reviewer, backend-engineer, frontend-engineer, qa-engineer, code-reviewer, tech-lead, product-owner, release-manager, sre-engineer

**Child Workflows**: `maker_checker_reviewer_approver_workflow` (x4), `qa_validation_workflow`, `deployment_readiness_workflow`

**Timeout**: 7 days

---

## bug_fix_workflow

**Purpose**: Structured bug resolution from triage through deployment.

**Stages**: triage -> diagnosis -> fix -> testing -> review -> approval -> deployment

**Trigger**: Bug report (React UI or external integration)

**Task Queue**: `bugfix-task-queue`

**Involved Agents**: qa-engineer, backend-engineer, frontend-engineer, code-reviewer, tech-lead, release-manager

**Child Workflows**: `qa_validation_workflow`, `maker_checker_reviewer_approver_workflow`

**Timeout**: 12-72 hours (severity-dependent)

---

## qa_validation_workflow

**Purpose**: Full quality assurance pipeline execution.

**Stages**: test_plan -> unit_tests -> integration_tests -> e2e_tests -> coverage_check -> report

**Trigger**: Child workflow started by `feature_development_workflow` or `bug_fix_workflow`

**Task Queue**: `qa-task-queue`

**Involved Agents**: qa-engineer

**Child Workflows**: None

**Timeout**: 4 hours

---

## deployment_readiness_workflow

**Purpose**: Pre-deployment validation of infrastructure, configuration, monitoring, and security.

**Stages**: environment_check -> config_validation -> infra_readiness -> monitoring_setup -> rollback_plan -> security_scan -> readiness_verdict

**Trigger**: Child workflow started by `feature_development_workflow` or `release_governance_workflow`

**Task Queue**: `release-task-queue`

**Involved Agents**: sre-engineer, release-manager, security-reviewer

**Child Workflows**: None

**Timeout**: 2 hours

---

## release_governance_workflow

**Purpose**: Release approval chain collecting sign-offs from engineering, product, and operations.

**Stages**: release_summary -> engineering_signoff -> product_signoff -> ops_signoff -> release_authorization -> post_release_verification

**Trigger**: Feature approved and ready for release, or batch release initiated

**Task Queue**: `governance-task-queue`

**Involved Agents**: release-manager, tech-lead, product-owner, sre-engineer

**Child Workflows**: `deployment_readiness_workflow`

**Timeout**: 48 hours

---

## maker_checker_reviewer_approver_workflow

**Purpose**: Governance gate enforcing four-eye principle on all artifacts. Three sequential signal-based gates.

**Stages**: checker_gate -> reviewer_gate -> approver_gate

**Trigger**: Child workflow started by any parent workflow requiring governance

**Task Queue**: `governance-task-queue`

**Involved Agents**: Varies by artifact type (checker, reviewer, approver assigned by parent)

**Child Workflows**: None

**Timeout**: 13 hours (sum of gate timeouts: 1h + 4h + 8h)

---

## Workflow Relationship Map

```
feature_development_workflow
├── maker_checker_reviewer_approver_workflow  (spec approval)
├── maker_checker_reviewer_approver_workflow  (design approval)
├── maker_checker_reviewer_approver_workflow  (architecture approval)
├── qa_validation_workflow                    (testing)
├── maker_checker_reviewer_approver_workflow  (code review)
├── deployment_readiness_workflow             (pre-deploy)
└── release_governance_workflow               (release)
    └── deployment_readiness_workflow         (if not already run)

bug_fix_workflow
├── qa_validation_workflow                    (testing)
└── maker_checker_reviewer_approver_workflow  (fix review)
```

## Task Queue Summary

| Queue | Workflows/Activities | Scaling |
|-------|---------------------|---------|
| `feature-dev-task-queue` | Feature workflow orchestration | 1-2 workers |
| `bugfix-task-queue` | Bug fix workflow orchestration | 1-2 workers |
| `product-task-queue` | Intake, specification activities | 1-2 workers |
| `design-task-queue` | Design activities | 1 worker |
| `architecture-task-queue` | Architecture activities | 1 worker |
| `engineering-task-queue` | Implementation, fix, diagnosis | 2-4 workers |
| `qa-task-queue` | All test activities, QA workflow | 2-4 workers |
| `review-task-queue` | Code review, security review | 1-2 workers |
| `governance-task-queue` | MCRA, release sign-offs | 1-2 workers |
| `release-task-queue` | Deployment, release activities | 1 worker |
