# Command: /bootstrap-product

## Purpose
Create product repo with full integration wiring. Uses validated APIs to create real external resources.

## Prerequisite
`/factory-init` must pass. All integrations validated.

## Step-by-Step Process

### Step 1: Confirm Factory Ready
Verify integrations validated. If not → block, send to /factory-init.

### Step 2: Product Identity
Ask user:
- Product name
- Product description (1 sentence)
- GitHub repo name

### Step 3: Create GitHub Repo (via API)
```
POST https://api.github.com/orgs/{org}/repos
{
  "name": "product-name",
  "description": "...",
  "private": true,
  "auto_init": true
}
```
- Clone repo locally
- Copy .claude/templates/product-skeleton/ into repo
- Copy relevant factory templates
- Initial commit + push

### Step 4: Create JIRA Project (via API)
```
POST {JIRA_BASE_URL}/rest/api/3/project
{
  "key": "PROD",
  "name": "Product Name",
  "projectTypeKey": "software",
  "leadAccountId": "..."
}
```
- Verify project created
- Store JIRA_PROJECT_KEY in product .env

### Step 5: Create Confluence Space (via API)
```
POST {CONFLUENCE_BASE_URL}/rest/api/space
{
  "key": "PROD",
  "name": "Product Name",
  "description": {"plain": {"value": "..."}},
  "type": "global"
}
```
- Create project hub page structure from templates:
  - Overview
  - BMAD
  - Architecture
  - Modules
  - Delivery Tracker
  - Risks
  - Decisions
  - Release Notes
  - Operations

### Step 6: Configure Product .env
Write to product repo .env:
```
PRODUCT_NAME=product-name
JIRA_PROJECT_KEY=PROD
CONFLUENCE_SPACE_KEY=PROD
GITHUB_REPO=org/product-name
```
Copy required integration keys from factory .env.

### Step 7: Initialize Temporal
- Register product task queue
- Verify worker can connect

### Step 8: Detect PRD
Ask: "Do you have a PRD or BMAD document?"
- YES → load it, parse with spec-miner, store in product memory
- NO → route to /vision-to-prd

### Step 9: Validate Readiness
Run readiness-validator:
- [ ] GitHub repo exists and accessible
- [ ] JIRA project exists and writable
- [ ] Confluence space exists with hub pages
- [ ] Temporal connected
- [ ] Product .env complete
- [ ] BMAD/PRD loaded (or /vision-to-prd scheduled)

### Step 10: Report
```
Product Bootstrap Complete
═════════════════════════
GitHub:     org/product-name ✓
JIRA:       PROD ✓
Confluence: PROD ✓
Temporal:   connected ✓
PRD:        loaded ✓ (or: pending /vision-to-prd)

Next: /vision-to-prd (if no PRD) or /spec
```

## Tracking Guarantee
After bootstrap, all workflows will:
- Create JIRA tickets for every work item
- Update ticket status at every stage transition
- Write Confluence updates at phase boundaries
- Sync execution state to Postgres
- Attach artifacts to tickets and Confluence pages

## Required Inputs
- Product name
- PRD/BMAD (or vision text)

## Outputs
- GitHub repo (created via API)
- JIRA project (created via API)
- Confluence space with hub (created via API)
- Product .env configured
- Temporal task queue registered

## Failure Handling
- GitHub API fail → show error, retry, block
- JIRA API fail → show error, retry, block
- Confluence API fail → show error, retry, block
- All failures logged with correlation_id

## Next Command
/vision-to-prd (if no PRD) or /business-docs (discovery) or /spec
