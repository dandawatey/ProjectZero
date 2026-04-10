# Guardrails Module

## Code Quality Gates
- Linting: zero errors, zero warnings (ESLint + Prettier)
- Type checking: strict mode, no `any` types in production code
- No `console.log` in production (use structured logger)
- No `// @ts-ignore` without explanation comment
- Max function complexity: cyclomatic complexity < 10
- Max file length: 300 lines (refactor if exceeded)

## PR Limits
- Max 400 lines changed per PR
- Larger changes must be split into logical PRs
- Exception: auto-generated code (migrations, types from contracts)

## Dependency Management
- New dependencies require review (justify need in PR description)
- No deprecated packages
- License check (no GPL in proprietary code without legal review)
- Monthly dependency audit (Dependabot/Snyk)
- Lock file always committed

## Breaking Change Detection
- API contract tests detect response schema changes
- Database migration review for data loss risk
- Minimum 1 version backward compatible for APIs
- Breaking changes require: version bump, migration guide, deprecation notice

## Database Migration Safety
- All migrations must be reversible (up + down)
- No data loss in migrations (add columns, don't drop without data migration)
- Test on staging database copy first
- Large table migrations during maintenance window
- Migration review required for tables > 1M rows
