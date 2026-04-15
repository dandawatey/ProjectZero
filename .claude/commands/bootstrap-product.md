# Command: /bootstrap-product

## Purpose
Create product repo with full integration wiring. Supports **greenfield** (create all) and **brownfield** (connect to existing resources).

## Prerequisite
`/factory-init` must pass. All required integrations validated.

## Mode Detection

At start, ask:

```
Project type?
  [1] Greenfield — create everything new
  [2] Brownfield — connect to existing codebase/integrations
```

Brownfield mode → each step becomes configurable: create, skip, or point to existing.

---

## Brownfield: Skip & Configure Rules

Each step supports three actions:

| Action | Meaning |
|--------|---------|
| `create` | Factory creates the resource (greenfield default) |
| `skip` | Step omitted entirely (no resource needed) |
| `existing:<value>` | Use existing resource — provide key/URL/path |

**Shorthand flags** (can be passed directly):
```
/bootstrap-product --brownfield
/bootstrap-product --brownfield --skip=github,confluence
/bootstrap-product --brownfield --github=org/existing-repo --jira=PROD --confluence=PROD
```

If `--brownfield` passed without step flags → interactive prompt per step.

---

## Step-by-Step Process

### Step 1: Confirm Factory Ready
Verify integrations validated. If not → block, send to /factory-init.

---

### Step 2: Product Identity
Ask user:
- Product name
- Product description (1 sentence)
- GitHub repo name (or existing repo path if brownfield)

---

### Step 3: Resolve PRODUCT_ROOT

**Standard layout — product repo lives alongside factory (default):**
```
<factory-parent>/
├── ProjectZeroFactory/   ← factory root (FACTORY_ROOT)
└── <product-name>/       ← PRODUCT_ROOT (created here by default)
```

`PRODUCT_ROOT` defaults to `$(dirname $FACTORY_ROOT)/<product-name>`.
Override with `--root=/custom/path` if a different location is needed.

This applies to both greenfield and brownfield. Always resolve and confirm `PRODUCT_ROOT` before any file operation.

---

### Step 4: GitHub Repo

**Greenfield:**
```
POST https://api.github.com/orgs/{org}/repos
{ "name": "product-name", "description": "...", "private": true, "auto_init": true }
```
- Clone into `$PRODUCT_ROOT` (sibling of factory)
- Copy `.claude/templates/product-skeleton/` into repo
- Copy relevant factory templates
- Initial commit + push

**Brownfield — existing:**
```
Existing GitHub repo? [org/repo-name]
```
- Clone into `$PRODUCT_ROOT` (sibling of factory, or `--root` override)
- Inject `.claude/` scaffold without overwriting existing files
- Commit as "chore: inject factory scaffold"

**Brownfield — skip:**
- `PRODUCT_ROOT` = `--root` value (must be existing git repo)
- Inject `.claude/` scaffold in-place

---

### Step 4: JIRA Project

**Greenfield:**
```
POST {JIRA_BASE_URL}/rest/api/3/project
{ "key": "PROD", "name": "Product Name", "projectTypeKey": "software", "leadAccountId": "..." }
```
- Verify project created
- Store JIRA_PROJECT_KEY in product .env

**Brownfield — existing:**
```
Existing JIRA project key? [e.g. PROD]
```
- Validate key exists via API
- Store in product .env

**Brownfield — skip:**
- Set `JIRA_ENABLED=false` in product .env
- Ticket tracking disabled for this product

---

### Step 5: Confluence Space

**Greenfield:**
```
POST {CONFLUENCE_BASE_URL}/rest/api/space
{ "key": "PROD", "name": "Product Name", ... }
```
- Create hub page structure from templates:
  - Overview, BMAD, Architecture, Modules, Delivery Tracker,
    Risks, Decisions, Release Notes, Operations

**Brownfield — existing:**
```
Existing Confluence space key? [e.g. PROD]
Root page ID for hub? (optional, creates under space root if blank)
```
- Validate space exists via API
- Inject missing hub pages (skip pages that already exist by title)
- Store CONFLUENCE_SPACE_KEY in product .env

**Brownfield — skip:**
- Set `CONFLUENCE_ENABLED=false` in product .env
- Doc sync disabled for this product

