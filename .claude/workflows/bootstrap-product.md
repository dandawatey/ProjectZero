# Workflow: Bootstrap Product

## Trigger
User runs `/bootstrap-product` after successful `/factory-init`

## Steps
1. Confirm factory is initialized (check state.json)
2. Ask: Create new product repo or use existing?
3. If new: create directory, init git, copy .claude template
4. If existing: validate structure, add missing .claude files
5. Configure integrations (JIRA project key, Confluence space, GitHub repo)
6. Validate .env has integration credentials (if integrations enabled)
7. Initialize product-specific .claude state
8. Intake BMAD/PRD (user provides document)
9. Parse BMAD using spec-miner skill
10. Extract module candidates from BMAD
11. Create initial tracking setup (queue, reports)
12. Validate readiness for /spec (readiness-validator)
13. Hand off to /spec

## Exit Criteria
- Product repo exists with .claude OS
- BMAD parsed and stored in memory
- Module candidates identified
- Readiness validated for specification phase
