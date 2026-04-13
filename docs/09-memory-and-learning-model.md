# Memory and Learning Model

Memory lives in the PRODUCT REPO. Factory has org-level memory and factory-level learning patterns. That's it.

## Architecture

```
React UI → FastAPI → Postgres → Temporal → Memory Activities → Product Repo Files
```

Temporal activities read memory before agent execution. Temporal activities write learnings after agent completion.

## Where Memory Lives

### Product Repo (per product)
```
.claude/memory/
  session-log.md          — Current session log
  agent-context.json      — Cross-session context per agent
  patterns/
    debug-patterns.md     — Debug patterns learned
    review-patterns.md    — Review patterns learned
    test-patterns.md      — Testing patterns learned
    uiux-patterns.md      — UI/UX patterns learned
  decisions/
    technical.md          — Technical decisions + rationale
    process.md            — Process decisions + rationale
  blockers/
    resolved.md           — Previously resolved blockers
    active.md             — Currently active blockers
```

### Factory (org-level)
```
.claude/memory/
  org-context.md          — Organization-wide context and standards
```

Factory also maintains factory-level learning patterns that apply across all products. These are templates. Product repos get copies.

## Memory Lifecycle

### Read Before Execute

Every agent execution starts with a Temporal activity that loads relevant memory:

1. Query memory by tags, module, agent type
2. Load relevant debug/review/test/uiux patterns
3. Load relevant decisions and constraints
4. Load relevant learnings from `.claude/learning/`
5. Inject into agent context

No skipping. Temporal workflow enforces this.

### Write After Complete

Every agent completion ends with a Temporal activity that persists learnings:

1. Capture what was done and outcome
2. Capture patterns discovered (bugs, review findings, test insights)
3. Write structured entry to appropriate memory file
4. Tag with module, agent, category, timestamp

No skipping. Temporal workflow enforces this.

## Memory Entry Format

```json
{
  "id": "mem-20260122-001",
  "timestamp": "2026-01-22T14:30:00Z",
  "type": "pattern",
  "category": "debug",
  "agent": "backend-engineer",
  "module": "user-management",
  "title": "Connection pool exhaustion under concurrency",
  "resolution": "Increased pool size, added timeout, added circuit breaker",
  "tags": ["postgresql", "connection-pool", "concurrency"],
  "confidence": 0.9,
  "promoted_to": null
}
```

## Learning Promotion Pipeline

```
Session → Project → Factory (requires approval)
```

### Session to Project
Triggered when:
- Pattern observed 3+ times in same project
- Manually flagged as important by human or approver
- Resolved blocker that took significant effort
- Security finding that must be prevented

Memory agent summarizes pattern → writes to `.claude/learning/{category}.md` → all agents receive as context.

### Project to Factory
Triggered when:
- Pattern observed in 2+ products
- Represents universal best practice (not product-specific)
- **Requires approval**: CoE reviews and approves promotion

CoE reviews → identifies universal learnings → adds to factory template → next factory version includes it → products that upgrade get it.

No automatic promotion to factory level. Always requires approval.

## Memory Agent

The memory agent manages the full lifecycle:

| Responsibility | Description |
|---|---|
| Load context | Read relevant memory before agent execution |
| Capture learnings | Write structured learnings after agent completion |
| Promote patterns | Identify and promote recurring patterns |
| Deduplicate | Merge similar memory entries |
| Archive | Move old low-relevance entries to archive |
| Consolidate | Combine related entries into single learnings |
| Prune | Remove entries for deprecated modules |

Memory agent runs as Temporal activities. Maintenance runs at sprint boundaries.

## Agent Memory Responsibilities

| Agent | Reads | Writes |
|---|---|---|
| Product Manager | Product context, decisions, blockers | Requirement clarifications, scope decisions |
| Architect | Architecture decisions, patterns, constraints | ADRs, architecture patterns |
| Backend Engineer | Debug patterns, review patterns, security learnings | Debug patterns, implementation patterns |
| Frontend Engineer | UI/UX patterns, review patterns, design system | UI patterns, component patterns |
| QA Engineer | Test patterns, debug patterns | Test patterns, quality metrics |
| Security Reviewer | Security learnings, vulnerability patterns | Security findings |
| Checker | All patterns | Validation patterns, false positive patterns |
| Reviewer | Review patterns, all learnings | Review patterns, quality standards |
| Memory Agent | Everything | Everything |

## State Boundary

| Location | Contains |
|---|---|
| **Product Repo** `.claude/memory/` | All product memory: patterns, decisions, blockers |
| **Product Repo** `.claude/learning/` | Promoted project-level learnings |
| **Factory** `.claude/memory/org-context.md` | Org-wide context and standards |
| **Factory** | Factory-level learning pattern templates |

Factory never stores product memory. Product repo is the source of truth.
