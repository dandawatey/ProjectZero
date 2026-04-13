# Command: /bootstrap-product

## Purpose
Main product creation entry point. Creates or configures a product repository for governed development.

## Trigger
User runs `/bootstrap-product` after successful `/factory-init`.

## Step-by-Step Process

### Step 1: Confirm Factory Initialized
Read `.claude/recovery/state.json`. Verify `initialized: true`. If not, direct user to run `/factory-init`.

### Step 2: Product Repository Decision
Ask user: "Create new product repository or use existing?"
- **New**: Ask for product name, GitHub org (optional)
- **Existing**: Ask for path to existing repository

### Step 3: Create or Validate Product Structure
**If new:**
- Create directory: `../<product-name>/`
- Run `git init`, set main as default branch
- Copy .claude/ directory from factory to product
- Create basic structure: src/, tests/, packages/, docs/

**If existing:**
- Validate git repository
- Check for existing .claude/ directory
- Add missing .claude/ files from factory template

### Step 4: Configure Integrations
Ask for each:
- **JIRA**: Project key, base URL (or skip)
- **Confluence**: Space key, base URL (or skip)
- **GitHub**: Org and repo name (or skip)
Update `.claude/integrations/config.json` with provided values.

### Step 5: Validate Environment
Check `.env` has integration credentials for enabled integrations. Warn for missing optional values.

### Step 6: Initialize Product State
Write product context to:
- `.claude/memory/org-context.md` (product name, team, constraints)
- `.claude/recovery/state.json` (product initialized)

### Step 7: Intake BMAD / PRD
Ask user to provide BMAD or PRD document (paste or file path).
If no BMAD, guide through BMAD creation using `.claude/core/bmad.md` template.

### Step 8: Parse BMAD
Use spec-miner skill to extract structured data:
- Business model canvas sections
- Target users and personas
- Technical constraints
- MVP scope
- Success metrics
Store in `.claude/memory/domain-memory.md`.

### Step 9: Create Module Candidates
From BMAD analysis, identify bounded business capabilities.
Create module candidates list with: name, purpose, estimated scope.
Store in `.claude/reports/current-state.md`.

### Step 10: Create Tracking Setup
Initialize queue files:
- `.claude/delivery/queue/ready.json` (empty)
- `.claude/delivery/queue/active.json` (empty)
Set up initial reports in `.claude/reports/`.

### Step 11: Validate Readiness
Run readiness-validator for specification phase:
- BMAD parsed? ✓
- Module candidates identified? ✓
- Integrations configured (or local fallback)? ✓
- Environment valid? ✓

### Step 12: Hand Off to /spec
Report readiness status. Instruct user to run `/spec`.

## Required Inputs
- Product name
- BMAD or PRD document
- Integration preferences (optional)

## Involved Agents
- spec-miner skill (BMAD parsing)
- readiness-validator (readiness check)
- integration-agent (if integrations configured)

## Outputs
- Product repository with .claude OS
- Parsed BMAD in memory
- Module candidates
- Tracking infrastructure initialized
- Readiness report

## Validation
Readiness-validator must pass before proceeding to /spec.

## Failure Handling
- Checkpoint state after each step
- If BMAD parsing fails, ask user to provide more detail
- If integration config fails, fall back to local-only mode
- Log failures to `.claude/recovery/failure-log.md`

## Next Command
/spec

---

## No PRD? No Problem.

If user says "I don't have a PRD" or "I just have an idea":

1. Run `/vision-to-prd` first
2. System asks 5-7 structured questions
3. Generates PRD + BMAD from answers
4. User reviews and approves
5. Continue bootstrap with generated docs

Flow: `/bootstrap-product` → detect no PRD → `/vision-to-prd` → resume `/bootstrap-product`
