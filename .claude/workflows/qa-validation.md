# Workflow: QA Validation

## Purpose

Temporal child workflow that executes the full quality assurance pipeline. Started by parent workflows (feature_development, bug_fix) when code reaches the testing stage. Runs test plan generation, unit tests, integration tests, E2E tests, coverage checks, and produces a consolidated report.

## Temporal Identity

- **Workflow type**: `qa_validation_workflow`
- **Task queue**: `qa-task-queue`
- **ID pattern**: `qa-{parent_workflow_id}-{timestamp}`
- **Execution timeout**: 4 hours
- **Invoked as**: Child workflow

## Stages

```
test_plan → unit_tests → integration_tests → e2e_tests → coverage_check → report
```

### Stage 1: Test Plan

- **Activity**: `test_plan_activity`
- **Agent**: qa-engineer
- **Task queue**: `qa-task-queue`
- **Timeout**: start_to_close=30m
- **Input**: Feature spec, implementation artifacts, acceptance criteria
- **Output**: Test plan document (test cases, priority, coverage targets, test data requirements)

### Stage 2: Unit Tests

- **Activity**: `unit_test_activity`
- **Agent**: qa-engineer
- **Task queue**: `qa-task-queue`
- **Timeout**: start_to_close=1h
- **Input**: Test plan, source code
- **Output**: Unit test results (passed, failed, skipped counts; failure details; execution time)
- **Gate**: If any unit test fails, workflow can continue to collect all results but marks overall status as `failed`

### Stage 3: Integration Tests

- **Activity**: `integration_test_activity`
- **Agent**: qa-engineer
- **Task queue**: `qa-task-queue`
- **Timeout**: start_to_close=1h
- **Input**: Test plan, source code, integration test config
- **Output**: Integration test results (API contract validation, database interaction tests, service communication tests)
- **Dependency**: Runs after unit_tests complete (sequential, not parallel)

### Stage 4: E2E Tests

- **Activity**: `e2e_test_activity`
- **Agent**: qa-engineer (invokes playwright-skill)
- **Task queue**: `qa-task-queue`
- **Timeout**: start_to_close=2h
- **Input**: Test plan, deployed test environment URL, user flows
- **Output**: E2E test results (user flow pass/fail, screenshots on failure, performance metrics)
- **Conditional**: Only runs if feature has UI components. Skipped for backend-only features.

### Stage 5: Coverage Check

- **Activity**: `coverage_check_activity`
- **Agent**: qa-engineer
- **Task queue**: `qa-task-queue`
- **Timeout**: start_to_close=15m
- **Input**: All test results, source code
- **Output**: Coverage report (line coverage, branch coverage, function coverage, per-file breakdown)
- **Threshold**: 80% line coverage minimum (configured per product). Below threshold = `failed`.

### Stage 6: Report

- **Activity**: `qa_report_activity`
- **Agent**: qa-engineer
- **Task queue**: `qa-task-queue`
- **Timeout**: start_to_close=15m
- **Input**: All stage results
- **Output**: Consolidated QA report (overall status, per-stage results, coverage summary, risk assessment, recommendations)
- **Side effect**: Writes report to Postgres via sync layer

## Workflow Definition

```python
@workflow.defn
class QAValidationWorkflow:
    def __init__(self):
        self.current_stage = "test_plan"

    @workflow.run
    async def run(self, params: QAParams) -> QAResult:
        failures = []

        # Stage 1: Test Plan
        self.current_stage = "test_plan"
        test_plan = await workflow.execute_activity(
            test_plan_activity, args=[params],
            start_to_close_timeout=timedelta(minutes=30),
            retry_policy=RetryPolicy(maximum_attempts=2),
        )

        # Stage 2: Unit Tests
        self.current_stage = "unit_tests"
        unit_results = await workflow.execute_activity(
            unit_test_activity, args=[test_plan, params.impl_artifacts],
            start_to_close_timeout=timedelta(hours=1),
            retry_policy=RetryPolicy(maximum_attempts=2),
        )
        if unit_results.failed_count > 0:
            failures.append(("unit_tests", unit_results.failures))

        # Stage 3: Integration Tests
        self.current_stage = "integration_tests"
        integration_results = await workflow.execute_activity(
            integration_test_activity, args=[test_plan, params.impl_artifacts],
            start_to_close_timeout=timedelta(hours=1),
            retry_policy=RetryPolicy(maximum_attempts=2),
        )
        if integration_results.failed_count > 0:
            failures.append(("integration_tests", integration_results.failures))

        # Stage 4: E2E Tests (conditional)
        e2e_results = None
        if params.has_ui_components:
            self.current_stage = "e2e_tests"
            e2e_results = await workflow.execute_activity(
                e2e_test_activity, args=[test_plan, params.test_env_url],
                start_to_close_timeout=timedelta(hours=2),
                retry_policy=RetryPolicy(maximum_attempts=2),
            )
            if e2e_results.failed_count > 0:
                failures.append(("e2e_tests", e2e_results.failures))

        # Stage 5: Coverage Check
        self.current_stage = "coverage_check"
        coverage = await workflow.execute_activity(
            coverage_check_activity,
            args=[unit_results, integration_results, params.impl_artifacts],
            start_to_close_timeout=timedelta(minutes=15),
            retry_policy=RetryPolicy(maximum_attempts=2),
        )
        if coverage.line_coverage < params.coverage_threshold:
            failures.append(("coverage_check", f"Line coverage {coverage.line_coverage}% < {params.coverage_threshold}% threshold"))

        # Stage 6: Report
        self.current_stage = "report"
        report = await workflow.execute_activity(
            qa_report_activity,
            args=[test_plan, unit_results, integration_results, e2e_results, coverage, failures],
            start_to_close_timeout=timedelta(minutes=15),
        )

        overall_status = "passed" if len(failures) == 0 else "failed"
        return QAResult(
            status=overall_status,
            failures=failures,
            report=report,
            coverage=coverage,
        )

    @workflow.query
    def get_current_stage(self) -> str:
        return self.current_stage
```

## QA Report Schema

```json
{
  "feature_id": "string",
  "workflow_id": "string",
  "overall_status": "passed | failed",
  "stages": {
    "test_plan": { "status": "completed", "test_case_count": 42 },
    "unit_tests": { "status": "passed", "passed": 38, "failed": 0, "skipped": 0, "duration_ms": 12340 },
    "integration_tests": { "status": "passed", "passed": 12, "failed": 0, "skipped": 0, "duration_ms": 45600 },
    "e2e_tests": { "status": "passed", "passed": 8, "failed": 0, "skipped": 2, "duration_ms": 120000 },
    "coverage_check": { "status": "passed", "line_coverage": 87.3, "branch_coverage": 82.1, "threshold": 80.0 }
  },
  "risk_assessment": "low | medium | high",
  "recommendations": ["string"],
  "generated_at": "ISO8601"
}
```

## Retry Policy

All test activities retry up to 2 times with no backoff. Test infrastructure flakiness is the primary retry target. If tests fail consistently across retries, the failure is real and propagated to the parent workflow.

## Failure Propagation

When `qa_validation_workflow` returns `status=failed`, the parent workflow receives the full failure list. The parent decides whether to:
- Return the feature to implementation stage (feature_development_workflow)
- Return the fix to the fix stage (bug_fix_workflow)
- Escalate to human decision
