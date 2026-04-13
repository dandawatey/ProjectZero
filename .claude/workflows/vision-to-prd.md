# Workflow: Vision to PRD

## Purpose
Generate structured PRD + BMAD from raw product vision. For users who have an idea but no formal document.

## Entry Criteria
User has product vision in any format (text, bullets, pitch, conversation).

## Stages

| # | Stage | Agent | What Happens |
|---|-------|-------|-------------|
| 1 | Vision Intake | Product Manager | Parse raw vision, extract key elements |
| 2 | Structure Extraction | Product Manager + spec-miner | Map to PRD sections |
| 3 | Gap Analysis | the-fool | Find missing info, generate max 3 follow-up questions |
| 4 | PRD Generation | Product Manager | Full PRD from template |
| 5 | BMAD Generation | Product Manager | Full BMAD from template |
| 6 | User Review | Human (signal) | User approves or requests changes |
| 7 | Store & Handoff | Memory Agent | Save to product memory, hand off to /spec |

## Temporal Implementation
- Workflow: `VisionToPRDWorkflow` in `platform/temporal/workflows/vision_to_prd.py`
- Signals: `provide_answers` (follow-up), `approve_review` (user OK)
- Queries: `current_stage`, `generated_prd`, `generated_bmad`
- Artifacts: PRD document, BMAD document

## Trigger
- `/vision-to-prd` command
- `/bootstrap-product` when user says "I don't have a PRD"
- API: POST /api/v1/workflows/start with type "vision_to_prd"

## Flow Rules
- Max 3 follow-up questions during gap analysis
- 30 min timeout on follow-up answers → proceed with assumptions
- Assumptions clearly marked in generated docs
- User review required before proceeding
