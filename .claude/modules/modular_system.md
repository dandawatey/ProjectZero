# Modular System

## Purpose
The factory decomposes every product into modules — bounded business capabilities that can be independently specified, designed, implemented, tested, and deployed.

## What is a Module?
A module is a self-contained unit that owns:
- **Business logic**: Domain rules and operations
- **API surface**: REST/GraphQL endpoints
- **Data model**: Database tables/collections
- **UI surface**: Pages and components
- **Tests**: Unit, integration, e2e
- **Documentation**: API docs, architecture notes

## Module Lifecycle
```
Candidate → Specified → Architected → Implemented → Tested → Reviewed → Deployed
```

1. **Candidate**: Identified during BMAD analysis. Named, described, boundaries proposed.
2. **Specified**: Requirements formalized, stories created, acceptance criteria defined.
3. **Architected**: API contracts designed, data model defined, dependencies mapped.
4. **Implemented**: Code written with TDD, all stories completed.
5. **Tested**: QA validated, integration tests passing, e2e flows working.
6. **Reviewed**: Code reviewed, security reviewed, UX reviewed (if UI).
7. **Deployed**: In production, monitoring active, runbook available.

## Module Rules
1. Modules communicate only via defined APIs (no shared databases)
2. No circular dependencies between modules
3. Each module independently testable
4. Shared code goes in `packages/shared`, not in module packages
5. Module template: `.claude/templates/module-template.md`

## Module Template Fields
- Name, Purpose, Owner
- Boundaries (what it owns, what it doesn't)
- API Surface (endpoints with methods, paths, request/response schemas)
- Data Model (tables, relationships, indexes)
- Dependencies (other modules, external services)
- Test Strategy (unit scope, integration scope, e2e flows)
- Status (lifecycle stage)
