# Main Workflow

## Complete Factory Flow
```
/factory-init → /bootstrap-product → /spec → /arch → /implement → /check → /review → /approve → /release → /monitor → /optimize
```

## Stage Map

| Stage | Command | Entry Criteria | Exit Criteria |
|-------|---------|---------------|---------------|
| Initialize | /factory-init | Cloned repo | Factory validated |
| Bootstrap | /bootstrap-product | Factory ready | Product configured, BMAD loaded |
| Specification | /spec | BMAD approved | Specs approved, tickets created |
| Architecture | /arch | Specs approved | Architecture approved, contracts created |
| Realization | /implement | Architecture approved | All tickets done, tests passing |
| Validation | /check, /review | Implementation complete | All checks and reviews pass |
| Approval | /approve | Reviews complete | Business sign-off |
| Release | /release | All approvals | Deployed, health checks green |
| Operations | /monitor | Released | Monitoring active, alerts configured |
| Optimization | /optimize | Monitoring data | Improvement tickets created |

## Cross-Cutting Workflows
- **Recovery**: /resume, /recover-ticket, /recover-workflow — any stage
- **Design System**: /design-system-init, /component-create, /ui-audit — during Architecture and Realization
- **Governance**: maker-checker-reviewer-approver — every artifact at every stage
