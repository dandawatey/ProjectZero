# Stage Gates

## Specification → Architecture
- [ ] All specifications written with acceptance criteria
- [ ] Specifications approved through governance chain
- [ ] Module candidates identified and documented
- [ ] Backlog prioritized
- [ ] Tickets created for all stories

## Architecture → Realization
- [ ] Architecture document approved
- [ ] All modules defined with boundaries
- [ ] API contracts created (api-contract.yaml)
- [ ] DB schema designed (db-schema.sql)
- [ ] Frontend types defined (frontend-types.ts)
- [ ] Tech stack decisions documented (ADRs)
- [ ] Infrastructure plan reviewed by SRE

## Realization → Release
- [ ] All tickets in release scope: status "Done"
- [ ] All tests passing (unit + integration + e2e)
- [ ] Test coverage ≥ 80%
- [ ] Security scan clean (no high/critical)
- [ ] All PRs approved through governance chain
- [ ] API contract tests passing
- [ ] Documentation updated
- [ ] Storybook stories complete (for UI)
- [ ] Accessibility audit passed (for UI)

## Release → Production
- [ ] Release checklist complete (.claude/checklists/release-readiness.md)
- [ ] Staging deployment successful
- [ ] Smoke tests passing on staging
- [ ] Rollback plan documented and tested
- [ ] Monitoring and alerting configured
- [ ] Runbooks available for operations
- [ ] Stakeholders notified

## Gate Enforcement
- Readiness-validator agent checks gates before stage transition
- Failing any gate blocks progression
- Override requires explicit user authorization with documented reason
