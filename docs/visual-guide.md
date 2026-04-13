# ProjectZero — Visual Guide

## The Big Picture

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│                    P R O J E C T Z E R O                        │
│              Managed AI Agent Platform for Products              │
│                                                                 │
│  ┌───────────┐   ┌───────────┐   ┌──────────┐   ┌───────────┐ │
│  │  React    │──▶│  FastAPI  │──▶│ Postgres │──▶│ Temporal  │ │
│  │  Control  │   │  Backend  │   │  State   │   │  Engine   │ │
│  │  Tower    │◀──│  API      │◀──│  Truth   │◀──│  Execute  │ │
│  └───────────┘   └───────────┘   └──────────┘   └─────┬─────┘ │
│       │                                                │       │
│       │              SEE EVERYTHING                     │       │
│       │              CONTROL EVERYTHING                 ▼       │
│       │                                          ┌───────────┐ │
│       └─────────────────────────────────────────▶│  AI       │ │
│                    APPROVE / REJECT               │  Agents   │ │
│                                                   │  (35)     │ │
│                                                   └───────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

---

## How To Use (Step by Step)

```
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║   YOU ──▶ Clone Factory ──▶ Create Product ──▶ Build Features    ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝


   STEP 1                STEP 2                STEP 3
   ══════                ══════                ══════

   ┌──────────┐     ┌──────────────┐     ┌──────────────┐
   │  Clone   │     │  Bootstrap   │     │  Build via   │
   │  Factory │────▶│  Product     │────▶│  Workflows   │
   │  Repo    │     │  (own repo)  │     │  (per feature)│
   └──────────┘     └──────────────┘     └──────────────┘
   /factory-init    /bootstrap-product    /implement
```

---

## Complete Phase Flow

```
    PHASE 0          PHASE 1          PHASE 2a         PHASE 2b
   ┌────────┐      ┌──────────┐     ┌──────────┐     ┌──────────┐
   │FACTORY │      │ CREATE   │     │ VISION   │     │ BUSINESS │
   │ INIT   │─────▶│ PRODUCT  │──┬─▶│ → PRD    │────▶│ DISCOVERY│
   └────────┘      └──────────┘  │  └──────────┘     └────┬─────┘
                                 │   (if no PRD)          │
                                 │                        │
                                 │   (if have PRD)        │
                                 └────────────────────────┘
                                                          │
                                                          ▼
    PHASE 3          PHASE 4          PHASE 5          PHASE 6
   ┌────────┐      ┌──────────┐     ┌──────────┐     ┌──────────┐
   │  SPEC  │─────▶│  ARCH    │────▶│ IMPLEMENT│────▶│ QUALITY  │
   │        │      │          │     │ (repeat  │     │ & RELEASE│
   │ /spec  │      │  /arch   │     │  per     │     │          │
   └────────┘      └──────────┘     │  feature)│     │ /check   │
                                    │ /implement│     │ /review  │
                                    └──────────┘     │ /approve │
                                                     │ /release │
                                                     └────┬─────┘
                                                          │
                                                          ▼
    PHASE 7          PHASE 8
   ┌──────────┐     ┌──────────┐
   │ BUSINESS │     │OPERATIONS│
   │ PLANNING │────▶│          │
   │          │     │ /monitor │
   │ financials│     │ /optimize│
   │ pitch deck│     └──────────┘
   │ GTM      │          │
   └──────────┘          │
                         ▼
                    ┌──────────┐
                    │  NEXT    │
                    │ FEATURE  │──── loop back to Phase 5
                    └──────────┘
```

---

## Feature = Workflow (Every Feature Goes Through This)

