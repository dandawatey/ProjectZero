# Tool Registry

| Tool | Purpose | Config Key | Health Check |
|------|---------|-----------|--------------|
| JIRA | Work tracking | jira.* | GET /rest/api/3/myself |
| Confluence | Documentation | confluence.* | GET /wiki/rest/api/space |
| GitHub | Code management | github.* | GET /user |
| Slack | Notifications | slack.* | POST webhook with test message |
| Redis | Queue/Cache | REDIS_URL | PING command |
| PostgreSQL | Database | DATABASE_URL | SELECT 1 |
| Dagster | Pipelines | DAGSTER_HOST:PORT | GET /dagit |
