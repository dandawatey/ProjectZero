# Command: /factory-init

## Purpose
Validate that the ProjectZeroFactory repository is correctly structured and ready to create products.

## Trigger
User runs `/factory-init` after cloning the factory repo.

## Step-by-Step Process

### Step 1: Validate Directory Structure
Check these directories exist under .claude/:
- core/, modules/, agents/, skills/, workflows/, guardrails/, commands/
- templates/, checklists/, memory/, learning/, recovery/
- delivery/, reports/, integrations/, runtime/
- design-system/, devops/, operations/, contracts/

### Step 2: Validate Core Files
Check these files exist and are non-empty:
- .claude/CLAUDE.md
- .claude/settings.json
- README.md, .gitignore, .env.example

### Step 3: Validate Agent Files
Check all 22 agent files exist in .claude/agents/:
product-manager, architect, backend-engineer, frontend-engineer, data-engineer, devops-engineer, qa-engineer, security-reviewer, ux-reviewer, sre-engineer, finops-analyst, checker, reviewer, approver, release-manager, ralph-controller, integration-agent, plugin-validator, repo-validator, readiness-validator, pipeline-agent, memory-agent

### Step 4: Validate Skill Folders
Check all 17 skill folders exist in .claude/skills/ with SKILL.md, usage.md, triggers.md, checklist.md:
debug-skill, feature-forge, code-reviewer, playwright-skill, spec-miner, using-git-worktrees, secure-code-guardian, rag-architect, the-fool, refactoring-ui, ux-heuristics, hooked-ux, frontend-design, ios-hig-design, ui-ux-pro-max, design-sprint, superpowers

### Step 5: Validate Workflow Files
Check all workflow files exist in .claude/workflows/

### Step 6: Validate Command Files
Check all command files exist in .claude/commands/

### Step 7: Validate Environment
Check .env exists. Validate required keys are present (can be empty for optional integrations).

### Step 8: Register Factory Status
Write to .claude/recovery/state.json:
```json
{"initialized": true, "lastCheckpoint": "<timestamp>", "activeStage": "ready"}
```

## Required Inputs
- None (reads current repo)

## Involved Agents
- repo-validator (structure check)
- plugin-validator (skill check)

## Outputs
- Validation report with pass/fail per check
- Updated state.json

## Validation
All checks must pass. Missing items listed with paths.

## Failure Handling
- List all missing items clearly
- Do not mark as initialized if anything missing
- User must fix and re-run

## Next Command
/bootstrap-product
