# Observability Rules

## Logging
- Structured JSON format for all log entries
- Required fields: timestamp, level, message, requestId, service
- Log levels: DEBUG (dev only), INFO (normal ops), WARN (recoverable), ERROR (action needed)
- No PII in logs (redact before logging)
- Request ID in every log line for correlation

## Metrics
- Request count by endpoint and status code
- Request duration histogram (p50, p95, p99)
- Error rate by service
- Business metrics (signups, key actions, revenue events)
- Infrastructure metrics (CPU, memory, disk, connections)

## Tracing
- Distributed tracing enabled (OpenTelemetry)
- Trace ID propagated across all service calls
- Span annotations for key operations (DB queries, external calls)
- Sampling: 100% for errors, 10% for normal requests

## Health Endpoints
- Every service exposes /health (liveness) and /ready (readiness)
- /health/deep checks all dependencies
- Health endpoints excluded from authentication

## Dashboards
- One dashboard per module (key metrics at a glance)
- System overview dashboard (all modules, infrastructure)
- Alerting dashboard (active alerts, recent incidents)

## Alerting
- Every alert has a linked runbook
- No alert without defined response action
- Alert fatigue prevention: tune thresholds, suppress flapping
