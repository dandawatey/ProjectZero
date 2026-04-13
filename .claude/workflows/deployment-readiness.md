# Workflow: Deployment Readiness

## Purpose

Temporal child workflow that validates all pre-deployment criteria before a feature or release goes to production. Ensures infrastructure, configuration, monitoring, rollback plans, and compliance are verified.

## Temporal Identity

- **Workflow type**: `deployment_readiness_workflow`
- **Task queue**: `release-task-queue`
- **ID pattern**: `deploy-ready-{parent_workflow_id}-{timestamp}`
- **Execution timeout**: 2 hours
- **Invoked as**: Child workflow from feature_development_workflow or release_governance_workflow

## Stages

```
environment_check → config_validation → infra_readiness → monitoring_setup → rollback_plan → security_scan → readiness_verdict
```

### Stage 1: Environment Check

- **Activity**: `environment_check_activity`
- **Agent**: sre-engineer
- **Timeout**: start_to_close=15m
- **Checks**:
  - Target environment exists and is reachable
  - Environment variables are set (not values -- existence only)
  - Database migrations are pending and valid
  - Required secrets exist in secrets manager
- **Output**: `EnvironmentCheckResult(passed: bool, issues: list[str])`

### Stage 2: Config Validation

- **Activity**: `config_validation_activity`
- **Agent**: sre-engineer
- **Timeout**: start_to_close=15m
- **Checks**:
  - Feature flags configured for the deployment
  - API rate limits configured
  - CORS settings correct for target environment
  - Logging levels appropriate for production
- **Output**: `ConfigValidationResult(passed: bool, issues: list[str])`

### Stage 3: Infrastructure Readiness

- **Activity**: `infra_readiness_activity`
- **Agent**: sre-engineer
- **Timeout**: start_to_close=30m
- **Checks**:
  - Sufficient compute capacity
  - Database connection pool headroom
  - Cache layer healthy
  - Message queue / task queue capacity
  - SSL certificates valid and not near expiry
- **Output**: `InfraReadinessResult(passed: bool, issues: list[str], capacity_report: dict)`

### Stage 4: Monitoring Setup

- **Activity**: `monitoring_setup_activity`
- **Agent**: sre-engineer
- **Timeout**: start_to_close=15m
- **Checks**:
  - Prometheus metrics endpoints registered for new services
  - Grafana dashboards exist for the feature
  - Alert rules configured (error rate, latency, saturation)
  - Sentry project configured with proper DSN
  - OpenTelemetry trace propagation verified
- **Output**: `MonitoringSetupResult(passed: bool, issues: list[str])`

### Stage 5: Rollback Plan

- **Activity**: `rollback_plan_activity`
- **Agent**: release-manager
- **Timeout**: start_to_close=15m
- **Checks**:
  - Database migration has a down migration
  - Previous deployment artifact is tagged and available
  - Rollback runbook exists
  - Feature flag kill switch configured
  - Estimated rollback time documented
- **Output**: `RollbackPlanResult(passed: bool, rollback_time_estimate: str, issues: list[str])`

### Stage 6: Security Scan

- **Activity**: `security_scan_activity`
- **Agent**: security-reviewer
- **Timeout**: start_to_close=30m
- **Checks**:
  - No critical or high CVEs in dependencies
  - No secrets in codebase (git-secrets scan)
  - OWASP top 10 checklist for new endpoints
  - Authentication and authorization verified for new routes
- **Output**: `SecurityScanResult(passed: bool, vulnerabilities: list[dict], issues: list[str])`

### Stage 7: Readiness Verdict

- **Activity**: `readiness_verdict_activity`
- **Agent**: release-manager
- **Timeout**: start_to_close=10m
- **Input**: All previous stage results
- **Logic**: ALL stages must pass. Any single failure blocks deployment.
- **Output**: `ReadinessVerdict(status: "ready" | "not_ready", blockers: list[str], report: dict)`

## Workflow Definition

```python
@workflow.defn
class DeploymentReadinessWorkflow:
    def __init__(self):
        self.current_stage = "environment_check"

    @workflow.run
    async def run(self, params: DeploymentParams) -> ReadinessVerdict:
        all_issues = []
        retry = RetryPolicy(maximum_attempts=2)

        # Stage 1: Environment Check
        self.current_stage = "environment_check"
        env = await workflow.execute_activity(
            environment_check_activity, args=[params],
            start_to_close_timeout=timedelta(minutes=15), retry_policy=retry,
        )
        if not env.passed:
            all_issues.extend(env.issues)

        # Stage 2: Config Validation
        self.current_stage = "config_validation"
        config = await workflow.execute_activity(
            config_validation_activity, args=[params],
            start_to_close_timeout=timedelta(minutes=15), retry_policy=retry,
        )
        if not config.passed:
            all_issues.extend(config.issues)

        # Stage 3: Infra Readiness
        self.current_stage = "infra_readiness"
        infra = await workflow.execute_activity(
            infra_readiness_activity, args=[params],
            start_to_close_timeout=timedelta(minutes=30), retry_policy=retry,
        )
        if not infra.passed:
            all_issues.extend(infra.issues)

        # Stage 4: Monitoring Setup
        self.current_stage = "monitoring_setup"
        monitoring = await workflow.execute_activity(
            monitoring_setup_activity, args=[params],
            start_to_close_timeout=timedelta(minutes=15), retry_policy=retry,
        )
        if not monitoring.passed:
            all_issues.extend(monitoring.issues)

        # Stage 5: Rollback Plan
        self.current_stage = "rollback_plan"
        rollback = await workflow.execute_activity(
            rollback_plan_activity, args=[params],
            start_to_close_timeout=timedelta(minutes=15), retry_policy=retry,
        )
        if not rollback.passed:
            all_issues.extend(rollback.issues)

        # Stage 6: Security Scan
        self.current_stage = "security_scan"
        security = await workflow.execute_activity(
            security_scan_activity, args=[params],
            start_to_close_timeout=timedelta(minutes=30), retry_policy=retry,
        )
        if not security.passed:
            all_issues.extend(security.issues)

        # Stage 7: Verdict
        self.current_stage = "readiness_verdict"
        status = "ready" if len(all_issues) == 0 else "not_ready"
        return ReadinessVerdict(
            status=status,
            blockers=all_issues,
            report={
                "environment": env.dict(),
                "config": config.dict(),
                "infra": infra.dict(),
                "monitoring": monitoring.dict(),
                "rollback": rollback.dict(),
                "security": security.dict(),
            },
        )

    @workflow.query
    def get_current_stage(self) -> str:
        return self.current_stage
```

## Blocking vs Non-Blocking Issues

- **Blocking**: Critical CVE, missing rollback migration, unreachable environment, missing monitoring alerts
- **Non-blocking**: Minor CVE with no exploit path, cosmetic dashboard issue, non-critical config warning

Non-blocking issues are included in the report but do not prevent the `ready` verdict. The distinction is encoded in the activity logic, not the workflow.

## Integration with Parent Workflows

The parent workflow receives `ReadinessVerdict`. If `not_ready`, the parent workflow:
1. Records blockers in Postgres
2. Notifies the relevant agents/humans
3. Does NOT auto-retry -- human must resolve infrastructure issues
4. Waits for a `retry_readiness_signal` before re-running this child workflow
