# Completion Rules

## Definition of Done — Factory-Wide

A work item is DONE only when ALL of the following are true:

### Code
- [ ] All acceptance criteria implemented
- [ ] No TODO or FIXME comments in shipped code
- [ ] No console.log or debug statements in production code
- [ ] Code follows project style guide (enforced by linter)
- [ ] No dead code or unused imports

### Tests
- [ ] Unit tests for all business logic
- [ ] Integration tests for all API endpoints
- [ ] E2E tests for critical user flows
- [ ] All tests passing (zero failures)
- [ ] Coverage ≥ 80% lines (100% on critical paths)
- [ ] Test names describe behavior

### Security
- [ ] Security scan clean (no high/critical findings)
- [ ] No secrets in code or config
- [ ] Input validation on all user-facing endpoints
- [ ] Auth/authz applied where required
- [ ] Dependencies audited (no known vulnerabilities)

### Quality
- [ ] Linting passes with zero errors, zero warnings
- [ ] Type checking passes (TypeScript strict mode)
- [ ] No circular dependencies
- [ ] Performance acceptable (no regressions)
- [ ] API responses match contract

### Documentation
- [ ] API documentation updated (if API changed)
- [ ] README updated (if setup changed)
- [ ] Architecture docs updated (if architecture changed)
- [ ] Inline comments for non-obvious logic only

### UI (if applicable)
- [ ] Uses design tokens (no hardcoded colors/sizes)
- [ ] Storybook stories for all variants and states
- [ ] Accessibility: keyboard navigable, screen reader tested
- [ ] Responsive: works at all breakpoints
- [ ] Loading, error, and empty states implemented

### Process
- [ ] Ticket updated with final status
- [ ] PR approved by Reviewer and Approver
- [ ] All PR comments resolved
- [ ] Branch merged and deleted
- [ ] Learning written to session-learnings.md

## Truthful Completion Policy

**Non-negotiable rules:**
1. Never mark an item as "done" if any checkbox above is unchecked
2. Never claim tests pass without actually running them
3. Never claim coverage without measuring it
4. Never use placeholder implementations ("// TODO: implement later")
5. Never skip security scan and claim "clean"
6. Never approve without actually reviewing
7. "Works on my machine" is not done — CI must pass

**Violation handling:**
- If a completed item is found to violate these rules, it is immediately moved back to "in progress"
- The violation is logged in `.claude/reports/audit-log.md`
- Pattern of violations triggers review of agent behavior
