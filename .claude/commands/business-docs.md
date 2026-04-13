# Command: /business-docs

## Purpose
Generate full business document suite. Two phases: Discovery (before PRD) and Planning (after PRD).

## Trigger
User runs `/business-docs` at any point. System detects phase based on PRD existence.

## Phase 1: Business Discovery (pre-PRD)

Run when: no PRD exists yet, or user starting fresh.

### Step 1: TAM-SAM-SOM Analysis
- **Total Addressable Market**: Global market size for problem category
- **Serviceable Addressable Market**: Market segment we can reach
- **Serviceable Obtainable Market**: Realistic capture in 1-3 years
- Inputs: industry, geography, user type, pricing assumption
- Output: TAM-SAM-SOM document with sources and methodology

### Step 2: Competitive Analysis
- Direct competitors (feature matrix comparison)
- Indirect competitors (alternative solutions)
- Competitive advantages / moats
- Positioning map (price vs capability)
- Output: Competitive landscape document

### Step 3: Team Composition
- Required roles for MVP build
- Current team vs gaps
- Hiring plan with timeline
- Cost per role (loaded)
- Build vs outsource decisions
- Output: Team plan document

### Step 4: Initial Business Model
- Revenue model (subscription/usage/transaction/freemium)
- Pricing tiers (draft, validated after PRD)
- Unit economics targets (CAC, LTV, payback)
- Key assumptions listed
- Output: Business model canvas

→ These 4 docs feed into BMAD → which feeds into PRD.

## Phase 2: Business Planning (post-PRD)

Run when: PRD exists and architecture is at least drafted.

### Step 5: Financial Projections
- Revenue forecast (12-month, 3-year, 5-year)
- Cost structure (cloud, team, tools, compliance, marketing)
- Cash flow projection
- Burn rate and runway
- Break-even analysis
- Key assumptions table
- Sensitivity analysis (best/base/worst)
- Output: Financial model document

### Step 6: Build & Run Costing
- Development cost (team × time × rate)
- Infrastructure cost (cloud estimate from architecture)
- Third-party service costs (APIs, tools, licenses)
- Compliance costs (audits, certifications)
- Ongoing operational cost (support, monitoring, maintenance)
- Total cost to MVP
- Monthly run rate post-launch
- Output: Costing breakdown document

### Step 7: Go-to-Market Strategy
- Launch plan (beta → GA → scale)
- Channel strategy (direct, content, partnerships, paid)
- Messaging framework per persona
- Pricing finalization
- Sales process (if B2B)
- Success metrics per channel
- 90-day launch plan
- Output: GTM strategy document

### Step 8: Pitch Deck
- Problem (1 slide)
- Solution (1 slide)
- Market size — TAM-SAM-SOM (1 slide)
- Product (2 slides — screenshots/mockups)
- Business model (1 slide)
- Traction / validation (1 slide)
- Competition (1 slide)
- Team (1 slide)
- Financials (1 slide)
- Ask / use of funds (1 slide)
- Output: 10-12 slide pitch deck content (markdown)

### Step 9: Investor Data Room (optional)
- Packages: pitch deck, financials, team bios, TAM analysis, competitive analysis, product demo, legal docs checklist
- Output: Data room index document

## Required Inputs
Phase 1: Vision or market context from user
Phase 2: Approved PRD + architecture (at minimum PRD)

## Involved Agents
- Cofounder Strategist (market analysis, business model)
- CFO (financial projections, costing)
- CMO (GTM strategy, messaging)
- CRO (pricing, sales process)
- Product Manager (product positioning)
- CPO (product strategy alignment)

## Outputs
Up to 9 documents, generated in order.

## Failure Handling
- Missing data → ask user (max 3 questions per doc)
- Assumptions clearly marked in every document
- User reviews each doc before next generates

## Next Command
Phase 1 → `/vision-to-prd` or `/bootstrap-product`
Phase 2 → `/release` preparation
