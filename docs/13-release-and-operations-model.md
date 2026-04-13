# 13 - Release and Operations Model

## Overview

Releases are Temporal workflows. Monitoring is a command. Incidents are workflows. Bug fixes are workflows. Everything that moves code from approved to production and keeps it healthy runs through Temporal, with Postgres as the system of record and FastAPI as the API layer.

## Release Workflows

### DeploymentReadinessWorkflow

This Temporal workflow gates deployment. Each step is an activity. If any activity fails, the workflow stops and reports why.

```
build_check -> security_scan -> staging -> smoke_test -> approval -> prod -> health_check
```

**Activities in order**:

| Step | Activity | What It Does | Failure Behavior |
|---|---|---|---|
| 1 | `build_check` | Compile, lint, run all tests, check coverage threshold | Fail workflow. Fix and retry. |
| 2 | `security_scan` | Run SAST/DAST, check for critical/high findings | Fail workflow. No deploy with critical findings. |
| 3 | `staging` | Deploy to staging environment | Retry up to 3 times. Fail if staging unreachable. |
| 4 | `smoke_test` | Run smoke test suite against staging | Fail workflow. Staging is broken. |
| 5 | `approval` | Wait for human approval signal via Temporal signal | Blocks until signal received. Timeout configurable. |
| 6 | `prod` | Deploy to production environment | Retry up to 3 times. Rollback staging if prod fails. |
| 7 | `health_check` | Verify production health (endpoints, error rate, latency) | Alert on failure. Auto-rollback if critical. |

**Triggering**:
```
/release --version 1.0.0
```

This starts `DeploymentReadinessWorkflow` in Temporal. The workflow ID is deterministic: `deploy-{product}-{version}`.

### ReleaseGovernanceWorkflow

This Temporal workflow handles the release paperwork and communication. Runs in parallel with or after deployment.

```
changelog -> version_bump -> validation -> stakeholder_approval -> tag -> notify
```

**Activities in order**:

| Step | Activity | What It Does |
|---|---|---|
| 1 | `changelog` | Generate changelog from completed stories and their JIRA tickets |
| 2 | `version_bump` | Update version in package.json, pyproject.toml, etc. |
| 3 | `validation` | Validate all stories in the release are approved, all module gates passed |
| 4 | `stakeholder_approval` | Wait for stakeholder sign-off via Temporal signal |
| 5 | `tag` | Create git tag, create GitHub release |
| 6 | `notify` | Update Confluence release page, notify via configured channels |

### Release Types

| Type | Workflow | Gating | Use Case |
|---|---|---|---|
| Standard | Full DeploymentReadinessWorkflow | All 7 steps | Normal releases |
| Hotfix | DeploymentReadinessWorkflow (reduced) | build_check + security_scan + prod + health_check | Critical production fix |
| Rollback | RollbackWorkflow | health_check only | Production incident |

### Rollback

```
/release --rollback v0.9.0
```

1. Deploy the previous version tag to production
2. Run production health check
3. Verify monitoring shows recovery
4. Create a post-incident JIRA ticket for root cause analysis
5. The rolled-back changes remain on their branches for investigation

## Observability

Observability is configured during integration setup (Phase 0) via `guided-setup.sh` and `/factory-init`. The factory sets up four systems:

### Prometheus

Metrics collection. Scrapes FastAPI and application metrics.

**Key metrics**:

| Metric | Type | Alert Threshold |
|---|---|---|
| `http_request_duration_ms` | Histogram | P95 > 500ms |
| `http_request_total` | Counter | 5xx rate > 1% |
| `db_query_duration_ms` | Histogram | P95 > 200ms |
| `db_connection_pool_usage` | Gauge | > 80% |
| `temporal_workflow_failures` | Counter | > 0 in 5min window |
| `error_rate` | Rate | > 10/min |

### Grafana

Dashboards. Four standard dashboards created by the sre-engineer agent:

1. **Service Health**: Request rate, error rate, latency (RED metrics)
2. **Infrastructure**: CPU, memory, disk, network, Postgres connections
3. **Business**: Product-specific KPIs from the BMAD
4. **Deployment**: Recent deployments, rollback history, Temporal workflow status

### Sentry

Error tracking. Captures exceptions with full stack traces, breadcrumbs, and context.

**Configuration**:
- `SENTRY_DSN` in `.env`
- Source maps uploaded on deploy
- Release tracking tied to git tags
- Performance monitoring enabled

### OpenTelemetry

Distributed tracing. All requests get a trace ID that follows them through every service.

**What is traced**:
- HTTP requests (inbound and outbound)
- Database queries
- Temporal workflow and activity executions
- External API calls (JIRA, Confluence, GitHub)

**Configuration**:
- `OTEL_EXPORTER_OTLP_ENDPOINT` in `.env`
- Auto-instrumented via FastAPI middleware and Temporal interceptors

### Alert Configuration

Alerts follow a severity model:

