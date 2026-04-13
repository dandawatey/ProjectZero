# 03 - Org Operating Model

## Overview

ProjectZeroFactory is designed to operate at the organizational level, not just the project level. A single factory template governs multiple product instances, enabling consistent standards, shared learning, and centralized oversight across an entire engineering organization.

## Portfolio Model

The `.claude/portfolio/` directory tracks all product instances created from the factory:

```
.claude/portfolio/
  registry.json           # Master list of all products
  health-dashboard.json   # Aggregated health metrics
  product-a/
    status.json           # Current stage, velocity, risks
    config.json           # Product-specific overrides
  product-b/
    status.json
    config.json
  product-c/
    status.json
    config.json
```

### Registry Format

```json
{
  "factory_version": "1.0.0",
  "products": [
    {
      "name": "ProductA",
      "repo": "https://github.com/org/product-a",
      "jira_key": "PA",
      "confluence_space": "PA",
      "created_at": "2026-01-15T10:00:00Z",
      "factory_version_at_creation": "1.0.0",
      "current_stage": "realization",
      "stack": ["nextjs", "fastapi", "postgresql"],
      "team_size": 3,
      "status": "active"
    }
  ]
}
```

### Health Dashboard

The portfolio health dashboard aggregates metrics across all products:

- **Velocity**: Stories completed per sprint per product
- **Quality**: Defect density, test coverage, security findings
- **Governance compliance**: Percentage of work that passed all governance gates
- **Recovery frequency**: How often products need to use recovery mechanisms
- **Learning rate**: Number of learnings promoted from session to factory level

## Multi-Project Governance

### Consistent Standards

Every product instance inherits the same governance model:
- Same SPARC workflow stages
- Same Maker-Checker-Reviewer-Approver chain
- Same definition-of-done criteria
- Same agent roles and responsibilities
- Same quality gates

This consistency means that team members can move between products without relearning processes, and that leadership can compare metrics across products on an apples-to-apples basis.

### Shared Learning

The factory's learning model operates at three levels:

1. **Session learnings**: Captured during a single Claude session, stored in `.claude/memory/`
2. **Project learnings**: Promoted from sessions, stored in `.claude/learning/`
3. **Factory learnings**: Promoted from projects, stored in the factory template and propagated to all products

When a product discovers a useful pattern (e.g., "always add retry logic to external API calls"), that learning can be promoted to the factory level so that all future products benefit.

### Cross-Product Patterns

The portfolio model enables identification of cross-product patterns:

- If three products all struggle with the same integration pattern, that is a signal to add it as a factory-level skill
- If a particular agent consistently produces lower-quality output in a specific domain, that is a signal to refine the agent's training
- If recovery is triggered frequently in a particular workflow stage, that is a signal to improve the stage's robustness

## Center of Excellence Ownership

### CoE Responsibilities

The Center of Excellence (CoE) is the team that owns and maintains the factory template. Their responsibilities:

1. **Factory development**: Adding new agents, skills, commands, and workflows
2. **Factory upgrades**: Versioning and releasing new factory versions
3. **Quality assurance**: Ensuring the factory itself meets quality standards
4. **Governance enforcement**: Defining and updating governance rules
5. **Learning curation**: Reviewing and promoting project-level learnings to factory level
6. **Support**: Helping product teams with factory adoption and troubleshooting
7. **Metrics**: Tracking portfolio-wide metrics and reporting to leadership

### CoE Workflow

```
Product teams report issues/suggestions
  |
  v
CoE triages and prioritizes
  |
  v
CoE develops factory improvements
  |
  v
CoE tests in staging product instance
  |
  v
CoE releases new factory version
  |
  v
Product teams upgrade (at their own pace)
```

### CoE Staffing Model

A typical CoE for ProjectZeroFactory includes:
- **1 Factory Architect**: Owns the overall factory design and agent model
- **1-2 Factory Engineers**: Implement new skills, commands, and integrations
- **1 Governance Lead**: Defines and maintains governance rules and checklists
- **1 Learning Curator**: Reviews and promotes learnings across products

