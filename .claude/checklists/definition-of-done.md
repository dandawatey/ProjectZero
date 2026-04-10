# Definition of Done

A work item is DONE when ALL are checked:

## Code
- [ ] All acceptance criteria implemented
- [ ] No TODO/FIXME comments in shipped code
- [ ] No console.log/debug in production code
- [ ] Follows project style guide (linter passes)

## Tests
- [ ] Unit tests written and passing
- [ ] Integration tests written and passing (where applicable)
- [ ] Coverage ≥ 80%
- [ ] No flaky tests

## Quality
- [ ] Linting: zero errors, zero warnings
- [ ] Security scan: no high/critical findings
- [ ] API contracts honored (response matches spec)
- [ ] No circular dependencies introduced

## Process
- [ ] Ticket updated with final status
- [ ] PR approved (Reviewer + Approver)
- [ ] All PR comments resolved
- [ ] Branch merged and deleted

## Documentation
- [ ] API docs updated (if API changed)
- [ ] README updated (if setup changed)

## UI (if applicable)
- [ ] Uses design tokens
- [ ] Storybook stories for all variants
- [ ] Accessible (keyboard, screen reader, contrast)
- [ ] Responsive at all breakpoints
- [ ] Loading, error, empty states implemented