| Severity | Response Time | Notification | Example |
|---|---|---|---|
| P1 - Critical | Immediate | PagerDuty + Slack | Service down, data loss |
| P2 - High | Within 1 hour | Slack + Email | Error rate > 5%, latency > 2s |
| P3 - Medium | Within 4 hours | Slack | Error rate > 1%, disk > 85% |
| P4 - Low | Next business day | Email | Warning thresholds, non-critical |

### Activity Monitor

The Activity Monitor at `/api/v1/activities/` provides operational visibility into all user and system actions. During release and operations phases, it tracks:

- **Release actions**: Who triggered `/release`, when, what version, approval decisions
- **Incident response**: Triage assignments, mitigation steps taken, resolution timeline
- **Operational commands**: `/monitor` and `/optimize` invocations with results summary
- **System events**: Deployment successes/failures, rollback triggers, integration errors

The Activity Monitor dashboard (`GET /api/v1/activities/summary`) gives operations teams a single view of all actions taken, categorized by type (release, incident, monitoring, optimization). The user timeline view (`GET /api/v1/activities/timeline/{user_id}`) shows what each team member did and when -- useful for post-incident reviews and operational audits.

## Monitoring Command

```
/monitor
```

The `/monitor` command queries Temporal, Postgres, and the observability stack to produce a health report:

- **Temporal**: Active workflows, failed workflows, task queue depth, worker status
- **Application**: Error rate, latency percentiles, request throughput
- **Infrastructure**: CPU, memory, disk, database connections
- **Integrations**: JIRA, Confluence, GitHub, Temporal connection health
- **Business**: Product KPIs from monitoring dashboards

## Incident Handling

Incidents are Temporal workflows.

### IncidentWorkflow

```
alert_fires -> triage -> mitigate -> resolve -> post_mortem -> follow_up
```

| Step | Activity | What It Does |
|---|---|---|
| 1 | `alert_fires` | Alert detected (from Prometheus/Sentry/manual) |
| 2 | `triage` | Assign severity (P1-P4), create JIRA incident ticket |
| 3 | `mitigate` | Execute runbook, reduce impact |
| 4 | `resolve` | Fix root cause (may trigger BugFixWorkflow) |
| 5 | `post_mortem` | Generate post-mortem document, update Confluence |
| 6 | `follow_up` | Create prevention tickets, update runbooks, capture learnings |

### BugFixWorkflow

Bug fixes go through the same governance chain as features, but with expedited timelines:

```
triage -> implement_fix -> test -> check -> review -> approve -> hotfix_deploy
```

This is a Temporal workflow. The hotfix deploy uses `DeploymentReadinessWorkflow` with reduced gating (build_check + security_scan + prod + health_check).

### Runbooks

Stored in `.claude/operations/runbooks/`, one per common failure mode. Referenced by the `mitigate` activity during incident handling.

### Post-Mortem Template

```markdown
# Incident Post-Mortem: {INCIDENT-ID}

## Summary
{One-line description}

## Timeline
| Time | Event |
|---|---|
| HH:MM | Alert fired |
| HH:MM | Triage complete |
| HH:MM | Mitigation applied |
| HH:MM | Root cause fixed |
| HH:MM | Service restored |

## Impact
- Duration: {X} minutes
- Users affected: {N}
- Revenue impact: {$X or N/A}

## Root Cause
{What went wrong and why}

## Action Items
- [ ] {Action} - Owner: {agent} - Due: {date}

## Learnings Captured
- {Learning promoted to .claude/learning/}
```

## Post-Release Business Documents

After a successful release, generate the business document suite:

```
/business-docs --phase planning
```

This triggers the `BusinessDocsWorkflow` with phase=planning, which generates:
- Financial projections (revenue model, unit economics, burn rate)
- Costing analysis (infrastructure, team, tooling)
- GTM strategy (go-to-market plan, channels, pricing)
- Pitch deck (investor-ready presentation)
- Data room documents

These are generated based on the actual built product -- real architecture, real infrastructure costs, real feature set.

## Operations Checklist

### Pre-Launch

- [ ] All monitoring dashboards created (Grafana)
- [ ] All alerts configured (Prometheus) and tested
- [ ] Sentry configured with source maps
- [ ] OpenTelemetry tracing verified end-to-end
- [ ] Runbooks written for known failure modes
- [ ] Rollback procedure documented and tested
- [ ] SLOs defined and baseline established
- [ ] Backup and restore procedure tested

### Post-Launch (First 24 Hours)

- [ ] Error rate within acceptable range (< 1%)
- [ ] Latency within NFR benchmarks
- [ ] No critical or high alerts
- [ ] Traces flowing correctly through OpenTelemetry
- [ ] Sentry capturing errors with correct source maps
- [ ] Resource utilization within expected range

## 8-Phase Context

Release and operations span Phases 7 and 8 of the factory flow:

| Phase | What Happens | Temporal Workflows |
|---|---|---|
| Phase 7: Release | Code deployed, release governed | DeploymentReadinessWorkflow, ReleaseGovernanceWorkflow |
| Phase 8: Operations | Monitor, optimize, incident response | IncidentWorkflow, BugFixWorkflow, HealthCheckWorkflow |

After Phase 8, the cycle loops back. `/optimize` creates new tickets that feed into `/implement` for the next iteration.
