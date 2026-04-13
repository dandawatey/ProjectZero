# Integration Setup Guide

## Quick Setup
```bash
./scripts/guided-setup.sh    # interactive, walks through each integration
./scripts/validate-integrations.sh   # validates all connections
```

## Manual Setup

### 1. GitHub (REQUIRED)
**Get token:**
1. Go to https://github.com/settings/tokens
2. "Generate new token (classic)"
3. Select scopes: `repo`, `workflow`, `admin:org` (if using org)
4. Copy token

**Set in .env:**
```
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx
GITHUB_ORG=your-org
GITHUB_DEFAULT_BRANCH=main
```

**Validates:** `GET https://api.github.com/user` (200 = valid)

---

### 2. JIRA (REQUIRED)
**Get token:**
1. Go to https://id.atlassian.com/manage-profile/security/api-tokens
2. "Create API token"
3. Copy token

**Set in .env:**
```
JIRA_BASE_URL=https://your-org.atlassian.net
JIRA_USER_EMAIL=you@company.com
JIRA_API_TOKEN=xxxxxxxxxxxxxxxx
JIRA_PROJECT_KEY=PZ
```

**Validates:** `GET {base}/rest/api/3/myself` with basic auth (200 = valid)

**Bootstrap creates:** JIRA project (if missing), verifies ticket creation capability.

---

### 3. Confluence (REQUIRED)
**Same Atlassian token as JIRA.**

**Set in .env:**
```
CONFLUENCE_BASE_URL=https://your-org.atlassian.net/wiki
CONFLUENCE_API_TOKEN=xxxxxxxxxxxxxxxx
CONFLUENCE_SPACE_KEY=PZ
```

**Validates:** `GET {base}/rest/api/space` (200 = valid)

**Bootstrap creates:** Confluence space (if missing), project hub page structure.

---

### 4. Temporal (REQUIRED)
**Local setup:**
```bash
brew install temporal          # macOS
temporal server start-dev      # starts on localhost:7233
```

**Set in .env:**
```
TEMPORAL_HOST=localhost:7233
TEMPORAL_NAMESPACE=default
TEMPORAL_TASK_QUEUE=projectzero-factory
```

**Validates:** TCP connect to host:port, or `temporal workflow list`

---

### 5. Postgres (REQUIRED)
**Local setup:**
```bash
brew install postgresql@15
brew services start postgresql@15
createdb projectzero
```

**Set in .env:**
```
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/projectzero
```

**Validates:** `SELECT 1` via psql or TCP connect

---

### 6. Redis (REQUIRED)
**Local setup:**
```bash
brew install redis
brew services start redis
```

**Set in .env:**
```
REDIS_URL=redis://localhost:6379
```

**Validates:** `PING` → `PONG` via redis-cli or TCP connect

---

### 7. Anthropic (REQUIRED)
**Get key:**
1. Go to https://console.anthropic.com/settings/keys
2. Create API key
3. Copy key

**Set in .env:**
```
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxx
CLAUDE_MODEL=claude-sonnet-4-20250514
```

**Validates:** POST to /v1/messages (200 = valid)

---

### 8. Optional: Sentry
```
SENTRY_DSN=https://xxx@sentry.io/xxx
```

### 9. Optional: PostHog
```
POSTHOG_API_KEY=phc_xxxxxxxx
```

### 10. Optional: Stripe / Razorpay
```
STRIPE_SECRET_KEY=sk_xxxx
RAZORPAY_KEY_ID=rzp_xxxx
RAZORPAY_KEY_SECRET=xxxx
```

### 11. Optional: MinIO (object storage)
```
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET=projectzero
```

## Validation Gate

Before ANY workflow executes:
```
[ ] GitHub validated
[ ] JIRA validated
[ ] Confluence validated
[ ] Temporal connected
[ ] Database connected
[ ] Redis connected
[ ] AI key working

ANY FAILURE → BLOCK EXECUTION
```
