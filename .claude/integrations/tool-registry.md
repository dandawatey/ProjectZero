# Tool Registry

## Required Integrations

| Tool | Purpose | Env Keys | Validation | Blocks? |
|------|---------|----------|-----------|---------|
| GitHub | Code repos, PRs | GITHUB_TOKEN, GITHUB_ORG | GET /user | YES |
| JIRA | Tickets, tracking | JIRA_BASE_URL, JIRA_USER_EMAIL, JIRA_API_TOKEN, JIRA_PROJECT_KEY | GET /myself | YES |
| Confluence | Documentation | CONFLUENCE_BASE_URL, CONFLUENCE_API_TOKEN, CONFLUENCE_SPACE_KEY | GET /space | YES |
| Temporal | Workflow engine | TEMPORAL_HOST, TEMPORAL_NAMESPACE, TEMPORAL_TASK_QUEUE | TCP connect | YES |
| Postgres | State database | DATABASE_URL | SELECT 1 | YES |
| Redis | Queue/cache | REDIS_URL | PING | YES |
| Anthropic | AI provider | ANTHROPIC_API_KEY, CLAUDE_MODEL | POST /messages | YES |

## Optional Integrations

| Tool | Purpose | Env Keys | Blocks? |
|------|---------|----------|---------|
| Sentry | Error tracking | SENTRY_DSN | NO |
| PostHog | Product analytics | POSTHOG_API_KEY | NO |
| Stripe | Payments | STRIPE_SECRET_KEY | NO |
| Razorpay | Payments (India) | RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET | NO |
| MinIO | Object storage | MINIO_ENDPOINT, MINIO_ACCESS_KEY, MINIO_SECRET_KEY | NO |
| Datadog | APM | DATADOG_API_KEY | NO |

## Validation Scripts
- `scripts/guided-setup.sh` — Interactive setup for all integrations
- `scripts/validate-integrations.sh` — Validates all connections
- `scripts/validate-env.sh` — Checks .env completeness

## Integration Flow
```
/factory-init
  → detect .env
  → if missing: guided-setup.sh
  → validate-integrations.sh
  → ALL PASS? → proceed
  → ANY FAIL? → BLOCK
```
