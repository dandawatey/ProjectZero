# 02 - How to Start a New Product

## Prerequisites

Before starting, ensure you have:

1. **Claude Code CLI** installed and authenticated
2. **Git** installed and configured
3. **Node.js 18+** (for Storybook and frontend tooling)
4. **Python 3.11+** (for FastAPI workers and Dagster pipelines, if using pipeline mode)
5. Access to the **ProjectZeroFactory** template repository
6. (Optional) JIRA, Confluence, and GitHub credentials
7. (Optional) Redis and PostgreSQL for pipeline mode

## Step 1: Clone the Factory

```bash
git clone https://github.com/your-org/ProjectZeroFactory.git MyProduct
cd MyProduct
```

This gives you the full factory template. The `.claude/` directory contains the entire operating system, but it is not yet configured for your specific product.

## Step 2: Run /factory-init

Open Claude Code in the cloned directory and run:

```
/factory-init
```

This command:
1. Validates that the `.claude/` directory structure is intact
2. Creates a fresh `.env` from `.env.example`
3. Initializes empty memory, recovery, and learning stores
4. Sets the factory version in `.claude/core/`
5. Creates the local delivery queue structure
6. Runs the repo-validator agent to confirm readiness

**Expected output:**
```
Factory initialized successfully.
Factory version: 1.0.0
Directory structure: VALID
Memory store: INITIALIZED
Recovery store: INITIALIZED
Delivery queue: INITIALIZED
Status: READY for /bootstrap-product
```

**If it fails:** Check that the `.claude/` directory was not corrupted during cloning. The most common issue is missing subdirectories. Run `ls -la .claude/` and compare against the expected structure in [01-how-projectzerofactory-works.md](01-how-projectzerofactory-works.md).

## Step 3: Run /bootstrap-product

```
/bootstrap-product --name "MyProduct" --type saas --stack "nextjs,fastapi,postgresql"
```

Parameters:
- `--name`: Product name (used in JIRA, Confluence, package.json)
- `--type`: Product type (`saas`, `internal-tool`, `platform`, `mobile`, `api`)
- `--stack`: Comma-separated technology stack

This command:
1. Sets `PRODUCT_NAME` in `.env`
2. Creates product-specific directories in the source tree
3. Initializes `package.json` and/or `pyproject.toml` based on the stack
4. Creates the initial module structure in `.claude/modules/`
5. Sets up the design system skeleton in `.claude/design-system/` (if frontend stack)
6. Configures agents for the chosen stack (e.g., enables frontend-engineer for Next.js)
7. Creates the initial `.claude/knowledge/product-context.md` file
8. Initializes git with an initial commit

**Expected output:**
```
Product bootstrapped: MyProduct
Type: saas
Stack: nextjs, fastapi, postgresql
Modules initialized: 0 (ready for BMAD)
Design system: INITIALIZED
Git: Initial commit created
Status: READY for integration configuration
```

## Step 4: Configure Integrations

### 4a: JIRA Configuration

Edit `.env` with your JIRA credentials:

```env
JIRA_BASE_URL=https://your-org.atlassian.net
JIRA_API_TOKEN=your-api-token
JIRA_USER_EMAIL=you@your-org.com
JIRA_PROJECT_KEY=MYP
JIRA_BOARD_ID=123
```

Then run:
```
/setup jira
```

This validates the connection, confirms the project exists, and syncs the initial board state to `product repo .claude/delivery/jira/state/`.

### 4b: Confluence Configuration

```env
CONFLUENCE_BASE_URL=https://your-org.atlassian.net/wiki
CONFLUENCE_API_TOKEN=your-api-token
CONFLUENCE_SPACE_KEY=MYP
```

Then run:
```
/setup confluence
```

This creates the Confluence project hub with the standard page hierarchy:
- Product Overview
- Architecture Decisions
- Module Documentation
- Sprint Reports
- Risk Register
- Decision Log
- Release Notes

### 4c: GitHub Configuration

```env
GITHUB_TOKEN=your-github-token
GITHUB_ORG=your-org
GITHUB_DEFAULT_BRANCH=main
```