```
    ┌─────────────────────────── TEMPORAL WORKFLOW ───────────────────────────┐
    │                                                                         │
    │  ①        ②        ③        ④         ⑤         ⑥       ⑦      ⑧     │
    │  ●───────●───────●───────●────────●─────────●───────●──────●───── │
    │  │       │       │       │        │         │       │      │      │
    │ INTAKE  SPEC   DESIGN  ARCH    IMPLEMENT   TEST  REVIEW APPROVE  │
    │  │       │       │       │        │         │       │      │      │
    │  ▼       ▼       ▼       ▼        ▼         ▼       ▼      ▼      │
    │ Product Product Architect Architect Engineer  QA    Checker Human  │
    │ Manager Manager                    (TDD)   Engineer Reviewer      │
    │                                                    Approver       │
    │                                                                   │
    │  ⑨              ⑩                                                 │
    │  ●─────────────●                                                  │
    │  │             │                                                  │
    │ RELEASE     COMPLETE                                              │
    │ READINESS                                                         │
    │  │             │                                                  │
    │  ▼             ▼                                                  │
    │ Release     DONE ✓                                                │
    │ Manager                                                           │
    └───────────────────────────────────────────────────────────────────┘
```

---

## Approval Chain (Every Artifact)

```
    ┌────────┐       ┌─────────┐       ┌──────────┐       ┌──────────┐
    │ MAKER  │──────▶│ CHECKER │──────▶│ REVIEWER │──────▶│ APPROVER │
    │        │       │         │       │          │       │          │
    │ Creates│       │ Tests?  │       │ Quality? │       │ Business?│
    │ work   │       │ Lint?   │       │ Arch?    │       │ Ready?   │
    │        │       │ Security│       │ Coverage?│       │          │
    └────────┘       └────┬────┘       └────┬─────┘       └────┬─────┘
                          │                 │                   │
                     FAIL │            FAIL │              FAIL │
                          ▼                 ▼                   ▼
                    ┌──────────┐      ┌──────────┐       ┌──────────┐
                    │ Back to  │      │ Back to  │       │ Back to  │
                    │ MAKER    │      │ MAKER    │       │ MAKER    │
                    │ (specific│      │ (specific│       │ (specific│
                    │ feedback)│      │ feedback)│       │ feedback)│
                    └──────────┘      └──────────┘       └──────────┘
```

---

## What You See in Control Tower (React UI)

```
┌──────────────────────────────────────────────────────────────────────┐
│  🏭 ProjectZero Control Tower                                        │
├──────────┬───────────────────────────────────────────────────────────┤
│          │                                                           │
│ Dashboard│   ┌─────┐  ┌─────┐  ┌─────┐  ┌─────┐  ┌─────┐          │
│ Workflows│   │  3  │  │ 12  │  │  1  │  │  0  │  │  2  │          │
│ Approvals│   │ACTIVE│  │DONE │  │FAIL │  │BLOCK│  │PEND │          │
│ Agents   │   └─────┘  └─────┘  └─────┘  └─────┘  └─────┘          │
│ Artifacts│                                                           │
│ Audit Log│   Recent Workflows                                        │
│ Failures │   ┌────────────────┬──────────┬───────────┬──────────┐   │
│          │   │ Feature        │ Stage    │ Status    │ Agent    │   │
│          │   ├────────────────┼──────────┼───────────┼──────────┤   │
│          │   │ Vitals Dash    │ testing  │ ●RUNNING  │ QA Eng   │   │
│          │   │ Auth Module    │ review   │ ●WAITING  │ Reviewer │   │
│          │   │ Patient CRUD   │ complete │ ●DONE     │ —        │   │
│          │   │ Alert System   │ arch     │ ●RUNNING  │ Architect│   │
│          │   └────────────────┴──────────┴───────────┴──────────┘   │
│          │                                                           │
│          │   Workflow Detail: Vitals Dashboard                        │
│          │   ┌──┐ ┌──┐ ┌──┐ ┌──┐ ┌──┐ ┌──┐ ┌──┐ ┌──┐ ┌──┐ ┌──┐  │
│          │   │✓ │─│✓ │─│✓ │─│✓ │─│✓ │─│● │─│○ │─│○ │─│○ │─│○ │  │
│          │   └──┘ └──┘ └──┘ └──┘ └──┘ └──┘ └──┘ └──┘ └──┘ └──┘  │
│          │   IN  SPEC DSGN ARCH IMPL TEST REVW APRV REL  DONE    │
│          │                                                           │
└──────────┴───────────────────────────────────────────────────────────┘

Legend: ✓ = done   ● = active   ○ = pending
```

