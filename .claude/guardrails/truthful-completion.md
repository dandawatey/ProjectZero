# Truthful Completion Guardrail

## Rule
Work is complete ONLY when it actually meets all criteria. No exceptions. No "close enough." No "we'll fix later."

## Violations (Each is Grounds for Rejection)
1. Marking a ticket "done" with failing tests
2. Claiming test coverage without running coverage tool
3. Using `// TODO: implement` in code marked as complete
4. Claiming security scan passed without running it
5. Approving without reading the code/artifact
6. Merging with unresolved PR comments
7. Shipping with known P1/P2 bugs
8. Claiming "works" based on manual testing only (automated tests required)

## Enforcement
- Checker agent validates all completion claims automatically
- Violations logged in `.claude/reports/audit-log.md`
- Repeated violations trigger agent behavior review
- Immediate revert to "in progress" on any violation discovery

## Why This Matters
Fake completion creates technical debt that compounds. A "done" item that isn't actually done blocks downstream work and erodes trust in the system. Better to be honestly incomplete than falsely complete.
