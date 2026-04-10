# 13 - Release and Operations Model

## Overview

The release and operations model governs how software moves from approved code to production, how it is monitored in production, how incidents are handled, and how support workflows operate. This is the Completion stage of SPARC, extended into ongoing operations.

## Release Process

### Release Gating

Before any release can proceed, all gates must pass:

| Gate | Checked By | Criteria |
|---|---|---|
| All tests pass | qa-engineer | Unit, integration, E2E: 100% pass rate |
| Coverage threshold | qa-engineer | Minimum 80% line coverage (configurable) |
| Security clear | security-reviewer | No critical or high findings |
| All stories approved | approver | Every story in the release has passed the governance chain |
| Module gates passed | approver | Every module included has passed its module gate checklist |
| Performance validated | sre-engineer | NFR benchmarks met (response times, throughput, resource usage) |
| Release notes drafted | product-manager | User-facing changes documented |
| Rollback plan documented | release-manager | Steps to roll back if deployment fails |

### Release Command

```
/release --version 1.0.0
```

This command triggers the release-manager agent to orchestrate:

1. **Pre-release validation**: Run all gates above
2. **Create release branch**: `release/v1.0.0` from the current main
3. **Tag the release**: `v1.0.0`
4. **Generate release notes**: From completed stories and their descriptions
5. **Build artifacts**: Compile, bundle, containerize
6. **Deploy to staging**: Using the CI/CD pipeline
7. **Run staging smoke tests**: Verify core functionality
8. **Deploy to production**: After staging validation
9. **Run production smoke tests**: Verify core functionality in production
10. **Activate monitoring**: Confirm dashboards and alerts are live
11. **Notify stakeholders**: Release announcement via Confluence and JIRA

### Release Types

| Type | Branch Pattern | Gating | Use Case |
|---|---|---|---|
| Standard | `release/v{major}.{minor}.{patch}` | Full gates | Normal releases |
| Hotfix | `hotfix/v{major}.{minor}.{patch+1}` | Reduced gates (security + tests only) | Critical production fix |
| Rollback | N/A (revert to previous tag) | No gates (emergency) | Production incident |

### Rollback Procedure

```
/release --rollback v0.9.0
```

1. Deploy the previous version tag to production
2. Run production smoke tests
3. Verify monitoring shows recovery
4. Create a post-incident ticket for root cause analysis
5. The rolled-back changes remain on their branches for investigation

## Observability

### Three Pillars

The factory establishes observability through logs, metrics, and traces.

#### Logs

**Configuration**: `.claude/operations/observability.md` and `.claude/sre/logging.md`

**Standards**:
- Structured JSON logging (no unstructured text logs)
- Every log entry includes: timestamp, level, service, trace_id, span_id, message, context
- Log levels: DEBUG, INFO, WARN, ERROR, FATAL
- Production runs at INFO level by default
- Sensitive data (passwords, tokens, PII) is never logged

**Log format**:
```json
{
  "timestamp": "2026-01-22T14:30:00.123Z",
  "level": "ERROR",
  "service": "user-management",
  "trace_id": "abc123def456",
  "span_id": "span789",
  "message": "Failed to create user: duplicate email",
  "context": {
    "endpoint": "/api/auth/register",
    "method": "POST",
    "status_code": 409,
    "duration_ms": 45,
    "user_agent": "Mozilla/5.0..."
  },
  "error": {
    "type": "DuplicateEmailError",
    "message": "Email already registered",
    "stack": "..."
  }
}
```

**Integration**: Logs are shipped to the configured observability backend via `OTEL_EXPORTER_OTLP_ENDPOINT` or `SENTRY_DSN` or `DATADOG_API_KEY`.

#### Metrics

**Key metrics tracked**:

| Metric | Type | Description | Alert Threshold |
|---|---|---|---|
| `http_request_duration_ms` | Histogram | API response time | P95 > 500ms |
| `http_request_total` | Counter | Total requests by endpoint and status | 5xx rate > 1% |
| `db_query_duration_ms` | Histogram | Database query time | P95 > 200ms |
| `db_connection_pool_usage` | Gauge | Connection pool utilization | > 80% |
| `queue_depth` | Gauge | Work queue depth | > 100 items |
| `error_rate` | Rate | Errors per minute | > 10/min |
| `cpu_usage_percent` | Gauge | CPU utilization | > 80% |
| `memory_usage_mb` | Gauge | Memory usage | > 80% of limit |
| `disk_usage_percent` | Gauge | Disk utilization | > 85% |

**Custom business metrics** (defined per product):
- User registrations per hour
- Active sessions
- API calls per customer
- Revenue-impacting transaction success rate

#### Traces

**Distributed tracing**: All requests get a trace ID that follows them through every service, database call, and external API call.

**Trace format**: OpenTelemetry (OTLP) compatible.

**What is traced**:
- HTTP requests (inbound and outbound)
- Database queries
- Cache operations
- Queue operations
- External API calls (JIRA, Confluence, GitHub)

### Dashboards

The sre-engineer agent creates four standard dashboards:

1. **Service Health**: Request rate, error rate, latency (RED metrics)
2. **Infrastructure**: CPU, memory, disk, network
3. **Business**: Product-specific KPIs from the BMAD
4. **Deployment**: Recent deployments, rollback history, deployment duration

### Alert Configuration

Alerts are defined in `.claude/sre/` and follow a severity model:

