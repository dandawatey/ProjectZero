# 09 - Memory and Learning Model

## Overview

ProjectZeroFactory maintains persistent memory across sessions, projects, and the entire portfolio. The memory system ensures that no knowledge is lost between sessions, that agents learn from past work, and that patterns discovered in one project benefit all future projects.

## Memory Architecture

Memory is stored in four locations within `.claude/`:

```
.claude/memory/           # Active session and cross-session memory
.claude/memory_store/     # Indexed memory for fast retrieval
.claude/learning/         # Promoted learnings (project-level)
.claude/knowledge/        # Product-specific knowledge base
```

### .claude/memory/

This is the primary memory store. It contains structured Markdown and JSON files that persist across Claude sessions.

```
.claude/memory/
  session-log.md          # Current session log (what happened, decisions made)
  agent-context.json      # Cross-session context per agent
  patterns/
    debug-patterns.md     # Patterns learned from debugging
    review-patterns.md    # Patterns learned from code review
    test-patterns.md      # Patterns learned from testing
    uiux-patterns.md      # Patterns learned from UI/UX work
  decisions/
    technical.md          # Technical decisions and rationale
    process.md            # Process decisions and rationale
  blockers/
    resolved.md           # Previously resolved blockers (for reference)
    active.md             # Currently active blockers
```

### .claude/memory_store/

This is the indexed memory store, optimized for retrieval. It contains structured JSON files that agents query when they need context.

```
.claude/memory_store/
  index.json              # Master index of all memory entries
  by-module/              # Memory entries indexed by module
  by-agent/               # Memory entries indexed by agent
  by-pattern/             # Memory entries indexed by pattern type
  embeddings/             # Vector embeddings for semantic search (if enabled)
```

### .claude/learning/

This contains learnings that have been promoted from session-level to project-level. These are durable insights that should influence all future work on this product.

```
.claude/learning/
  architecture.md         # Architectural learnings
  coding.md               # Coding practice learnings
  testing.md              # Testing strategy learnings
  security.md             # Security learnings
  performance.md          # Performance optimization learnings
  process.md              # Process improvement learnings
  integration.md          # Integration (JIRA/Confluence/GitHub) learnings
```

### .claude/knowledge/

This contains product-specific reference material that agents consult.

```
.claude/knowledge/
  bmad.md                 # Business Model Architecture Document
  prd.md                  # Product Requirements Document
  product-context.md      # Product context summary
  adrs/                   # Architecture Decision Records
    ADR-001.md
    ADR-002.md
  glossary.md             # Product-specific terminology
  constraints.md          # Technical and business constraints
```

## Memory Lifecycle

### 1. Session Memory Capture

During every session, the memory-agent captures:

**Automatic captures** (happen without explicit invocation):
- Commands executed and their outcomes
- Errors encountered and how they were resolved
- Governance chain results (pass/fail/block with reasons)
- Agent handoff events
- Recovery checkpoints

**Agent-triggered captures** (agents write to memory during their work):
- Debug patterns: When the debug-skill resolves an issue, it logs the pattern
- Review patterns: When the reviewer finds a recurring issue, it logs the pattern
- Test patterns: When tests reveal a class of bugs, the pattern is logged
- Architecture patterns: When architectural decisions prove good or bad, the outcome is logged

### 2. Memory Entry Format

Every memory entry follows this structure:

```json
{
  "id": "mem-20260122-001",
  "timestamp": "2026-01-22T14:30:00Z",
  "type": "pattern",
  "category": "debug",
  "agent": "backend-engineer",
  "module": "user-management",
  "title": "PostgreSQL connection pool exhaustion under concurrent requests",
  "description": "When more than 50 concurrent requests hit the user registration endpoint, the connection pool (size 10) is exhausted, causing 503 errors.",
  "resolution": "Increased pool size to 20 and added connection timeout of 5s. Also added circuit breaker for database connections.",
  "tags": ["postgresql", "connection-pool", "concurrency", "performance"],
  "confidence": 0.9,
  "reuse_count": 0,
  "promoted_to": null
}
```

### 3. Memory Retrieval

Before starting any work, agents query the memory store for relevant context:

```
Agent: backend-engineer
Task: Implement user authentication API
Query: "authentication API patterns, security, PostgreSQL"

Memory agent returns:
- 3 relevant debug patterns (auth-related issues previously resolved)
- 2 architecture decisions (ADR on JWT vs. session tokens)
- 1 security learning (always hash passwords with bcrypt, minimum 12 rounds)
- 1 performance learning (connection pool sizing for auth endpoints)
```

The memory-agent uses a combination of:
- **Tag matching**: Exact match on tags
- **Keyword search**: Full-text search on titles and descriptions
- **Module affinity**: Prioritize memories from the same module
- **Recency weighting**: More recent memories rank higher
- **Semantic search**: If embeddings are enabled, use vector similarity

### 4. Pattern Categories

#### Debug Patterns (.claude/memory/patterns/debug-patterns.md)

Track recurring bugs and their resolutions:

