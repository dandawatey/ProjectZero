# Product Skeleton

This directory contains the template structure that `/bootstrap-product` copies into a new product repository.

## What Gets Created in the Product Repo

```
<product-repo>/
  .claude/
    delivery/
      queue/          — Work item queues (ready, active, blocked, completed, failed)
      reconciliation/ — Sync conflict tracking
      jira/           — JIRA sync state (issues, payloads, mappings, logs)
      confluence/     — Confluence sync state (pages, payloads, mappings, logs)
      github/         — GitHub sync state (repos, branches, logs)
      features/       — Feature tracking
      epics/          — Epic tracking
    reports/          — Product reports (progress, queue status, agent status, etc.)
    recovery/         — Recovery state (checkpoints, active ticket/workflow, failure log)
    memory/           — Product-specific memory (domain, architecture, tech stack, decisions, risks)
    learning/         — Product-specific learnings (session, project)
    integrations/     — Product-specific integration config
    feature-flags/    — Product feature flags
  src/                — Application source code
  tests/              — Test suites
  packages/           — Monorepo packages (ui, shared, etc.)
  docs/               — Product documentation
```

## What Stays in the Factory

The factory repo provides: agents, skills, workflows, commands, guardrails, checklists, templates, core methodology docs, and design-system standards. These are NOT copied — the product repo references the factory for governance.

## Usage

This skeleton is used by `scripts/bootstrap-product.sh` and the `/bootstrap-product` command. Do not modify files here unless you want to change what every new product starts with.
