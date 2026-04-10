# BMAD — Business Model Architecture Document

## Purpose
BMAD is the foundational intake document. It captures everything about the business before any code is written. No product begins without a completed BMAD.

## BMAD Sections

### 1. Business Model Canvas
- **Key Partners**: Who do we depend on? (payment providers, cloud vendors, data sources)
- **Key Activities**: What must we do? (develop platform, onboard users, maintain compliance)
- **Key Resources**: What do we need? (engineering team, cloud infra, domain expertise)
- **Value Propositions**: What problem do we solve? Why us?
- **Customer Relationships**: How do we acquire and retain? (self-service, dedicated support)
- **Channels**: How do users find and use us? (web app, mobile, API)
- **Customer Segments**: Who are our users? (personas with demographics, needs, behaviors)
- **Cost Structure**: What are our costs? (cloud, team, compliance, marketing)
- **Revenue Streams**: How do we make money? (subscription, usage, transaction fees)

### 2. Target Users
For each persona:
- Name and role
- Demographics
- Goals and motivations
- Pain points
- Current workarounds
- Success criteria

### 3. Value Proposition Detail
- Primary problem being solved
- How our solution is different
- Key differentiators vs competitors
- Unfair advantage (if any)

### 4. Revenue Model
- Pricing strategy (per-seat, usage-based, tiered, freemium)
- Price points with justification
- Expected conversion rates
- Unit economics (CAC, LTV, payback period)

### 5. Competitive Landscape
- Direct competitors (feature comparison matrix)
- Indirect competitors
- Market positioning
- Defensibility

### 6. Technical Constraints
- Compliance requirements (HIPAA, SOC2, GDPR, PCI)
- Performance requirements (latency, throughput, availability)
- Integration requirements (existing systems, APIs, data sources)
- Platform requirements (web, mobile, desktop, API)
- Scale requirements (users, data volume, geography)

### 7. Success Metrics
- North star metric
- Primary KPIs (3-5)
- Leading indicators
- Measurement approach

### 8. MVP Scope
- In-scope features (must-have for launch)
- Out-of-scope features (future phases)
- MVP success criteria
- Launch timeline

## BMAD Intake Process

1. **Receive**: User provides raw BMAD or PRD document
2. **Parse**: spec-miner skill extracts structured data into sections above
3. **Validate**: Check all 8 sections have content. Flag gaps.
4. **Clarify**: Ask user to fill gaps. Do not assume.
5. **Store**: Write structured BMAD to `.claude/memory/domain-memory.md`
6. **Confirm**: Present summary to user for approval
7. **Proceed**: Feed approved BMAD to `/spec` command

## Validation Checklist
- [ ] All 8 sections completed
- [ ] At least 2 user personas defined
- [ ] Revenue model has price points
- [ ] Technical constraints explicitly listed
- [ ] MVP scope has clear in/out boundaries
- [ ] Success metrics are measurable
- [ ] Competitive landscape has at least 2 competitors
- [ ] No section contains only "TBD" or placeholders