---

## Agent Teams

```
                              ┌─────────────┐
                              │  CXO TEAM   │
                              │ CEO CTO CPO │
                              │ CFO CMO CRO │
                              └──────┬──────┘
                                     │
               ┌─────────────────────┼─────────────────────┐
               │                     │                     │
        ┌──────┴──────┐      ┌──────┴──────┐       ┌──────┴──────┐
        │  COFOUNDER  │      │   PRODUCT   │       │  MARKETING  │
        │  TEAM       │      │   TEAM      │       │  TEAM       │
        │             │      │             │       │             │
        │ Strategist  │      │ PM          │       │ Strategist  │
        │ Tech CoF    │      │ Analyst     │       │ Content     │
        │ Ralph ⚙️     │      │ UX Research │       └─────────────┘
        └──────┬──────┘      └──────┬──────┘
               │                    │
        ┌──────┴────────────────────┴──────┐
        │          ENGINEERING TEAM         │
        │                                   │
        │  Architect  Backend   Frontend    │
        │  Data       DevOps    QA    SRE  │
        └──────────────┬────────────────────┘
                       │
            ┌──────────┼──────────┐
            │          │          │
     ┌──────┴──────┐  │   ┌──────┴──────┐
     │ GOVERNANCE  │  │   │   SALES     │
     │ TEAM        │  │   │   TEAM      │
     │             │  │   │             │
     │ Checker     │  │   │ Strategist  │
     │ Reviewer    │  │   │ Cust Success│
     │ Approver    │  │   └─────────────┘
     │ Security    │  │
     │ UX Review   │  │
     └─────────────┘  │
                      │
               ┌──────┴──────┐
               │ OPERATIONS  │
               │ TEAM        │
               │             │
               │ Release Mgr │
               │ FinOps      │
               │ Integration │
               │ Validators  │
               │ Pipeline    │
               │ Memory      │
               └─────────────┘
```

---

## Vision → Product (If You Start With Just an Idea)

```
    ┌──────────────┐
    │ "I want to   │
    │  build a     │
    │  patient     │
    │  monitoring  │
    │  app"        │
    └──────┬───────┘
           │
           ▼
    ┌──────────────┐     System asks 5-7 questions
    │ /vision-to-  │     (max 3 follow-ups)
    │    prd       │─────────────────────────────┐
    └──────┬───────┘                             │
           │                                     │
           ▼                                     ▼
    ┌──────────────┐                      ┌──────────────┐
    │  Generated   │                      │  Generated   │
    │  PRD         │                      │  BMAD        │
    │  (structured)│                      │  (business)  │
    └──────┬───────┘                      └──────┬───────┘
           │                                     │
           └──────────────┬──────────────────────┘
                          │
                          ▼
    ┌──────────────────────────────────────┐
    │ /business-docs --phase discovery     │
    │                                      │
    │  ├── TAM-SAM-SOM  ($2.3B market)    │
    │  ├── Competitors   (3 found)         │
    │  ├── Team Plan     (7 people)        │
    │  └── Business Model (SaaS $49/seat)  │
    └──────────────────┬───────────────────┘
                       │
                       ▼
              ┌─────────────────┐
              │ Ready to build! │
              │                 │
              │ /spec → /arch   │
              │ → /implement    │
              └─────────────────┘
```

---

## Business Docs: When To Generate What

