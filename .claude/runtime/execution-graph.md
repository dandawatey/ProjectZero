# Execution Graph

The execution graph is a DAG (Directed Acyclic Graph) of work items and their dependencies.

## Structure
```
Epic A
├── Story A1 (no deps) → ready
├── Story A2 (depends on A1) → blocked
└── Story A3 (depends on A1) → blocked

Epic B
├── Story B1 (no deps) → ready
└── Story B2 (depends on A1, B1) → blocked
```

## Rules
- Items with no unmet dependencies are "ready"
- Items with unmet dependencies are "blocked"
- When a dependency completes, re-evaluate blocked items
- Circular dependencies are an architecture error — reject
- Ralph Controller maintains this graph during /implement
