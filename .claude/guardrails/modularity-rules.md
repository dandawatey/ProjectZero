# Modularity Rules

## Module Boundaries
- Each module has a clear, documented boundary
- Module owns its data (no shared tables)
- Module exposes functionality via defined API only
- No direct database access across module boundaries

## Dependencies
- No circular dependencies between modules
- Dependency direction: feature modules → shared packages (never reverse)
- New cross-module dependency requires architecture review
- Visualize dependency graph periodically

## Shared Code
- Shared utilities in `packages/shared`
- Shared UI in `packages/ui`
- Shared types in `packages/types`
- No module-specific logic in shared packages

## Independent Testing
- Each module testable in isolation
- Module tests don't depend on other modules being available
- Mock cross-module APIs in unit tests
- Integration tests verify cross-module contracts

## Independent Deployment
- Each module deployable independently (goal)
- No deployment requires deploying another module simultaneously
- Database migrations per module, independently executable
- Feature flags for gradual module rollout
