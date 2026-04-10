# SRE Module

## SLOs (Service Level Objectives)
| Metric | Target | Measurement |
|--------|--------|-------------|
| Availability | 99.9% | Successful requests / total requests per month |
| Latency p50 | < 200ms | Request duration histogram |
| Latency p99 | < 2s | Request duration histogram |
| Error Rate | < 0.1% | 5xx responses / total responses |

## Monitoring Stack
- **Metrics**: Prometheus + Grafana (or cloud-native: CloudWatch/Datadog)
- **Logs**: Structured JSON → ELK/CloudWatch/Datadog Logs
- **Traces**: OpenTelemetry → Jaeger/Datadog APM
- **Alerting**: PagerDuty/OpsGenie integration

## Health Endpoints
- `GET /health` — Liveness probe (is the process running?)
- `GET /ready` — Readiness probe (can it serve traffic?)
- `GET /health/deep` — Deep health (DB, Redis, external APIs all connected?)

## Alerting Rules
- Page (P1): SLO breach, service down, error rate > 1%
- Warn (P2): Latency trending up, error rate > 0.5%, disk > 80%
- Info (P3): Deployment completed, scaling event, certificate expiring in 30 days

## Incident Response
1. Alert fires → on-call notified
2. Triage: determine severity (P1-P4)
3. Investigate: check logs, metrics, traces
4. Mitigate: apply immediate fix or rollback
5. Resolve: permanent fix with tests
6. Postmortem: blameless review within 48 hours
7. Action items: create prevention tickets
