# Command: /factory-audit

## Purpose
Validate the factory repo structure is correct and no product-specific state has leaked in.

## Trigger
User runs `/factory-audit` to health-check the factory.

## Step-by-Step Process

### Step 1: Validate Structure
Check required directories exist:
- .claude/agents/ (with team subdirectories)
- .claude/skills/ (17 skill folders)
- .claude/workflows/, commands/, guardrails/, checklists/, templates/
- .claude/core/, modules/, design-system/, runtime/
- docs/, examples/, scripts/

### Step 2: Check for Product Leakage
Scan for files that should NOT be in the factory:
- .claude/delivery/ (should not exist in factory)
- .claude/reports/ (should not exist in factory)
- .claude/recovery/state.json, active-ticket.json, active-workflow.json (should not exist)
- .claude/memory/ should only have org-context.md
- .claude/integrations/config.json should not exist (template only)
- Any .json files with non-template live state

### Step 3: Validate Agent Registry
Check AGENT_REGISTRY.md matches actual team folders and files.

### Step 4: Validate Skill Completeness
Each skill folder should have: SKILL.md, usage.md, triggers.md, checklist.md

### Step 5: Report
Generate validation report with pass/fail per check.

## Required Inputs
None (reads current repo)

## Outputs
Factory health report

## Next Command
/factory-upgrade (if issues found) or /bootstrap-product (if healthy)
