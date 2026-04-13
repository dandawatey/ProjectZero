# Refactor Audit: ProjectZeroFactory

**Date**: 2026-04-10
**Purpose**: Classify all content as factory-owned vs product-owned and plan refactor.

## Classification

### FACTORY-OWNED (keep as-is)
| Path | Purpose |
|------|---------|
| .claude/agents/*-team/ | Reusable agent definitions grouped by team |
| .claude/skills/ | 17 reusable skill packages |
| .claude/workflows/ | 15 reusable workflow definitions |
| .claude/commands/ | 22 reusable command definitions |
| .claude/guardrails/ | 9 governance guardrails |
| .claude/checklists/ | 8 quality checklists |
| .claude/templates/ | 17 reusable templates |
| .claude/core/ | Build methodology, architecture principles, BMAD process |
| .claude/modules/ | 10 module pattern guides |
| .claude/design-system/ | Design system standards |
| .claude/runtime/ | Execution model, scheduler, agent protocol docs |
| .claude/devops/ | Deployment/rollback script templates, env docs |
| .claude/operations/ | Bug/support/incident/analytics process docs |
| .claude/CLAUDE.md | Org-wide operating contract |
| .claude/settings.json | Factory default settings |
| docs/ | Process documentation |
| examples/ | Sample BMAD, PRD, module, ticket |
| scripts/ | Bootstrap and validation scripts |
| README.md | Getting started guide |

### PRODUCT-OWNED (must move out or convert to templates)
| Path | Issue | Action |
|------|-------|--------|
| .claude/delivery/queue/*.json | Live queue state with `"items": []` | Convert to template schemas |
| .claude/delivery/queue/scheduler-state.json | Live scheduler state | Convert to template |
| .claude/delivery/reconciliation/*.md | Live sync conflict tracking | Convert to template |
| .claude/delivery/jira/* (empty dirs) | Product JIRA state directories | Remove; document in product skeleton |
| .claude/delivery/confluence/* (empty dirs) | Product Confluence state dirs | Remove; document in product skeleton |
| .claude/delivery/github/* (empty dirs) | Product GitHub state dirs | Remove; document in product skeleton |
| .claude/delivery/features/ (empty) | Product feature tracking | Remove; document in product skeleton |
| .claude/delivery/epics/ (empty) | Product epic tracking | Remove; document in product skeleton |
| .claude/reports/*.md | Live product reports (11 files) | Convert to templates |
| .claude/recovery/state.json | Live product recovery state | Convert to template |
| .claude/recovery/active-ticket.json | Live ticket state | Convert to template |
| .claude/recovery/active-workflow.json | Live workflow state | Convert to template |
| .claude/recovery/failure-log.md | Live failure log | Convert to template |
| .claude/memory/domain-memory.md | Product domain knowledge | Convert to template |
| .claude/memory/architecture-memory.md | Product arch decisions | Convert to template |
| .claude/memory/tech-stack-memory.md | Product tech stack | Convert to template |
| .claude/memory/decisions-log.md | Product decisions | Convert to template |
| .claude/memory/known-risks.md | Product risks | Convert to template |
| .claude/learning/session-learnings.md | Product session data | Convert to template |
| .claude/learning/project-learnings.md | Product learnings | Convert to template |
| .claude/contracts/api-contract.yaml | Sample product API contract | Move to templates |
| .claude/contracts/db-schema.sql | Sample product DB schema | Move to templates |
| .claude/contracts/frontend-types.ts | Sample product types | Move to templates |
| .claude/integrations/config.json | Product integration config | Convert to template |
| .claude/feature-flags/flags.json | Product feature flags | Convert to template |
| .env | Product environment secrets | Keep in .gitignore only |

### DUPLICATES (remove)
| Path | Duplicate Of | Action |
|------|-------------|--------|
| .claude/agents/*.md (22 root files) | Same files in team folders | Delete root copies |
| CLAUDE.md (root, 65 lines) | .claude/CLAUDE.md (345 lines) | Merge into .claude/CLAUDE.md; root becomes pointer |

### EMPTY DIRECTORIES (remove from factory, document in skeleton)
27 empty directories under .claude/ — these are product-state directories that should be created by /bootstrap-product in product repos, not exist in the factory.

### AMBIGUOUS (resolved)
| Path | Decision |
|------|----------|
| .claude/memory/org-context.md | KEEP — factory-level org context template |
| .claude/learning/factory-learnings.md | KEEP — factory-level (cross-product) |
| .claude/learning/promoted-patterns.md | KEEP — factory-level |
| .claude/learning/rejected-patterns.md | KEEP — factory-level |
| .claude/learning/debug-patterns.md | KEEP — factory-level pattern library |
| .claude/learning/review-patterns.md | KEEP — factory-level |
| .claude/learning/test-patterns.md | KEEP — factory-level |
| .claude/learning/uiux-patterns.md | KEEP — factory-level |
| .claude/recovery/ide-session.md | KEEP — generic recovery guide |
| .claude/recovery/resume-protocol.md | KEEP — generic protocol |
| .claude/recovery/restart-checklist.md | KEEP — generic checklist |

## Summary
- **Keep**: ~250 files (agents, skills, workflows, commands, docs, templates, process guides)
- **Convert to templates**: ~30 files (delivery state, reports, recovery state, memory, contracts)
- **Delete duplicates**: 22 root-level agent files + root CLAUDE.md
- **Remove empty dirs**: 27 empty directories
- **New files needed**: 6 (repository-boundaries, migration guide, validation, factory-audit cmd, factory-upgrade cmd, product-repo skeleton)
