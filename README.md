# ProjectZeroFactory

**The org-wide Claude operating system for governed product development.**

ProjectZeroFactory is the canonical source of truth for how your organization builds software products with AI assistance. It is not a framework or a library -- it is an operating model. Every product your teams build starts here, inherits its governance rules from here, and reports its learning back here.

---

## Table of Contents

- [Why ProjectZeroFactory Exists](#why-projectzerofactory-exists)
- [Who Should Use This](#who-should-use-this)
- [Problems It Solves](#problems-it-solves)
- [The Clone-First Operating Model](#the-clone-first-operating-model)
- [Prerequisites](#prerequisites)
- [Quick Start: Creating a New Product](#quick-start-creating-a-new-product)
- [Command Flow](#command-flow)
- [Governance Rules](#governance-rules)
- [Stage Model](#stage-model)
- [Learning Model](#learning-model)
- [Recovery Model](#recovery-model)
- [Troubleshooting](#troubleshooting)
- [Example: End-to-End Flow](#example-end-to-end-flow)

---

## Why ProjectZeroFactory Exists

Organizations building multiple products with AI-assisted development face a compounding problem: each team invents its own workflow, its own quality gates, its own definition of "done." The result is fragmentation -- inconsistent quality, no knowledge reuse, no governance, and no way to measure what "good" looks like across the portfolio.

ProjectZeroFactory exists to solve this by providing a single, governed operating system that every product inherits from. When a team starts a new product, they do not start from scratch. They clone this factory, run the bootstrap script, and immediately inherit:

- A governed stage model (Specification, Architecture, Realization, Completion)
- A complete command flow from init to release
- Quality gates enforced by policy, not by memory
- A learning system that captures what works and feeds it back to the factory
- Recovery mechanisms that prevent silent failures

This is not optional tooling. This is the way products are built.

## Who Should Use This

- **Any team starting a new product** within the organization
- **Tech leads** setting up a new project repo
- **Product managers** who want governed, traceable development
- **Platform engineers** maintaining the factory itself
- **Individual developers** who want to understand the rules they are operating under

If you are building a product in this organization, you start here.

## Problems It Solves

| Problem | How the Factory Solves It |
|---------|--------------------------|
| **Fragmented development** | Every product inherits the same stage model, commands, and governance rules |
| **No governance** | Maker-Checker-Reviewer-Approver flow is enforced, not suggested |
| **No reuse** | Learning model captures patterns and promotes them back to the factory |
| **Silent failures** | Truthful completion policy -- no fake done, no placeholder code, no skipped tests |
| **No traceability** | No Ticket No Work -- every change maps to a tracked work item |
| **Inconsistent quality** | TDD required, minimum 80% test coverage enforced |
| **Lost context** | Memory system persists decisions, blockers, and learnings across sessions |
| **No recovery** | Checkpoint system allows resumption from last known good state |

## The Clone-First Operating Model

ProjectZeroFactory operates on a **clone-first** model. This means:

1. The factory repo is the **source of truth** for all governance, commands, and operating rules.
2. When you create a new product, you do not copy files manually. You run the bootstrap script, which clones the relevant factory configuration into your product repo.
3. Your product repo contains a `.claude/` directory that inherits from the factory. Product-specific overrides are allowed, but factory rules cannot be weakened -- only extended.
4. When the factory is updated (new governance rules, improved commands, better learning), products can pull those updates.
5. Learnings from individual products are promoted back to the factory through an approval process.

This creates a two-way flow: governance flows down from factory to product, and learnings flow up from product to factory.

## Prerequisites

Before using ProjectZeroFactory, ensure you have the following installed:

| Tool | Version | Required | Purpose |
|------|---------|----------|---------|
| **Git** | 2.30+ | Yes | Version control, factory clone |
| **Node.js** | 18+ | Yes | Runtime for tooling and scripts |
| **Claude Code CLI** | Latest | Yes | AI-assisted development agent |
| **VS Code** | Latest | Yes | Primary IDE with Claude Code extension |
| **Bash** | 4.0+ | Yes | Script execution |
| **JIRA** | Cloud | Optional | Work item tracking (No Ticket No Work) |
| **Confluence** | Cloud | Optional | Documentation hub |

### Verifying Your Setup

```bash
git --version          # Should be 2.30+
node --version         # Should be 18+
claude --version       # Claude Code CLI installed
code --version         # VS Code installed
bash --version         # Should be 4.0+
```

## Quick Start: Creating a New Product

### Step 1: Clone the Factory

```bash
git clone git@github.com:your-org/ProjectZeroFactory.git
cd ProjectZeroFactory
```

### Step 2: Configure Environment

```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

At minimum, set these values in `.env`:
- `ANTHROPIC_API_KEY` -- your Anthropic API key
- `GITHUB_TOKEN` -- a GitHub personal access token with repo scope
- `GITHUB_ORG` -- your GitHub organization name

### Step 3: Bootstrap a New Product

```bash
bash scripts/bootstrap-product.sh
```

The script will prompt you for:
- **Product name** (e.g., `customer-portal`)
- **Product directory** (defaults to `../ProductName`)

It will then:
1. Create the product directory
2. Initialize a git repository
3. Copy the `.claude/` governance template
4. Validate your environment
5. Print next steps

### Step 4: Enter the Product and Start Working

```bash
cd ../customer-portal
claude
```

Once inside Claude Code, the governed command flow begins.

## Command Flow

Every product follows this command sequence. Commands must be executed in order -- you cannot skip stages.

| Order | Command | Stage | What It Does |
|-------|---------|-------|-------------|
| 1 | `/factory-init` | Setup | Validates factory connection, loads governance rules, checks environment |
| 2 | `/bootstrap-product` | Setup | Creates product structure, initializes repo, copies templates |
| 3 | `/spec` | Specification | Generates product requirements from PRD, creates user stories, maps to JIRA tickets |
| 4 | `/arch` | Architecture | Produces system architecture, component diagrams, tech stack decisions, ADRs |
| 5 | `/implement` | Realization | Executes implementation tickets one at a time, TDD-first, with maker-checker |
| 6 | `/check` | Realization | Runs quality gates: tests pass, coverage meets threshold, no lint errors, no type errors |
| 7 | `/review` | Completion | Creates PR, runs automated review, flags issues, requests human review |
| 8 | `/approve` | Completion | Final approval gate -- human confirms, merge proceeds |
| 9 | `/release` | Completion | Tags release, updates changelog, notifies stakeholders, captures learnings |

### Command Dependencies

```
/factory-init
    |
    v
/bootstrap-product
    |
    v
/spec  ---------> /arch
                    |
                    v
              /implement  <--+
                    |        |
                    v        |
                /check ------+  (loop until passing)
                    |
                    v
                /review
                    |
                    v
                /approve
                    |
                    v
                /release
```

## Governance Rules

ProjectZeroFactory enforces four governance frameworks. These are non-negotiable.

### 1. BMAD (Business, Market, Architecture, Delivery)

Every product must address all four dimensions before code is written:
- **Business**: What problem does this solve? Who pays for it?
- **Market**: Who are the users? What alternatives exist?
- **Architecture**: What is the system design? What are the constraints?
- **Delivery**: What is the plan? What are the milestones?

### 2. SPARC (Specification, Pseudocode, Architecture, Refinement, Completion)

The development process follows SPARC stages:
- **Specification**: Requirements are written, reviewed, and approved before any code
- **Pseudocode**: High-level logic is designed before implementation
- **Architecture**: System design is finalized and documented
- **Refinement**: Implementation is iterative with continuous quality checks
- **Completion**: Work is verified, reviewed, and released

### 3. TDD (Test-Driven Development)

All implementation follows TDD:
1. Write a failing test
2. Write the minimum code to make it pass
3. Refactor
4. Repeat

Minimum test coverage: **80%**. No exceptions. No skipping tests to meet deadlines.

### 4. No Ticket No Work

Every piece of work must be traced to a ticket:
- No code changes without a corresponding JIRA ticket (or equivalent)
- Commit messages must reference ticket IDs
- PRs must link to tickets
- Untracked work is flagged and blocked

### Maker-Checker-Reviewer-Approver

Every significant change passes through four hands:
1. **Maker**: Creates the implementation
2. **Checker**: Verifies correctness (automated tests, linting, type checks)
3. **Reviewer**: Reviews for quality, design, and adherence to standards
4. **Approver**: Final human approval before merge

## Stage Model

Products move through four stages. Each stage has entry criteria and exit criteria.

### Specification
- **Entry**: Product brief exists, team is assigned
- **Activities**: Requirements gathering, user story creation, acceptance criteria definition
- **Exit**: All stories have acceptance criteria, stories are estimated, backlog is prioritized

### Architecture
- **Entry**: Specification stage is complete
- **Activities**: System design, technology selection, API design, data modeling, ADR creation
- **Exit**: Architecture document is approved, all ADRs are recorded, tech stack is finalized

### Realization
- **Entry**: Architecture stage is complete
- **Activities**: TDD implementation, continuous integration, quality gate checks
- **Exit**: All tickets implemented, all tests pass, coverage >= 80%, zero critical issues

### Completion
- **Entry**: Realization stage is complete
- **Activities**: Final review, approval, release tagging, changelog update, learning capture
- **Exit**: Release is tagged, stakeholders are notified, learnings are recorded

## Learning Model

ProjectZeroFactory includes a built-in learning system that improves over time.

### How It Works

1. **Read Before Act**: Before starting any task, Claude reads relevant memory and past learnings
2. **Write After Act**: After completing a task, Claude records what happened -- decisions made, blockers encountered, patterns discovered
3. **Promote Through Approval**: Learnings from individual products are reviewed and, if valuable, promoted to the factory level so all future products benefit

### Learning Storage

- **Product-level memory**: Stored in the product's `.claude/memory/` directory
- **Factory-level knowledge**: Stored in the factory's `.claude/knowledge/` directory
- **Promotion**: Product learnings are promoted to factory knowledge through a review process

### What Gets Captured

- Architecture decisions and their rationale
- Blockers encountered and how they were resolved
- Patterns that proved effective (or ineffective)
- Integration gotchas and workarounds
- Performance findings and optimizations

## Recovery Model

Things go wrong. The factory is designed to recover gracefully.

### Checkpoints

The factory creates checkpoints at stage boundaries and at significant milestones within stages. If a process fails, it can resume from the last checkpoint rather than starting over.

### Recovery Scenarios

| Scenario | Recovery Action |
|----------|----------------|
| **Claude session interrupted** | Resume from last checkpoint; memory provides context |
| **Test suite fails** | Identify failing tests, fix, re-run `/check` |
| **Build breaks** | Rollback to last green commit, diagnose, fix forward |
| **Governance violation detected** | Block merge, notify team, require remediation |
| **Environment misconfigured** | Run `scripts/validate-env.sh` to diagnose |

### Auto-Resume

When `recovery.autoResume` is enabled (default), the factory will attempt to resume interrupted work automatically. It reads the last checkpoint, restores context from memory, and continues from where it left off. Maximum retry attempts: 3.

## Troubleshooting

### "Factory not initialized"

You have not run `/factory-init` yet. This must be the first command in any product session.

```bash
claude
# Then inside Claude Code:
/factory-init
```

### "Environment validation failed"

Your `.env` file is missing required keys. Run the validation script:

```bash
bash scripts/validate-env.sh
```

It will tell you exactly which keys are missing or empty.

### "No ticket linked"

You attempted to make a change without a linked ticket. Create a ticket first, then reference it in your work.

### "Test coverage below threshold"

Your test coverage is below 80%. Write more tests. The `/check` command will tell you which files need coverage.

### "Checkpoint not found"

The recovery system could not find a valid checkpoint. This usually means the product was not properly bootstrapped. Re-run:

```bash
bash scripts/bootstrap-product.sh
```

### "Permission denied on scripts"

Make the scripts executable:

```bash
chmod +x scripts/*.sh
```

### Claude Code CLI not responding

Ensure your `ANTHROPIC_API_KEY` is set correctly in `.env` and that you have network connectivity.

### JIRA/Confluence integration not working

1. Verify your tokens in `.env`
2. Ensure the URLs do not have trailing slashes
3. Test connectivity: `curl -s -o /dev/null -w "%{http_code}" $JIRA_BASE_URL`

## Example: End-to-End Flow

Here is a complete example of creating a new product called "customer-portal" from scratch.

```bash
# 1. Clone the factory
git clone git@github.com:your-org/ProjectZeroFactory.git
cd ProjectZeroFactory

# 2. Set up environment
cp .env.example .env
vim .env  # Add your API keys

# 3. Bootstrap the product
bash scripts/bootstrap-product.sh
# Enter: customer-portal
# Accept default directory: ../customer-portal

# 4. Enter the product
cd ../customer-portal

# 5. Start Claude Code
claude

# 6. Inside Claude Code, run the governed flow:
/factory-init          # Validates factory, loads rules
/spec                  # Generates requirements from PRD
/arch                  # Produces architecture
/implement             # TDD implementation of first ticket
/check                 # Quality gates
/review                # PR creation and review
/approve               # Final approval
/release               # Tag and release
```

After `/release`, the factory captures learnings from the product and stores them for future use. The next product you build will benefit from what this one taught the system.

---

## Contributing to the Factory

The factory itself follows the same governance rules it enforces. To modify governance rules, commands, or operating policies:

1. Create a ticket describing the change
2. Create a branch from `main`
3. Make your changes
4. Ensure all existing products are not broken by the change
5. Submit a PR with the Maker-Checker-Reviewer-Approver flow
6. Once merged, notify all product teams of the update

---

## License

Internal use only. This factory and all derived products are proprietary to the organization.
