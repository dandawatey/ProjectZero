# ProjectZero Factory — Root CLAUDE.md

## Operating Contract
See [.claude/CLAUDE.md](.claude/CLAUDE.md) for full org-wide operating contract.

## Caveman Mode (ACTIVE)

Respond terse like smart caveman. All technical substance stay. Only fluff die.

Rules:
- Drop articles (a/an/the), filler (just/really/basically/actually/simply), pleasantries, hedging
- Fragments OK. Short synonyms preferred. Technical terms exact
- Code blocks unchanged. Errors quoted exact
- Pattern: [thing] [action] [reason]. [next step]
- Abbreviate where clear: DB/auth/config/req/res/fn/impl
- Use arrows for causality: X → Y
- No "Sure!", no "I'd be happy to", no "Let me explain"
- Output format stays structured when asked (STEP/ACTION/FILES/STATUS)

Auto-clarity: drop caveman for security warnings, irreversible action confirmations, or when user is confused. Resume after.

## graphify-ts

This project has a graphify-ts knowledge graph at .claude/graphify-out/.

Rules:
- Before answering architecture or codebase questions, read .claude/graphify-out/GRAPH_REPORT.md for god nodes and community structure
- If .claude/graphify-out/wiki/index.md exists, navigate it instead of reading raw files
- Use only Node.js / TypeScript tooling in this repository
- After modifying code files, refresh graph: `graphify-ts generate . --wiki --svg` then move output to `.claude/graphify-out/`
- Graph output path: .claude/graphify-out/

## Key Architecture

```
React (Control Tower) → FastAPI (API) → Postgres (State + Brain) → Temporal (Engine) → Agents
```

## Brain (Persistent Memory)

ProjectZero has a Postgres-backed brain at `/api/v1/brain/`:
- `/brain/memory` — persistent memories (factory + product scope)
- `/brain/decisions` — architecture and product decisions
- `/brain/patterns` — reusable patterns (proven approaches)
- `/brain/conversations` — chat/brainstorm/plan/implement per workflow step

Agents MUST read brain before action, write after action.

## Interaction Modes

Every workflow step supports 4 modes:
- **chat** — discuss, ask questions, clarify
- **brainstorm** — explore ideas, challenge assumptions
- **plan** — structure approach, define steps
- **implement** — execute, write code, generate artifacts

Mode stored in conversation. User switches via UI or signal.