| Severity | Response Time | Notification | Example |
|---|---|---|---|
| P1 - Critical | Immediate | PagerDuty + Slack | Service down, data loss |
| P2 - High | Within 1 hour | Slack + Email | Error rate > 5%, latency > 2s |
| P3 - Medium | Within 4 hours | Slack | Error rate > 1%, disk > 85% |
| P4 - Low | Next business day | Email | Warning thresholds, non-critical issues |

## Incident Handling

### Incident Workflow

```
Alert fires
  |
  v
Incident created (auto or manual)
  |
  v
Triage: Assign severity (P1-P4)
  |
  v
Respond: Mitigate the impact
  |
  v
Resolve: Fix the root cause
  |
  v
Post-mortem: Document learnings
  |
  v
Follow-up: Implement prevention
```

### Incident Response Runbooks

Stored in `.claude/operations/runbooks/`, one per common failure mode:

```markdown
# Runbook: Database Connection Pool Exhaustion

## Symptoms
- 503 errors on API endpoints
- `db_connection_pool_usage` > 95%
- Slow query log shows waiting connections

## Immediate Mitigation
1. Scale up the connection pool: `ALTER SYSTEM SET max_connections = 200;`
2. Kill idle connections: `SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE state = 'idle' AND query_start < now() - interval '5 minutes';`
3. Restart the API service to reset the pool

## Root Cause Investigation
1. Check for long-running queries: `SELECT * FROM pg_stat_activity WHERE state = 'active' ORDER BY query_start;`
2. Check for connection leaks in application code
3. Review recent deployments for connection handling changes

## Prevention
- Set connection pool max to `max_connections * 0.8 / num_workers`
- Add connection timeout (5s)
- Add circuit breaker for database connections
- Monitor pool usage with alert at 80%
```

### Post-Mortem Template

```markdown
# Incident Post-Mortem: {INCIDENT-ID}

## Summary
{One-line description of what happened}

## Timeline
| Time | Event |
|---|---|
| 14:00 | Alert fired: error rate > 5% |
| 14:05 | On-call acknowledged |
| 14:15 | Root cause identified: deployment introduced N+1 query |
| 14:20 | Rollback initiated |
| 14:25 | Service restored |

## Impact
- Duration: {X} minutes
- Users affected: {N}
- Revenue impact: {$X or N/A}
- SLO budget consumed: {X}%

## Root Cause
{Detailed explanation of what went wrong and why}

## What Went Well
- {Positive observation}

## What Could Be Improved
- {Improvement opportunity}

## Action Items
- [ ] {Action} - Owner: {agent/person} - Due: {date}

## Learnings Captured
- {Learning promoted to .claude/learning/}
```

## Support Workflow

### Support Ticket Flow

```
User reports issue
  |
  v
Support ticket created (JIRA Bug type)
  |
  v
Triage: Severity and priority assigned
  |
  v
Investigation: Relevant agent investigates
  |
  v
Resolution: Fix developed through normal governance
  |
  v
Verification: User confirms fix
  |
  v
Close: Ticket closed, learning captured
```

### Support Integration

The factory creates support-related JIRA tickets with:
- **Type**: Bug
- **Priority**: Based on severity (P1 = Blocker, P2 = Critical, P3 = Major, P4 = Minor)
- **Labels**: `support`, `production`
- **Links**: Related to the original story that introduced the issue

## Analytics Tracking

### Event Tracking

The factory supports product analytics through structured event tracking:

```json
{
  "event": "user_registered",
  "timestamp": "2026-01-22T14:30:00Z",
  "properties": {
    "method": "email",
    "source": "landing_page",
    "plan": "free"
  },
  "user_id": "usr_abc123",
  "session_id": "sess_def456"
}
```

### Analytics Configuration

Analytics tracking is defined in `.claude/analytics/`:

```
.claude/analytics/
  events.json             # Event catalog (all tracked events)
  funnels.json            # Funnel definitions
  segments.json           # User segment definitions
  dashboards.json         # Analytics dashboard configurations
```

### Event Catalog

Every trackable event is defined before implementation:

```json
{
  "events": [
    {
      "name": "user_registered",
      "description": "User completed registration",
      "properties": {
        "method": {"type": "string", "enum": ["email", "google", "github"]},
        "source": {"type": "string"},
        "plan": {"type": "string", "enum": ["free", "pro", "enterprise"]}
      },
      "triggers": ["registration form submission"],
      "owner": "user-management module"
    }
  ]
}
```

### Analytics Governance

- Events must be defined in the event catalog before being implemented
- Event names follow a consistent naming convention: `{noun}_{verb}` (e.g., `user_registered`, `subscription_created`, `report_viewed`)
- All events include standard properties (timestamp, user_id, session_id)
- PII is never included in event properties
- The checker agent validates that implemented analytics calls match the event catalog

## Operations Checklist

### Pre-Launch

- [ ] All monitoring dashboards created and validated
- [ ] All alerts configured and tested
- [ ] Runbooks written for known failure modes
- [ ] Rollback procedure documented and tested
- [ ] On-call rotation established (if applicable)
- [ ] SLOs defined and baseline established
- [ ] Analytics events implemented and validated
- [ ] Error tracking configured (Sentry or equivalent)
- [ ] Log aggregation configured and validated
- [ ] Backup and restore procedure documented and tested

### Post-Launch (First 24 Hours)

- [ ] Error rate within acceptable range (< 1%)
- [ ] Latency within NFR benchmarks
- [ ] No critical or high alerts
- [ ] Analytics events flowing correctly
- [ ] Logs aggregating correctly
- [ ] Resource utilization within expected range
