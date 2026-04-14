# Skill: mem-search — Persistent Memory Search

## Purpose
Query project history stored by claude-mem across past sessions using 3-layer progressive disclosure. Cheap search first; full fetch only for selected IDs.

## Usage
```
/mem-search <query>
/mem-search timeline <observation-id>
/mem-search fetch <id1> [id2] [id3...]
```

## Instructions

You are executing a mem-search against the claude-mem worker at http://localhost:${CLAUDE_MEM_PORT:-37777}.

### Layer 1 — Search (do this first, always)
```
GET http://localhost:37777/search?q={query}&limit=10
```
Present results as numbered list: ID | timestamp | snippet | score
Show token cost estimate: (~50 tokens)

### Layer 2 — Timeline (only if user wants context)
```
GET http://localhost:37777/timeline?id={obs_id}&window=5
```
Show: 5 observations before and after the target
Show token cost estimate: (~200 tokens)

### Layer 3 — Fetch (only for IDs user selects)
```
POST http://localhost:37777/fetch
Body: {"ids": ["id1", "id2"]}
```
Show: full content of selected observations only

## Progressive Disclosure Rule
ALWAYS start with Layer 1.
Only go to Layer 2/3 if user explicitly asks for more detail.
Always show token cost before fetching.
Never fetch all memories at once — that defeats the purpose.

## Privacy
Observations tagged `<private>` are excluded from all search results automatically.

## If worker not running
Show: "claude-mem worker not running. Start with: npx claude-mem start"
Show: "Or check if CLAUDE_MEM_PORT is set correctly (default: 37777)"

## Citation format
When referencing a past observation in your response, cite it as: [obs:abc123]

## Stage Mapping
Used during: all stages (always read before acting, write after completing)

## Integration
Available to all agents. Invoke before starting any ticket to recall past context.
