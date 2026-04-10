# 01 - How ProjectZeroFactory Works

## Architecture Overview

ProjectZeroFactory is structured as an operating system that lives inside a `.claude/` directory. The entire system is composed of five layers:

```
Layer 5: Commands (user-facing entry points)
Layer 4: Workflows (multi-step orchestrations)
Layer 3: Agents (specialized roles with defined scopes)
Layer 2: Skills (reusable capabilities any agent can invoke)
Layer 1: Core (memory, recovery, governance rules, contracts)
```

## The .claude/ Directory as Operating System

The `.claude/` directory is the kernel of the factory. Here is the complete directory structure and what each part does:

```
.claude/
  agents/            # Agent definitions (role, scope, inputs, outputs)
  analytics/         # Usage and performance tracking data
  checklists/        # Pre-flight and post-flight checklists for stages
  commands/          # Slash command definitions (the user interface)
  contracts/         # Inter-agent contracts (what agent A expects from agent B)
  core/              # Core governance rules, system prompts, configuration
  data/
    fixtures/        # Test fixtures and seed data
    synthetic-data/  # Generated test data for development
  definition-of-done/  # DoD criteria per artifact type
  delivery/
    confluence/      # Confluence sync state and payloads
      logs/          # Sync operation logs
      mappings/      # Local-to-Confluence ID mappings
      pages/         # Cached page content
      payloads/      # Queued API payloads
      sync_queue/    # Pending sync operations
    epics/           # Epic definitions and tracking
    features/        # Feature definitions and tracking
    github/          # GitHub sync state
      branches/      # Branch metadata
      logs/          # Sync operation logs
      repos/         # Repository configuration
      state/         # Current sync state
    jira/            # JIRA sync state
      issues/        # Cached issue data
      logs/          # Sync operation logs
      mappings/      # Local-to-JIRA ID mappings
      payloads/      # Queued API payloads
      state/         # Current sync state
      sync_queue/    # Pending sync operations
    queue/           # Work queue (ready, active, completed, failed, blocked)
    reconciliation/  # Reconciliation logs for integration drift
  design-system/     # Design tokens, component registry
  devops/            # Infrastructure and deployment configuration
  embeddings/        # Vector embeddings for semantic search
  feature-flags/     # Feature flag definitions per product
  finops/            # Cost tracking and optimization data
  guardrails/        # Safety and compliance rules
  integrations/      # Integration configuration and adapters
  knowledge/         # Product-specific knowledge base
  learning/          # Learning entries promoted from sessions
  memory/            # Persistent memory across sessions
  memory_store/      # Indexed memory for fast retrieval
  modules/           # Module definitions (bounded contexts)
  operations/        # Operational runbooks and incident data
  pipelines/         # Pipeline definitions for Dagster
  portfolio/         # Multi-product portfolio tracking
  recovery/          # Checkpoints and recovery state
  reports/           # Generated reports (velocity, quality, etc.)
  runtime/           # Runtime state for workers and orchestration
  skills/            # Skill definitions (reusable capabilities)
    code-reviewer/
    debug-skill/
    design-sprint/
    feature-forge/
    frontend-design/
    hooked-ux/
    ios-hig-design/
    playwright-skill/
    rag-architect/
    refactoring-ui/
    secure-code-guardian/
    spec-miner/
    superpowers/
    the-fool/
    ui-ux-pro-max/
    using-git-worktrees/
    ux-heuristics/
  sre/               # SRE runbooks and monitoring configuration
  templates/         # Templates for all artifact types
  workflows/         # Multi-step workflow definitions
```

## Factory Repo vs. Product Repo

There are two distinct concepts:

### Factory Repo (Template)

The **ProjectZeroFactory** repository is the template. It contains:
- All agent definitions
- All command definitions
- All skill definitions
- All workflow definitions
- Core governance rules
- Empty delivery, memory, and recovery directories (ready to be populated)
- Documentation (this file)

The factory repo is maintained by the Center of Excellence. It is versioned. Products track which factory version they were created from.

### Product Repo (Instance)

When you run `/factory-init` followed by `/bootstrap-product`, the factory creates a **product instance**. This is a new repository that contains:
- A copy of `.claude/` from the factory (customized for the product)
- The product's source code (generated through the SPARC workflow)
- Product-specific memory, learning, and recovery data
- Product-specific JIRA/Confluence/GitHub configuration

The product repo diverges from the factory over time. Factory upgrades can be pulled in selectively.

### Relationship Diagram