---

### Step 6: Configure Product .env

**Write location: `$PRODUCT_ROOT/.env` — always the target product git directory, never the factory root.**

`PRODUCT_ROOT` is resolved before this step:
- Greenfield → absolute path of freshly cloned repo (`git clone` destination)
- Brownfield `--github=org/repo` → absolute path after clone
- Brownfield `--root=./path` → `realpath` of provided path (must contain `.git/`)
- Brownfield `--skip=github` → `realpath` of current working directory

**Validation before write:**
- `$PRODUCT_ROOT` directory exists
- `$PRODUCT_ROOT/.git/` exists (is a git repo)
- `$PRODUCT_ROOT` is writable
- If brownfield: git remote URL matches `--github` value (if provided)
- `$PRODUCT_ROOT` != factory root (never overwrite factory .env)

Fail hard if any check fails. Never silently fall back to factory root.

Write to `$PRODUCT_ROOT/.env`:
```
PRODUCT_NAME=product-name
PROJECT_MODE=brownfield|greenfield
PRODUCT_ROOT=/absolute/path/to/product/repo
JIRA_PROJECT_KEY=PROD           # omit if JIRA skipped
CONFLUENCE_SPACE_KEY=PROD       # omit if Confluence skipped
GITHUB_REPO=org/product-name
JIRA_ENABLED=true|false
CONFLUENCE_ENABLED=true|false
```
Copy required integration keys from factory .env into `$PRODUCT_ROOT/.env`.
Append `$PRODUCT_ROOT/.env` to `$PRODUCT_ROOT/.gitignore` (create if absent).

---

### Step 7: Temporal

**Greenfield / Brownfield — register:**
- Register product task queue
- Verify worker can connect

**Brownfield — existing queue:**
```
Existing Temporal task queue name? [e.g. product-name-queue]
```
- Validate queue reachable
- Store TEMPORAL_TASK_QUEUE in product .env

**Brownfield — skip:**
- Set `TEMPORAL_ENABLED=false` in product .env
- Workflow orchestration disabled; manual execution mode

---

### Step 8: Detect PRD

Ask: "Do you have a PRD or BMAD document?"
- YES → load it, parse with spec-miner, store in product memory
- NO → route to /vision-to-prd

**Brownfield extra options:**
- Existing doc in repo? Provide path (e.g. `docs/PRD.md`)
- Confluence page URL? Factory fetches and parses it
- Legacy spec / wiki dump? Paste or provide file path

---

### Step 9: Brownfield Codebase Audit (brownfield only)

When mode = brownfield, run codebase discovery:
```
Scanning existing codebase...
```
- Detect language / framework / package manager
- Detect existing test framework and coverage baseline
- Detect existing CI/CD config (.github/workflows, Jenkinsfile, etc.)
- Detect existing env config patterns
- Write findings to product memory as `brownfield-audit.md`

Report:
```
Codebase Audit
══════════════
Language:    TypeScript / Node 20
Framework:   Next.js 14
Tests:       Jest — baseline coverage 42% (below 80% threshold)
CI/CD:       GitHub Actions (2 workflows detected)
Env config:  .env.local pattern
```

Flag coverage gap → create ticket PRJ0-001: "Raise coverage to 80%"

---

### Step 10: Design System Init

Run `/design-system-init` automatically for every new product.

**What it sets up:**
- `src/design-system/tokens.ts` — color palette, typography scale, spacing, shadows, z-index
- `src/design-system/motion.ts` — Framer Motion variants (fadeIn, fadeUp, scaleIn, stagger, drawer, etc.)
- `src/design-system/components/` — Button, Input, Card, Badge, Spinner, Avatar with Storybook stories
- `src/design-system/index.ts` — barrel export
- `.storybook/main.ts` + `.storybook/preview.tsx` — Storybook configured for framework
- `package.json` updated with `storybook`, `storybook:build`, `storybook:test` scripts

**Packages installed:**
```
framer-motion  clsx  class-variance-authority
@storybook/nextjs (or react-vite / vue3-vite)
@storybook/addon-docs  @storybook/addon-a11y  @storybook/addon-themes
```

**Skippable:**
```
--skip=design-system      # skip entirely (no UI framework needed)
--skip=storybook          # tokens + motion only, no Storybook
--skip=framer             # CSS transitions only
```

