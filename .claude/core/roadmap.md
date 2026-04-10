# Factory Roadmap

## v1.0 — Core Factory (Current)
- Local-first operation with file-based state
- All agents defined with missions, scopes, handoffs
- All skills packaged with usage guides
- All workflows documented with step-by-step processes
- All commands defined with inputs/outputs/validation
- Governance chain (maker-checker-reviewer-approver)
- Memory and learning system
- Recovery and resume capability
- Design system governance
- Queue-based work management

## v1.1 — Live Integrations
- JIRA API integration (create/update/query tickets)
- Confluence API integration (create/update pages)
- GitHub API integration (create repos, PRs, manage branches)
- Webhook handlers for real-time sync
- Conflict resolution for bidirectional sync
- Slack notifications for status updates
- **Dependencies**: API tokens, network access, webhook endpoints

## v1.2 — Pipeline Automation
- Dagster integration for data pipelines
- FastAPI workers for async task execution
- Redis-based queue with atomic operations
- Scheduled jobs (daily reports, weekly audits)
- Pipeline monitoring dashboard
- **Dependencies**: Redis, Dagster, FastAPI infrastructure

## v1.3 — Portfolio Management
- Multiple product repos managed from single factory
- Cross-product dependency tracking
- Shared learning promotion across products
- Portfolio-level reporting
- Resource allocation across products
- **Dependencies**: v1.0, multi-repo git workflows

## v2.0 — Self-Improving Factory
- ML-based pattern promotion (auto-detect successful patterns)
- Automated code quality scoring
- Predictive risk assessment
- Agent performance metrics and optimization
- Natural language query across factory memory
- **Dependencies**: v1.3, ML infrastructure, sufficient training data
