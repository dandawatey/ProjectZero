# 00 - Introduction to ProjectZeroFactory

## What Is ProjectZeroFactory?

ProjectZeroFactory is an **org-wide Claude operating system** for governed product development. It is not a coding assistant, a prompt library, or a chatbot wrapper. It is a complete operating system that sits inside a `.claude/` directory and transforms how software products are conceived, specified, built, tested, and released.

When you use a coding assistant, you open a file, ask for help, and get a suggestion. The assistant has no memory of your architecture, no awareness of your governance process, no understanding of your team's standards, and no ability to enforce quality gates. Each session starts from zero.

ProjectZeroFactory is fundamentally different. It provides:

- **Persistent memory** across sessions, projects, and even across your entire product portfolio
- **Governed workflows** that enforce BMAD, SPARC, and TDD at every stage
- **Specialized agents** (product manager, architect, engineers, QA, security, SRE) that each operate within defined scopes and hand off work through formal contracts
- **Integration with your existing tools** (JIRA, Confluence, GitHub) so that work is tracked, documented, and auditable
- **Recovery and resume** so that no work is lost when sessions end, context overflows, or networks fail
- **A learning system** that captures patterns, mistakes, and solutions and promotes them from session-level to project-level to factory-level knowledge

## What "Governed AI Factory" Means

The word "governed" is deliberate and central. In an ungoverned environment, an AI agent can:

- Write code that nobody reviews
- Skip tests because "it works"
- Ignore security concerns
- Produce architecture that contradicts organizational standards
- Lose context between sessions with no recovery path

ProjectZeroFactory eliminates all of these failure modes through governance at three levels:

### 1. Process Governance (BMAD + SPARC)

Every product begins with a **BMAD** (Business Model Architecture Document) that defines the business context, target market, value proposition, and success metrics. No code is written until the BMAD is loaded and validated.

Every feature follows the **SPARC** lifecycle:
- **S**pecification: What are we building and why?
- **P**seudocode/Design: How will it work at a logical level?
- **A**rchitecture: What are the technical decisions, patterns, and boundaries?
- **R**ealization: Build it, test it, check it
- **C**ompletion: Release it, monitor it, learn from it

### 2. Quality Governance (Maker-Checker-Reviewer-Approver)

No artifact moves forward without passing through the governance chain:
- The **Maker** (an engineering agent) produces the work
- The **Checker** validates it against the specification and contract
- The **Reviewer** examines it for quality, security, and standards compliance
- The **Approver** gives final sign-off before it can be merged or released

### 3. Operational Governance (No Ticket No Work)

Every piece of work traces back to a JIRA ticket (or local equivalent). There is no ad-hoc coding, no "quick fixes" that bypass the process. This ensures:
- Full traceability from business requirement to deployed code
- Accurate velocity and burndown tracking
- No orphaned code that nobody owns

## How the Factory Differs from a Coding Assistant

| Dimension | Coding Assistant | ProjectZeroFactory |
|---|---|---|
| Scope | Single file or function | Entire product lifecycle |
| Memory | None between sessions | Persistent across sessions and projects |
| Governance | None | BMAD + SPARC + TDD + Maker-Checker-Reviewer-Approver |
| Agents | One generic assistant | 22+ specialized agents with defined roles |
| Integration | Copy-paste | JIRA, Confluence, GitHub native |
| Recovery | Start over | Checkpoint and resume from last known good state |
| Learning | None | Session -> Project -> Factory knowledge promotion |
| Quality | Whatever the user accepts | Enforced gates at every stage |
| Traceability | None | Ticket -> Story -> Branch -> PR -> Release |

## Who Should Use This

ProjectZeroFactory is designed for:

- **Product teams** building SaaS applications, internal tools, or platform services
- **Engineering organizations** that want consistent, governed development across multiple products
- **Center of Excellence teams** that define standards and want to enforce them through tooling rather than documentation
- **Solo developers** who want the rigor of a full team without hiring one

## Core Principles

1. **File-based, not database-based**: Everything lives in `.claude/` as Markdown and JSON files. No external database required for the factory itself. This makes it portable, versionable, and inspectable.

2. **Local-first, cloud-enhanced**: The factory works entirely offline. JIRA, Confluence, and GitHub integrations enhance it but are never required. When integrations are unavailable, the factory falls back to local file representations.

3. **Template-to-instance**: The factory repo is a template. Each product gets its own clone. The factory can be upgraded independently of any product instance.

4. **Opinionated but extensible**: The factory ships with strong defaults (SPARC workflow, specific agent roles, TDD requirement). These can be configured per-product but the defaults represent battle-tested practices.

5. **Observable**: Every agent action, every governance decision, every recovery event is logged. You can audit what happened, when, and why.

## What Comes Next

- **[01 - How ProjectZeroFactory Works](01-how-projectzerofactory-works.md)** explains the architecture
- **[02 - How to Start a New Product](02-how-to-start-a-new-product.md)** gets you building immediately
- **[03 - Org Operating Model](03-org-operating-model.md)** explains multi-project governance
- **[14 - Command Reference](14-command-reference.md)** is the complete command catalog
- **[15 - Example New Product Flow](15-example-new-product-flow.md)** walks through a realistic end-to-end scenario
