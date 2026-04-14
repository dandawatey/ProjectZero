# Agent Registry — Organized by Team

## CXO Team
Executive leadership. Owns company strategy, cross-functional alignment, and organizational health.

| Agent | File | Mission |
|-------|------|---------|
| CEO | cxo-team/ceo.md | Company direction, OKRs, board relations, final escalation |
| CTO | cxo-team/cto.md | Technical vision, engineering excellence, technology bets |
| CPO | cxo-team/cpo.md | Product strategy, portfolio management, product-market fit |
| CFO | cxo-team/cfo.md | Financial health, budgeting, forecasting, unit economics |
| CMO | cxo-team/cmo.md | Brand, market positioning, demand generation, growth |
| CRO | cxo-team/cro.md | Revenue strategy, sales + CS alignment, pipeline, pricing |
| Ralph Controller | cxo-team/ralph-controller.md | Master orchestrator — routes work, manages queues, never implements |

## Product Management Team
Owns product vision, specifications, user research, and analytics.

| Agent | File | Mission |
|-------|------|---------|
| Product Manager | product-team/product-manager.md | Translate BMAD/PRD to specs, prioritize backlog |
| Product Analyst | product-team/product-analyst.md | Data-driven insights, metrics, A/B tests |
| UX Researcher | product-team/ux-researcher.md | User research, usability testing, personas |

## Engineering Team
Owns technical design, implementation, testing, reliability, and infrastructure.

| Agent | File | Mission |
|-------|------|---------|
| Architect | engineering-team/architect.md | System architecture, modules, contracts, tech stack |
| Backend Engineer | engineering-team/backend-engineer.md | Server-side code, APIs, database, TDD |
| Frontend Engineer | engineering-team/frontend-engineer.md | UI components, pages, design system, Storybook |
| Data Engineer | engineering-team/data-engineer.md | Data pipelines, ETL, analytics infrastructure |
| DevOps Engineer | engineering-team/devops-engineer.md | CI/CD, infrastructure, environments, monitoring |
| QA Engineer | engineering-team/qa-engineer.md | Test plans, integration/e2e tests, quality validation |
| SRE Engineer | engineering-team/sre-engineer.md | Reliability, SLOs, monitoring, incident response |

## Sales Team
Owns revenue generation, customer acquisition, and customer success.

| Agent | File | Mission |
|-------|------|---------|
| Sales Strategist | sales-team/sales-strategist.md | Sales strategy, playbooks, pipeline, pricing |
| Customer Success | sales-team/customer-success.md | Onboarding, retention, expansion, advocacy |

## Marketing Team
Owns brand, demand generation, content, and public communications.

| Agent | File | Mission |
|-------|------|---------|
| Marketing Strategist | marketing-team/marketing-strategist.md | Marketing strategy, brand, campaigns, launch |
| Content Creator | marketing-team/content-creator.md | Blog, social, email, case studies, landing pages |

## Governance Team
Owns quality gates, security, and UX compliance.

| Agent | File | Mission |
|-------|------|---------|
| Checker | governance-team/checker.md | First gate: tests, lint, security scan, ticket compliance |
| Reviewer | governance-team/reviewer.md | Second gate: code quality, architecture, coverage |
| Approver | governance-team/approver.md | Final gate: business requirements, governance compliance |
| Security Reviewer | governance-team/security-reviewer.md | OWASP, dependency audit, auth review. Can BLOCK. |
| UX Reviewer | governance-team/ux-reviewer.md | Usability, accessibility, design system. Can BLOCK. |
| ISO Documentation Agent | governance-team/iso-documentation-agent.md | Keep ISO 42001 docs current: SoA, risk register, incidents, audit readiness → Confluence |

## Operations Team
Owns releases, integrations, infrastructure operations, and factory tooling.

| Agent | File | Mission |
|-------|------|---------|
| Release Manager | operations-team/release-manager.md | Release orchestration, deployment, rollback |
| FinOps Analyst | operations-team/finops-analyst.md | Cloud costs, optimization, budget compliance |
| Integration Agent | operations-team/integration-agent.md | JIRA/Confluence/GitHub sync |
| Plugin Validator | operations-team/plugin-validator.md | Validate plugins and skills installed |
| Repo Validator | operations-team/repo-validator.md | Validate repository structure |
| Readiness Validator | operations-team/readiness-validator.md | Validate stage readiness |
| Pipeline Agent | operations-team/pipeline-agent.md | Async pipeline execution (Dagster) |
| Memory Agent | operations-team/memory-agent.md | Memory lifecycle, learning, promotion |

---

## Team Interaction Model
```
CXO Team (CEO, CTO, CPO, CFO, CMO, CRO, Ralph)
    │
    ├──→ Product Team ──→ Engineering Team ──→ Governance Team
    │         │                   │                    │
    │         ▼                   │                    ▼
    ├──→ Sales Team               └──→ Operations Team
    │         │
    │         ▼
    └──→ Marketing Team
```

## Total Agents: 35 (across 7 teams)
