# Workflow: Factory Init

## Trigger
User runs `/factory-init` after cloning ProjectZeroFactory

## Steps
1. **Validate directory structure**: Check all required directories exist under .claude/
2. **Validate core files**: CLAUDE.md, settings.json present and non-empty
3. **Validate agents**: All 22 agent files in .claude/agents/
4. **Validate skills**: All 17 skill folders with required files
5. **Validate workflows**: All workflow files in .claude/workflows/
6. **Validate commands**: All command files in .claude/commands/
7. **Validate templates**: All template files
8. **Validate .env**: .env exists with required keys populated
9. **Register status**: Write initialized state to .claude/recovery/state.json

## Exit Criteria
- All validations pass
- State.json shows `initialized: true`

## Failure Handling
- List all missing items
- Do not proceed to /bootstrap-product until all resolved