For smaller organizations, these roles can be combined. The minimum viable CoE is one person who understands the factory architecture and can make changes to the template.

## Factory Versioning

### Version Scheme

The factory uses semantic versioning: `MAJOR.MINOR.PATCH`

- **MAJOR**: Breaking changes to agent contracts, command interfaces, or directory structure
- **MINOR**: New agents, skills, commands, or non-breaking enhancements
- **PATCH**: Bug fixes, learning promotions, documentation updates

### Version Tracking

Each product instance tracks:
- `factory_version_at_creation`: The factory version when the product was bootstrapped
- `factory_version_current`: The factory version currently in use
- `factory_version_available`: The latest factory version available for upgrade

### Upgrade Process

```
# In the product repo
/factory-upgrade --version 1.2.0
```

The upgrade command:
1. Downloads the new factory version
2. Diffs the `.claude/` directories (product vs. new factory)
3. Applies non-conflicting changes automatically
4. Flags conflicts for manual resolution
5. Preserves all product-specific data (memory, learning, recovery, delivery)
6. Updates `factory_version_current`
7. Runs the readiness validator to confirm the upgrade succeeded

### What Upgrades Touch

| Directory | Upgraded | Preserved |
|---|---|---|
| `.claude/agents/` | Yes | Product overrides preserved |
| `.claude/commands/` | Yes | Product extensions preserved |
| `.claude/skills/` | Yes | Product extensions preserved |
| `.claude/workflows/` | Yes | Product extensions preserved |
| `.claude/core/` | Yes (merge) | Product config merged |
| `product repo .claude/contracts/` | Yes | |
| `.claude/checklists/` | Yes | |
| `.claude/definition-of-done/` | Yes | |
| `.claude/templates/` | Yes | |
| `.claude/guardrails/` | Yes | |
| `.claude/memory/` | No | Fully preserved |
| `.claude/learning/` | No (additive only) | Product learnings preserved |
| `.claude/recovery/` | No | Fully preserved |
| `product repo .claude/delivery/` | No | Fully preserved |
| `.claude/design-system/` | No | Fully preserved |

## Org-Wide Reporting

### Sprint Reports

Each product generates sprint reports in `product repo .claude/reports/`. The portfolio aggregates these into org-wide views:

- Total stories completed across all products
- Average velocity per team
- Governance compliance rate
- Security findings by severity
- Test coverage trends

### Risk Aggregation

Risks identified in individual products (in `product repo .claude/delivery/` risk registers) are aggregated at the portfolio level. This enables leadership to see:

- Shared risks across products (e.g., dependency on a single external API)
- Resource conflicts (e.g., two products need the same shared service upgraded)
- Timeline risks (e.g., a product is behind and may delay a dependent product)

### Audit Trail

Every governance decision is logged. The portfolio can produce an audit trail showing:
- Who (which agent) made each decision
- What governance gate was applied
- Whether it passed or failed
- What action was taken on failure
- When the decision was made

This is critical for regulated industries (healthcare, finance, government) where software development processes must be auditable.

## Scaling Considerations

### Small Org (1-5 products)

- Single factory repo, manual upgrades
- CoE is 1 person (part-time)
- Portfolio tracking in registry.json
- Monthly review of learnings

### Medium Org (5-20 products)

- Factory repo with CI/CD for releases
- CoE is 2-3 people (dedicated)
- Automated portfolio health dashboard
- Weekly review of learnings
- Standardized upgrade cadence (monthly)

### Large Org (20+ products)

- Factory repo with automated testing and staged rollouts
- CoE is 4-6 people (dedicated team)
- Real-time portfolio dashboard with alerting
- Continuous learning curation with ML-assisted pattern detection
- Staggered upgrade rollout (canary -> early adopters -> general availability)
- Product-specific factory extensions versioned separately
