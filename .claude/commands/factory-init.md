# Command: /factory-init

## Purpose
Validate factory repo structure AND all integrations. Gate to all execution.

## Rule
NO INTEGRATION → NO EXECUTION. All required systems must validate before proceeding.

## Trigger
User runs `/factory-init` after cloning factory. First command always.

## Step-by-Step Process

### Step 1: Detect .env
- Check .env exists
- If missing → run `./scripts/guided-setup.sh` (interactive)
- If exists → proceed to validation

### Step 2: Validate Integrations (MANDATORY)
Run `./scripts/validate-integrations.sh`. Checks:

| Integration | Validation Method | Blocks If Failed? |
|-------------|------------------|-------------------|
| GitHub | API call to /user | YES |
| JIRA | API call to /myself | YES |
| Confluence | API call to /space | YES |
| Temporal | TCP connect or SDK list | YES |
| Postgres | psql SELECT 1 or TCP | YES |
| Redis | PING or TCP | YES |
| Anthropic | API call to /messages | YES |
| Sentry | Check DSN format | NO (optional) |
| PostHog | Check key format | NO (optional) |

**ALL required integrations must pass. ANY failure → BLOCK.**

### Step 3: Validate Factory Structure
Check directories: agents/, skills/, workflows/, commands/, templates/, guardrails/
Check files: CLAUDE.md, settings.json, AGENT_REGISTRY.md

### Step 4: Validate Completeness
- 35 agent files across 8 team folders
- 17 skill folders with 4 files each
- All workflow definitions present
- All command definitions present
- Product skeleton template exists

### Step 5: Register Status
Write to console:
```
Factory Status: READY
Integrations: 7/7 required validated
Optional: X/4 configured
Ready for: /bootstrap-product
```

## Required Inputs
- .env file with credentials (or interactive setup)

## Involved Agents
- repo-validator (structure)
- plugin-validator (skills)

## Outputs
- Validation report (pass/fail per integration)
- Factory readiness status

## Failure Handling
- Missing .env → launch guided-setup.sh
- Invalid key → show which key, show how to get it, block
- Unreachable service → show connection details, suggest fix, block
- Never proceed with failed required integrations

## Next Command
/bootstrap-product (only if ALL required integrations pass)