**Brownfield:** if `src/design-system/` already exists → inject only missing files, never overwrite.

Validate: `{pm} run storybook:build` must exit 0 before proceeding.

---

### Step 11: Validate Readiness
Run readiness-validator:
- [ ] GitHub repo exists and accessible
- [ ] JIRA project exists and writable (or explicitly skipped)
- [ ] Confluence space exists (or explicitly skipped)
- [ ] Temporal connected (or explicitly skipped)
- [ ] Product .env complete
- [ ] BMAD/PRD loaded (or /vision-to-prd scheduled)
- [ ] Brownfield audit complete (brownfield only)
- [ ] Design system initialized (or explicitly skipped)
- [ ] Storybook build passes (or --skip=storybook)

---

### Step 12: Open Alongside Factory (Always)

After every successful bootstrap, without exception:

1. Update `<parent-dir>/<parent-dir-name>.code-workspace` — add new product folder
2. Run `code --add $PRODUCT_ROOT` — injects folder into the **currently open** VS Code window, no restart
3. Factory and all products always visible together in one window

Workspace file is named after the parent directory (e.g. `i-ProjectZero/i-projectzero.code-workspace`).
Each new product appended — never removed. Workspace accumulates the full portfolio.

Fallback (no `code` CLI): `open -a "Visual Studio Code" <workspace-file>`
Install CLI: VS Code → Cmd+Shift+P → "Shell Command: Install code in PATH"

---

### Step 13: Report

```
Product Bootstrap Complete
══════════════════════════
Mode:           brownfield
GitHub:         org/existing-repo ✓ (existing)
JIRA:           PROD ✓ (existing)
Confluence:     skipped
Temporal:       product-queue ✓ (existing)
PRD:            docs/PRD.md ✓ (parsed)
Coverage:       42% → ticket PRJ0-001 created
Design system:  ✓ tokens · motion · 6 components · Storybook
Storybook:      ✓ build passing  →  pnpm storybook (port 6006)

Next: /spec (backlog from PRD) or /arch (existing system audit)
```

---

## Skip Reference

| Flag | Skips |
|------|-------|
| `--skip=github` | No repo creation; use cwd |
| `--skip=jira` | No JIRA; sets JIRA_ENABLED=false |
| `--skip=confluence` | No Confluence; sets CONFLUENCE_ENABLED=false |
| `--skip=temporal` | No Temporal; sets TEMPORAL_ENABLED=false |
| `--skip=prd` | Skip PRD step; go straight to /spec manually |
| `--skip=design-system` | Skip design system init entirely |
| `--skip=storybook` | Tokens + motion only; no Storybook install |
| `--skip=framer` | No Framer Motion; use CSS transitions |
| `--skip=all-integrations` | Skip steps 3–7; configure manually post-bootstrap |

Combine: `--skip=jira,confluence,temporal`

---

## Path Configuration Reference

| Flag | Purpose |
|------|---------|
| `--github=org/repo` | Use existing GitHub repo |
| `--jira=KEY` | Use existing JIRA project key |
| `--confluence=KEY` | Use existing Confluence space key |
| `--temporal-queue=name` | Use existing Temporal task queue |
| `--prd=path/to/file.md` | Load PRD from local file |
| `--prd-url=https://...` | Load PRD from Confluence/URL |
| `--root=./path` | Product root directory (default: cwd) |

---

## Required Inputs
- Product name
- PRD/BMAD (or vision text) — or `--skip=prd`

## Outputs
- GitHub repo (created or linked)
- JIRA project (created, linked, or skipped)
- Confluence space (created, linked, or skipped)
- Product .env configured
- Temporal task queue (registered, linked, or skipped)
- Brownfield audit report (brownfield only)

## Failure Handling
- GitHub API fail → show error, retry, block
- JIRA API fail → show error, retry, offer `--skip=jira`
- Confluence API fail → show error, retry, offer `--skip=confluence`
- All failures logged with correlation_id
- Brownfield: non-blocking failures (audit partial) → warn, continue

## Next Command
/vision-to-prd (no PRD) → /spec → /arch
Brownfield with existing arch: jump directly to /spec or /implement