```markdown
## Pattern: PostgreSQL Connection Pool Exhaustion

**First seen**: 2026-01-15
**Frequency**: 3 times across 2 modules
**Root cause**: Default pool size (10) insufficient for concurrent API endpoints
**Resolution**: Set pool size to max_connections * 0.8 / num_workers
**Prevention**: Add pool monitoring and alert at 80% utilization
```

#### Review Patterns (.claude/memory/patterns/review-patterns.md)

Track recurring code review findings:

```markdown
## Pattern: Missing Input Validation on API Endpoints

**First seen**: 2026-01-18
**Frequency**: 7 times across 3 modules
**Issue**: API endpoints accept raw input without Pydantic validation
**Standard**: All API endpoints MUST use Pydantic models for request validation
**Enforcement**: Checker now validates that all FastAPI routes have typed request models
```

#### Test Patterns (.claude/memory/patterns/test-patterns.md)

Track testing insights:

```markdown
## Pattern: E2E Tests Flaky Due to Race Conditions

**First seen**: 2026-01-20
**Frequency**: 5 times across UI modules
**Root cause**: Tests do not wait for API responses before asserting
**Resolution**: Always use page.waitForResponse() or page.waitForSelector() before assertions
**Template**: See .claude/data/fixtures/playwright-wait-pattern.ts
```

#### UI/UX Patterns (.claude/memory/patterns/uiux-patterns.md)

Track UI/UX insights:

```markdown
## Pattern: Form Validation Feedback Too Late

**First seen**: 2026-01-19
**Frequency**: 4 times across form-heavy modules
**Issue**: Validation errors only shown after form submission
**Resolution**: Implement inline validation on field blur
**Design system update**: Added FormField component with built-in blur validation
```

## Learning Promotion Pipeline

Learnings flow upward through three levels:

```
Session Memory  -->  Project Learning  -->  Factory Learning
(single session)     (single product)      (all products)
```

### Session -> Project Promotion

A memory entry is promoted to project learning when:
- It has been **observed 3+ times** in the same project
- It has been **manually marked** as important by a human or the approver agent
- It represents a **resolved blocker** that took significant effort to solve
- It represents a **security finding** that should be prevented going forward

Promotion process:
1. Memory-agent identifies candidate entries (frequency >= 3 or manually flagged)
2. Memory-agent summarizes the pattern into a learning entry
3. Learning entry is written to `.claude/learning/{category}.md`
4. All agents now receive this learning as context for related work

### Project -> Factory Promotion

A project learning is promoted to the factory when:
- It applies to **multiple products** (observed in 2+ product instances)
- It represents a **universal best practice** (not product-specific)
- The **CoE reviews and approves** the promotion

Promotion process:
1. CoE reviews project learnings from across the portfolio
2. CoE identifies learnings that are universally applicable
3. CoE adds the learning to the factory template
4. Next factory version includes the learning
5. Products that upgrade receive the learning automatically

### Learning Entry Format

```markdown
## Learning: Always Use Parameterized Queries

**Level**: Factory
**Category**: Security
**Source**: Observed in 4 products, promoted from ProductA (2026-02-15)
**Description**: Raw SQL string concatenation leads to SQL injection vulnerabilities. Always use parameterized queries or an ORM's query builder.
**Evidence**: 12 security findings across 4 products, all resolved by switching to parameterized queries.
**Action**: backend-engineer and checker now validate that no raw SQL string concatenation exists in database-accessing code.
**Tags**: sql-injection, security, database, owasp-a03
```

## Agent Learning Responsibilities

Each agent has specific memory responsibilities:

| Agent | Reads | Writes |
|---|---|---|
| product-manager | Product context, decisions, blockers | Requirement clarifications, scope decisions |
| architect | Architecture decisions, patterns, constraints | ADRs, architecture patterns, constraint updates |
| backend-engineer | Debug patterns, review patterns, security learnings | Debug patterns, implementation patterns |
| frontend-engineer | UI/UX patterns, review patterns, design system | UI patterns, component patterns |
| qa-engineer | Test patterns, debug patterns | Test patterns, quality metrics |
| security-reviewer | Security learnings, vulnerability patterns | Security findings, security patterns |
| checker | All patterns (for validation) | Validation patterns, false positive patterns |
| reviewer | Review patterns, all learnings | Review patterns, quality standards |
| memory-agent | Everything | Everything (memory lifecycle management) |

## Memory Configuration

Memory behavior is controlled by environment variables:

```env
ENABLE_MEMORY_PERSISTENCE=true   # Persist memory between sessions
```

And by files in `.claude/core/`:
- Memory retention policy (how long to keep session memories)
- Promotion thresholds (how many observations before auto-promotion)
- Embedding configuration (model, dimensions, if semantic search enabled)

## Memory Maintenance

Over time, memory grows. The memory-agent performs maintenance:

1. **Deduplication**: Merge similar memory entries
2. **Archival**: Move old, low-relevance entries to archive
3. **Consolidation**: Combine multiple related entries into a single learning
4. **Pruning**: Remove entries that are no longer relevant (e.g., patterns for deprecated modules)

Maintenance runs automatically at the end of each sprint or can be triggered manually.
