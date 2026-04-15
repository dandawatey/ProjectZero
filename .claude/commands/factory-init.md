# Command: /factory-init

## Purpose
Validate factory repo structure AND all integrations. Gate to all execution.

## Rule
NO INTEGRATION → NO EXECUTION. All required systems must validate before proceeding.

**Exception — brownfield mode**: Integrations explicitly skipped via `--skip` are excluded from the gate. Skipped integrations are disabled in product .env, not assumed present.

## Trigger
User runs `/factory-init` after cloning factory. First command always.

## Flags

| Flag | Effect |
|------|--------|
| `--brownfield` | Enables brownfield mode. Prompts which integrations to skip. |
| `--skip=jira` | Skip JIRA validation (sets JIRA_ENABLED=false) |
| `--skip=confluence` | Skip Confluence validation |
| `--skip=temporal` | Skip Temporal validation |
| `--skip=jira,confluence` | Skip multiple (comma-separated) |
| `--skip=all-optional` | Skip Sentry, PostHog |
| `--partial` | Alias for `--brownfield` |

Required integrations that cannot be skipped: **GitHub, Postgres, Anthropic**.
Redis and Temporal can be skipped in brownfield mode (async features disabled).

## Step-by-Step Process

### Step 1: Detect .env
- Check .env exists
- If missing → run `./scripts/guided-setup.sh` (interactive)
- If exists → proceed to validation

### Step 1b: Detect Mode
If `--brownfield` or `--partial` flag present:
```
Brownfield mode active.
Which integrations are NOT available for this project?
  [ ] JIRA
  [ ] Confluence
  [ ] Temporal
  [ ] Redis
  (GitHub, Postgres, Anthropic always required)
```
Mark selected as SKIP. Store in session context.

### Step 2: Validate Integrations (MANDATORY for non-skipped)
Run `./scripts/validate-integrations.sh`. Checks:

| Integration | Validation Method | Blocks If Failed? | Skippable? |
|-------------|------------------|-------------------|------------|
| GitHub | API call to /user | YES | NO |
| JIRA | API call to /myself | YES | YES (brownfield) |
| Confluence | API call to /space | YES | YES (brownfield) |
| Temporal | TCP connect or SDK list | YES | YES (brownfield) |
| Postgres | psql SELECT 1 or TCP | YES | NO |
| Redis | PING or TCP | YES | YES (brownfield) |
| Anthropic | API call to /messages | YES | NO |
| Sentry | Check DSN format | NO (optional) | YES |
| PostHog | Check key format | NO (optional) | YES |

**All non-skipped required integrations must pass. ANY failure → BLOCK.**
**Skipped integrations → logged as DISABLED, not failed.**

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