```
    BEFORE BUILD                           AFTER BUILD
    ════════════                           ══════════

    Phase 2b                               Phase 7
    /business-docs                         /business-docs
      --phase discovery                      --phase planning

    ┌──────────────────┐                   ┌──────────────────┐
    │ TAM-SAM-SOM      │                   │ Financial        │
    │ (market size)    │                   │ Projections      │
    ├──────────────────┤                   ├──────────────────┤
    │ Competitive      │                   │ Build & Run      │
    │ Analysis         │                   │ Costing          │
    ├──────────────────┤    ┌─────────┐    ├──────────────────┤
    │ Team             │    │ BUILD   │    │ GTM Strategy     │
    │ Composition      │───▶│ PRODUCT │───▶│                  │
    ├──────────────────┤    │         │    ├──────────────────┤
    │ Business Model   │    │ Phases  │    │ Pitch Deck       │
    │ Canvas           │    │ 3-6     │    │ (10-12 slides)   │
    └──────────────────┘    └─────────┘    ├──────────────────┤
                                           │ Investor Data    │
    WHY BEFORE:                            │ Room (optional)  │
    Informs WHAT to build                  └──────────────────┘

                                           WHY AFTER:
                                           Needs real scope,
                                           architecture, and
                                           cost data to be
                                           accurate
```

---

## Recovery: When Things Break

```
    ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
    │ IDE CRASH   │     │ WORKFLOW    │     │ CONTEXT     │
    │             │     │ FAILED      │     │ OVERFLOW    │
    └──────┬──────┘     └──────┬──────┘     └──────┬──────┘
           │                   │                    │
           ▼                   ▼                    ▼
    ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
    │  /resume    │     │  Auto-retry │     │  Checkpoint  │
    │             │     │  (max 3)    │     │  → new       │
    │  Reads last │     │             │     │    session   │
    │  Temporal   │     │  If still   │     │  → /resume   │
    │  checkpoint │     │  fails:     │     │              │
    │  → continue │     │  escalate   │     │  Temporal    │
    │             │     │  to human   │     │  keeps state │
    └─────────────┘     └─────────────┘     └─────────────┘

    TEMPORAL NEVER LOSES STATE
    Every step checkpointed
    Every retry tracked
    Every failure logged
```

---

## Governance Rules (Non-Negotiable)

```
    ╔════════════════════════════════════════════════╗
    ║                                                ║
    ║   ❌ No Workflow  →  No Build                  ║
    ║   ❌ No Ticket    →  No Work                   ║
    ║   ❌ No Tests     →  No Merge                  ║
    ║   ❌ No Review    →  No Deploy                 ║
    ║   ❌ No Approval  →  No Release                ║
    ║                                                ║
    ║   ✓  TDD mandatory (test first)               ║
    ║   ✓  80% coverage minimum                     ║
    ║   ✓  4-eye principle (maker→checker→           ║
    ║      reviewer→approver)                        ║
    ║   ✓  Everything auditable                      ║
    ║   ✓  Everything resumable                      ║
    ║                                                ║
    ╚════════════════════════════════════════════════╝
```

---

## Quick Reference Card

```
┌─────────────────────────────────────────────────────┐
│  PROJECTZERO QUICK REFERENCE                        │
├─────────────────────────────────────────────────────┤
│                                                     │
│  START:    git clone → /factory-init                │
│  CREATE:   /bootstrap-product                       │
│  NO PRD:   /vision-to-prd                          │
│  BIZ DOCS: /business-docs --phase discovery|planning│
│  SPEC:     /spec                                    │
│  DESIGN:   /arch                                    │
│  BUILD:    /implement  (per feature)                │
│  QUALITY:  /check → /review → /approve              │
│  SHIP:     /release                                 │
│  WATCH:    /monitor → /optimize                     │
│  BROKE:    /resume                                  │
│  AUDIT:    /factory-audit                           │
│                                                     │
│  UI:       http://localhost:3000  (control tower)   │
│  API:      http://localhost:8000  (backend)         │
│  TEMPORAL: http://localhost:8233  (temporal UI)     │
│                                                     │
└─────────────────────────────────────────────────────┘
```
