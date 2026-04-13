# Command: /factory-upgrade

## Purpose
Upgrade the factory with new agents, skills, workflows, or governance rules.

## Trigger
User runs `/factory-upgrade` when factory needs new capabilities.

## Step-by-Step Process

### Step 1: Identify Upgrade Type
Ask user what to upgrade:
- New agent definition
- New skill package
- New workflow
- New guardrail or checklist
- Updated template
- New documentation

### Step 2: Validate Upgrade
- Does not introduce product-specific content
- Does not break existing structure
- Follows naming conventions
- Includes all required files (e.g., skill needs SKILL.md, usage.md, triggers.md, checklist.md)

### Step 3: Apply Upgrade
Create/update files in the factory repo.

### Step 4: Update Registry
Update AGENT_REGISTRY.md, docs, or command reference as needed.

### Step 5: Run /factory-audit
Validate factory is still healthy after upgrade.

## Required Inputs
Upgrade specification from user

## Outputs
Updated factory files, audit report

## Next Command
/factory-audit
