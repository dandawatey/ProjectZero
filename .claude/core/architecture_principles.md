# Architecture Principles

## 1. Modular Monorepo
- Product organized as `packages/` with clear boundaries
- Each module is a package: `packages/auth`, `packages/vitals`, `packages/ui`
- Shared code in `packages/shared`
- **Enforcement**: Repo validator checks structure; circular dependency detection in CI
- **Example**: `packages/vitals` can import from `packages/shared` but not from `packages/auth` directly — use APIs

## 2. API-First Design
- Design API contracts (OpenAPI 3.0) before writing implementation
- Contracts stored in `.claude/templates/api-contract-template.yaml`
- Frontend and backend develop against contracts in parallel
- **Enforcement**: Contract tests validate responses match spec
- **Example**: Define `POST /api/vitals` contract → backend implements → frontend consumes → contract test validates both

## 3. Event-Driven Where Async
- Synchronous for request-response (API calls)
- Async for fire-and-forget (notifications, analytics, audit logging)
- Message queue (Redis/RabbitMQ) for decoupled operations
- **Enforcement**: Architecture review validates sync vs async choices
- **Example**: Vitals alert triggers async notification — don't block the vitals API response

## 4. 12-Factor App Compliance
- Config from environment variables (never hardcoded)
- Stateless processes (no local session state)
- Disposable instances (fast startup, graceful shutdown)
- Dev/prod parity (same stack, same configs structure)
- Logs as event streams (stdout, structured JSON)
- **Enforcement**: `.env.example` defines all config; deploy scripts validate

## 5. Infrastructure as Code
- All infrastructure defined in code (Terraform, Pulumi, or CDK)
- No manual cloud console changes
- Infrastructure changes go through same PR process as application code
- **Enforcement**: DevOps engineer reviews all infra changes

## 6. Security by Design
- Authentication and authorization from day one
- Input validation on every endpoint
- Parameterized queries only (no string concatenation for SQL)
- HTTPS everywhere, CORS restricted, CSP headers
- Secrets in environment variables only
- **Enforcement**: Security reviewer mandatory for auth/data/API changes

## 7. Observability Built-In
- Structured logging from first endpoint
- Request tracing (OpenTelemetry) from first service
- Health check endpoints from first deployment
- Metrics collection from first release
- **Enforcement**: SRE engineer validates observability in architecture review

## 8. Shared Component Library
- All UI components in `packages/ui`
- Design tokens as single source of truth
- Storybook for visual development and testing
- No ad-hoc components for existing patterns
- **Enforcement**: UI audit checks for design system compliance

## 9. Database per Bounded Context
- Each module owns its data store
- No shared tables between modules
- Cross-module data access via APIs only
- Migrations are reversible
- **Enforcement**: Architecture review validates data boundaries

## 10. Contract-First APIs
- OpenAPI 3.0 spec written before implementation
- Frontend types generated from spec
- Contract tests validate implementation matches spec
- Breaking changes require version bump and migration guide
- **Enforcement**: CI runs contract tests; breaking change detection in PR
