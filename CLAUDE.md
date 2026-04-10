# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

ProjectZeroFactory is an org-wide operating system for governed product development. It is not an application -- it is a file-based configuration and workflow system that lives in `.claude/`. Products are created by cloning the factory template via the bootstrap script, inheriting governance rules, memory structure, and command flows.

## Key Scripts

```bash
# Bootstrap a new product (interactive -- prompts for name and directory)
bash scripts/bootstrap-product.sh --name <product-name> --dir <path>

# Validate .env configuration (checks required keys, masks secrets)
bash scripts/validate-env.sh              # basic validation
bash scripts/validate-env.sh --strict     # also checks optional keys
bash scripts/validate-env.sh <path>       # validate a specific .env file
```

There is no build system, test runner, or linter in this repo. Those are product-specific and defined per product after bootstrapping.

## Architecture

**5-layer system, all file-based under `.claude/`:**

- **Layer 5 - Commands** (`commands/`): Slash command definitions (`/factory-init`, `/spec`, `/arch`, `/implement`, `/check`, `/review`, `/approve`, `/release`). These are the user interface.
- **Layer 4 - Workflows** (`workflows/`): Multi-step orchestrations that coordinate agents across stages.
- **Layer 3 - Agents** (`agents/`): Specialized role definitions with scoped responsibilities and contracts (`contracts/`).
- **Layer 2 - Skills** (17 skill directories): Reusable capabilities like `code-reviewer/`, `playwright-skill/`, `secure-code-guardian/`, `rag-architect/`, etc.
- **Layer 1 - Core** (`core/`): Governance rules, system prompts, memory, recovery, and the binding operating contract (`CLAUDE.md`).

**Supporting infrastructure under `.claude/`:**

- `delivery/` -- Integration adapters for JIRA, Confluence, GitHub (sync state, queues, mappings)
- `memory/` -- Product-level session logs, decisions, blockers, patterns (append-only during sessions)
- `knowledge/` -- Factory-level promoted learnings
- `recovery/` -- Checkpoint state for session resumption
- `templates/` -- Templates for all artifact types
- `guardrails/` -- Safety and compliance rules
- `settings.json` -- Factory configuration (governance thresholds, integration toggles, recovery settings)

## Command Flow (Sequential, Cannot Skip)

`/factory-init` -> `/bootstrap-product` -> `/spec` -> `/arch` -> `/implement` <-> `/check` (loop) -> `/review` -> `/approve` -> `/release`

## Binding Operating Contract

The full governance contract is at [.claude/CLAUDE.md](.claude/CLAUDE.md). All rules there are binding. Key non-negotiables:

1. No work without a ticket
2. TDD always -- tests before implementation
3. 80% minimum test coverage enforced by `/check`
4. Truthful completion -- never report done unless actually done
5. Memory recording -- read before act, write after act
6. Stage gates cannot be skipped
7. Maker-Checker-Reviewer-Approver on all significant changes

## Environment Setup

Copy `.env.example` to `.env` and configure. Minimum required keys: `ANTHROPIC_API_KEY`, `GITHUB_TOKEN`, `GITHUB_ORG`. JIRA and Confluence integrations are optional (disabled by default in `settings.json`).

## Memory System

Memory files in `.claude/memory/` are append-only during sessions. Each entry needs a timestamp and ticket ID. Structure: `session-log.md`, `decisions.md`, `blockers.md`, `patterns.md`, `learnings.md`. Learnings can be promoted to `.claude/knowledge/` for factory-wide reuse.
