# QA Module

## Testing Pyramid
- **Unit Tests (70%)**: Fast, isolated, test business logic. One assertion per test. Mock external dependencies.
- **Integration Tests (20%)**: Test API endpoints with real database. Test module interactions. Test external API contracts.
- **E2E Tests (10%)**: Test critical user flows with Playwright. Test cross-module workflows. Run in CI.

## Coverage Requirements
- Minimum 80% line coverage overall
- 100% coverage on critical paths (auth, payments, data mutations)
- Coverage measured and reported in CI
- No merge below threshold

## Test Conventions
- Test files: `*.test.ts` or `*.spec.ts` next to source
- Describe blocks: match module and function names
- Test names: describe behavior (`should return 404 when user not found`)
- No testing implementation details (test behavior, not internal structure)

## Test Data
- Fixtures in `.claude/data/fixtures/` for static test data
- Factory functions for dynamic test data
- Synthetic data in `.claude/data/synthetic-data/` for load testing
- Never use production data in tests

## QA Agent Responsibilities
- Write test plans from specifications
- Create integration and e2e tests
- Validate acceptance criteria through tests
- Report quality metrics (coverage, pass rate, flaky tests)
- Maintain regression test suite

## Visual Regression
- Storybook for component-level visual testing
- Screenshot comparison for key pages
- Baseline captured per release
- Differences flagged in PR
