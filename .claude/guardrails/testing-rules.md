# Testing Rules

## Test Pyramid
- Unit tests: 70% — fast, isolated, test business logic
- Integration tests: 20% — test API endpoints, DB operations, module interactions
- E2E tests: 10% — test critical user flows end-to-end

## Requirements
- Minimum 80% line coverage overall
- 100% coverage on critical paths (auth, payments, data mutations)
- All tests must pass in CI (no "known failures")
- No flaky tests allowed (fix or quarantine immediately)

## Conventions
- Test files next to source: `foo.ts` → `foo.test.ts`
- Describe blocks match module/function structure
- Test names describe behavior: `should return 404 when user not found`
- One assertion per test (prefer focused tests)
- No testing implementation details (test behavior)

## TDD Cycle
1. Write a failing test that describes expected behavior
2. Write the minimum code to make it pass
3. Refactor while keeping tests green
4. Repeat for next behavior

## Test Data
- Use fixtures for static data (`.claude/data/fixtures/`)
- Use factory functions for dynamic test data
- Never use production data
- Clean up test data after each test (isolated tests)

## What NOT to Test
- Third-party library internals
- Framework behavior (e.g., React rendering)
- Exact CSS/style values (use visual regression instead)
- Private/internal functions (test through public API)
