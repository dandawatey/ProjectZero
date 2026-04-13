# Refactor Migration Guide

## What Changed

This document records the refactor from v1 (factory-as-product) to v2 (clean factory).

### Files Deleted (Duplicates)
22 root-level agent files removed. Canonical copies live in team subdirectories:
- `.claude/agents/approver.md` → use `.claude/agents/governance-team/approver.md`
- `.claude/agents/architect.md` → use `.claude/agents/engineering-team/architect.md`
- (all 22 agents followed this pattern)

Root `CLAUDE.md` removed. Canonical copy: `.claude/CLAUDE.md`

### Files Moved to Product Skeleton Template
These files were live-state files that don't belong in the factory. They now live at `.claude/templates/product-skeleton/` and are copied to product repos by `/bootstrap-product`:

| Former Location | New Location |
|----------------|-------------|
| .claude/delivery/queue/*.json | .claude/templates/product-skeleton/delivery/queue/ |
| .claude/delivery/reconciliation/*.md | .claude/templates/product-skeleton/delivery/reconciliation/ |
| .claude/reports/*.md (11 files) | .claude/templates/product-skeleton/reports/ |
| .claude/recovery/state.json | .claude/templates/product-skeleton/recovery/ |
| .claude/recovery/active-ticket.json | .claude/templates/product-skeleton/recovery/ |
| .claude/recovery/active-workflow.json | .claude/templates/product-skeleton/recovery/ |
| .claude/recovery/failure-log.md | .claude/templates/product-skeleton/recovery/ |
| .claude/memory/architecture-memory.md | .claude/templates/product-skeleton/memory/ |
| .claude/memory/domain-memory.md | .claude/templates/product-skeleton/memory/ |
| .claude/memory/tech-stack-memory.md | .claude/templates/product-skeleton/memory/ |
| .claude/memory/decisions-log.md | .claude/templates/product-skeleton/memory/ |
| .claude/memory/known-risks.md | .claude/templates/product-skeleton/memory/ |
| .claude/learning/session-learnings.md | .claude/templates/product-skeleton/learning/ |
| .claude/learning/project-learnings.md | .claude/templates/product-skeleton/learning/ |
| .claude/contracts/api-contract.yaml | .claude/templates/api-contract-template.yaml |
| .claude/contracts/db-schema.sql | .claude/templates/db-schema-template.sql |
| .claude/contracts/frontend-types.ts | .claude/templates/frontend-types-template.ts |
| .claude/integrations/config.json | .claude/templates/product-skeleton/integrations/ |
| .claude/feature-flags/flags.json | .claude/templates/product-skeleton/feature-flags/ |

### Empty Directories Removed
27 empty directories that existed as product-state placeholders:
- .claude/delivery/jira/*, .claude/delivery/confluence/*, .claude/delivery/github/*
- .claude/delivery/features/, .claude/delivery/epics/
- .claude/portfolio/, .claude/finops/, .claude/sre/, .claude/analytics/
- .claude/embeddings/, .claude/memory_store/, .claude/knowledge/
- .claude/pipelines/, .claude/definition-of-done/
- .claude/data/fixtures/, .claude/data/synthetic-data/

These directories are now created by `/bootstrap-product` in product repos.

### New Files Created
| File | Purpose |
|------|---------|
| docs/refactor-audit.md | Audit classification of all files |
| docs/repository-boundaries.md | Factory vs product ownership rules |
| docs/refactor-migration-guide.md | This file |
| docs/refactor-validation.md | Post-refactor validation report |
| .claude/commands/factory-audit.md | New command: audit factory health |
| .claude/commands/factory-upgrade.md | New command: upgrade factory capabilities |
| .claude/templates/product-skeleton/README.md | Skeleton documentation |

### Docs Updated
- README.md — Rewrote to clarify factory vs product
- docs/01-how-projectzerofactory-works.md — Added boundary explanation
- docs/02-how-to-start-a-new-product.md — Clarified two-repo model
- docs/14-command-reference.md — Added factory-audit, factory-upgrade

## What Still Needs Manual Action

1. **If you had a product in progress**: Copy the product-specific files from git history into your product repo
2. **Update product repos**: Run `/bootstrap-product` to create the product-skeleton structure
3. **Review integration configs**: Product-specific JIRA/Confluence configs must live in product repos