```
ProjectZeroFactory (template)
  |
  |-- clone + /factory-init + /bootstrap-product
  |
  +-- ProductA/.claude/  (instance, customized)
  |     +-- source code
  |     +-- product-specific memory
  |     +-- product-specific integrations
  |
  +-- ProductB/.claude/  (instance, customized)
  |     +-- source code
  |     +-- product-specific memory
  |     +-- product-specific integrations
  |
  +-- ProductC/.claude/  (instance, customized)
        +-- source code
        +-- product-specific memory
        +-- product-specific integrations
```

## How Commands, Agents, Skills, and Workflows Compose

### Commands

Commands are the user interface. They are defined in `.claude/commands/` and invoked with a slash prefix (e.g., `/spec`, `/implement`, `/review`). A command:
1. Accepts user input (parameters, context)
2. Activates one or more workflows
3. Returns results to the user

### Workflows

Workflows are multi-step orchestrations. They are defined in `.claude/workflows/` and are typically triggered by commands. A workflow:
1. Determines which agents to involve
2. Sequences the agent invocations
3. Manages handoffs between agents
4. Enforces governance gates (checker, reviewer, approver)
5. Tracks progress and enables recovery

### Agents

Agents are specialized roles. They are defined in `.claude/agents/` and are invoked by workflows. Each agent:
1. Has a defined role, scope, and expertise
2. Receives structured inputs (per its contract)
3. Produces structured outputs (per its contract)
4. Operates within guardrails
5. Can invoke skills as needed

### Skills

Skills are reusable capabilities. They are defined in `.claude/skills/` and can be invoked by any agent. A skill:
1. Provides a specific capability (debugging, code review, UI analysis)
2. Is stateless -- it takes input and produces output
3. Can be composed into any workflow through agent invocation

### Composition Example

When a user runs `/implement PROJ-42`:

```
/implement (command)
  --> implementation-workflow (workflow)
    --> product-manager: retrieves spec for PROJ-42
    --> architect: retrieves architecture decisions
    --> backend-engineer: implements the feature (invokes feature-forge skill)
    --> qa-engineer: writes tests (invokes playwright-skill if UI)
    --> checker: validates against spec
    --> security-reviewer: scans for vulnerabilities (invokes secure-code-guardian skill)
    --> reviewer: full quality review (invokes code-reviewer skill)
    --> approver: final sign-off
    --> release-manager: prepares PR and release notes
```

## Configuration

Product-level configuration is managed through:

1. **`.env`** - Integration credentials and runtime settings (never committed)
2. **`.env.example`** - Template showing all available configuration
3. **`.claude/core/`** - Core governance configuration
4. **`.claude/integrations/`** - Integration-specific configuration
5. **`.claude/feature-flags/`** - Feature flags for the factory itself

Key environment variables:

| Variable | Purpose |
|---|---|
| `JIRA_BASE_URL` | Atlassian instance URL |
| `JIRA_PROJECT_KEY` | JIRA project key for this product |
| `CONFLUENCE_SPACE_KEY` | Confluence space for documentation |
| `GITHUB_ORG` | GitHub organization |
| `REDIS_URL` | Redis for queue and cache |
| `DATABASE_URL` | PostgreSQL for persistent storage |
| `DAGSTER_HOME` | Dagster orchestration home directory |
| `ENABLE_LOCAL_FALLBACK` | Use local files when integrations unavailable |
| `ENABLE_MEMORY_PERSISTENCE` | Persist memory between sessions |

## Data Flow

```
User Input
  |
  v
Command (parse + validate)
  |
  v
Workflow (orchestrate)
  |
  v
Agent(s) (execute)          <--> Skills (capabilities)
  |                          <--> Memory (context)
  |                          <--> Integrations (JIRA/Confluence/GitHub)
  v
Artifacts (specs, code, tests, PRs)
  |
  v
Governance Chain (check -> review -> approve)
  |
  v
Delivery (queue -> deploy -> monitor)
  |
  v
Recovery Checkpoint (saved state)
  |
  v
Learning (patterns captured and promoted)
```

## Offline Mode

When `ENABLE_LOCAL_FALLBACK=true` (the default), the factory operates without any external integrations:

- JIRA tickets are represented as JSON files in `.claude/delivery/jira/issues/`
- Confluence pages are represented as Markdown files in `.claude/delivery/confluence/pages/`
- GitHub operations are performed directly on the local git repository
- Queue state is managed in `.claude/delivery/queue/` as JSON files

When integrations become available, the reconciliation system in `.claude/delivery/reconciliation/` syncs local state to external systems.