Then run:
```
/setup github
```

This configures branch naming conventions, PR templates, and webhook settings.

### 4d: Skip Integrations (Local-Only Mode)

If you do not have JIRA/Confluence/GitHub access, ensure:

```env
ENABLE_LOCAL_FALLBACK=true
```

The factory will use local file representations for all integration points. You can configure integrations later and the reconciliation system will sync.

## Step 5: Load the BMAD

The BMAD (Business Model Architecture Document) is the foundation document that defines what you are building and why. Create it or load an existing one:

### Option A: Create from scratch

```
/spec --type bmad
```

The product-manager agent will guide you through a structured interview covering:
- Business context and problem statement
- Target users and personas
- Value proposition
- Revenue model
- Technical constraints
- Success metrics (KPIs)
- Non-functional requirements (performance, security, compliance)
- Competitive landscape

The output is saved to `.claude/knowledge/bmad.md`.

### Option B: Load existing BMAD

If you already have a BMAD or PRD document:

```
/spec --type bmad --input path/to/your/bmad.md
```

The product-manager agent will parse it, validate completeness, and store it in the standard format.

## Step 6: Load the PRD (Optional but Recommended)

If you have a separate Product Requirements Document:

```
/spec --type prd --input path/to/your/prd.md
```

The PRD supplements the BMAD with detailed feature requirements, user stories, and acceptance criteria.

## Step 7: Validate Readiness

Run the readiness check:

```
/setup validate
```

This runs the readiness-validator agent, which checks:

| Check | Required | Status |
|---|---|---|
| `.claude/` structure intact | Yes | |
| `.env` configured | Yes | |
| Product name set | Yes | |
| Stack defined | Yes | |
| BMAD loaded | Yes | |
| JIRA connected | No (local fallback) | |
| Confluence connected | No (local fallback) | |
| GitHub connected | No (local fallback) | |
| Memory store accessible | Yes | |
| Recovery store accessible | Yes | |
| Design system initialized | If frontend | |

**Expected output:**
```
Readiness validation: PASSED
  Required checks: 6/6 PASSED
  Optional checks: 3/3 PASSED (or SKIPPED with fallback)
  Status: READY to begin /spec
```

## Step 8: Begin Specification

You are now ready to start building. Run:

```
/spec
```

This enters the **Specification** stage of SPARC. The product-manager agent will:
1. Read the BMAD and PRD
2. Decompose the product into modules (bounded contexts)
3. Define epics for each module
4. Break epics into user stories with acceptance criteria
5. Create JIRA epics and stories (or local equivalents)
6. Produce the specification document

See [05-stage-by-stage-workflow.md](05-stage-by-stage-workflow.md) for detailed stage documentation.

## Quick-Start Checklist

For the impatient, here is the minimum path to start building:

```bash
# 1. Clone
git clone https://github.com/your-org/ProjectZeroFactory.git MyProduct
cd MyProduct

# 2. Open Claude Code and run:
/factory-init
/bootstrap-product --name "MyProduct" --type saas --stack "nextjs,fastapi,postgresql"
/spec --type bmad
# (answer the BMAD interview questions)
/setup validate
/spec
```

Total time from clone to first specification: approximately 30-45 minutes, depending on the complexity of your BMAD.

## Common Issues

### "Factory structure invalid"
The `.claude/` directory is missing subdirectories. Re-clone from the template.

### "BMAD not found"
You skipped Step 5. The factory requires a BMAD before any development work can begin.

### "Integration connection failed"
Check your `.env` credentials. Ensure `ENABLE_LOCAL_FALLBACK=true` if you want to work offline.

### "Stack not recognized"
Supported stacks: `nextjs`, `react`, `vue`, `angular`, `fastapi`, `django`, `express`, `nestjs`, `postgresql`, `mongodb`, `redis`, `elasticsearch`. Combine with commas.

### "Module structure empty"
This is normal after bootstrap. Modules are created during the `/spec` stage based on your BMAD.
