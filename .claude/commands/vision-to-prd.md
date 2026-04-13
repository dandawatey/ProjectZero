# Command: /vision-to-prd

## Purpose
Generate structured PRD from raw product vision. User has idea, no formal doc.

## Trigger
User runs `/vision-to-prd` when they have vision but no PRD.

## Step-by-Step Process

### Step 1: Vision Intake
Ask user structured questions:
1. What problem you solve? For whom?
2. How does your solution work? (1-2 sentences)
3. Who are your users? (roles, not demographics)
4. What's the first thing users do? (core flow)
5. Any constraints? (compliance, platform, budget, timeline)
6. How do you make money? (revenue model)
7. Who are competitors? What makes you different?

Accept any format: bullet points, paragraphs, voice-dump, pitch deck text.

### Step 2: Structure Extraction
Product Manager agent extracts:
- Problem statement
- Solution overview
- User personas (from user descriptions)
- Feature list (from described flows)
- Non-functional requirements (from constraints)
- Success metrics (inferred from goals)
- MVP scope (core flow only)

### Step 3: Gap Analysis
Identify missing info. Ask user ONLY about critical gaps:
- Missing: users (who?) → ask
- Missing: revenue model → ask
- Missing: constraints → assume standard, note assumption
- Missing: competitors → skip, note as unknown

Do NOT ask 50 questions. Max 3 follow-ups.

### Step 4: PRD Generation
Generate PRD using `.claude/templates/prd-extract-template.md` format:
- Problem
- Solution
- Personas (2-3)
- Features (prioritized P1/P2/P3)
- NFRs
- Constraints
- Success metrics
- MVP scope (in/out)
- Timeline estimate

### Step 5: BMAD Generation
From PRD, auto-generate BMAD using `.claude/core/bmad.md` template:
- Business model canvas (fill what's known, mark unknowns)
- Target users (from personas)
- Value proposition
- Revenue model
- Technical constraints
- Success metrics
- MVP scope

### Step 6: User Review
Present PRD + BMAD to user. Ask:
- "Anything wrong?"
- "Anything missing?"
- "Ready to proceed?"

### Step 7: Store
Save approved PRD → `.claude/memory/domain-memory.md` (product repo)
Save approved BMAD → `.claude/memory/domain-memory.md` (product repo)
Hand off to `/spec`

## Required Inputs
- User's vision (any format, any length)

## Involved Agents
- Product Manager (extraction + structuring)
- spec-miner skill (document parsing)
- the-fool skill (challenge assumptions, find gaps)

## Outputs
- Generated PRD (full document)
- Generated BMAD (full document)
- Gap list (what was assumed vs confirmed)

## Failure Handling
- Vision too vague → ask 3 targeted questions, try again
- User can't answer → mark as "TBD, validate during spec"
- Max 2 rounds of follow-up before proceeding with assumptions noted

## Next Command
/bootstrap-product (if not done) or /spec (if product exists)
