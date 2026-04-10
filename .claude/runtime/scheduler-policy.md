# Scheduler Policy

## Priority
- P1 (Critical) items always processed first
- Within same priority: FIFO order
- Starvation prevention: items waiting > 1 hour get priority boost

## Parallelism
- Max parallel agents: 3 (from settings.json, configurable)
- One agent per ticket (no splitting)
- Multiple tickets can be active if agents available

## Dependencies
- Only assign items whose dependencies are all in "completed" state
- Re-evaluate blocked items when any item completes
- Circular dependencies are rejected (architecture error)

## Timeouts
- Active item no progress > 30 minutes → Ralph checks in
- Active item no progress > 2 hours → Ralph escalates
- Blocked item no change > 4 hours → Ralph alerts user

## Queue Processing
```
1. Read ready.json
2. Sort by priority (P1 first), then by age (oldest first)
3. For each item: check dependencies met, check agent available
4. Assign up to max_parallel_agents items
5. Move assigned items to active.json
6. Wait for completion signals
7. On completion: evaluate blocked items, assign next batch
```
