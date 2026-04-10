# Workflow: Ralph Loop

## Purpose
Ralph Controller's continuous orchestration loop during active work.

## Loop
```
while (active_work || queued_work):
  1. Check queue state (ready, active, blocked, completed, failed)
  2. Assign ready items to available agents (respect max parallel)
  3. Monitor active items for completion or failure
  4. Detect blocked items (dependency not met, timeout exceeded)
  5. Handle failures (retry, reassign, escalate)
  6. Move completed items through governance chain
  7. Update reports (progress, queue status, agent status)
  8. Check for user interrupts or commands
  9. Repeat
```

## Assignment Logic
1. Check available agent slots (max - active)
2. Get highest priority ready items
3. Match item type to agent specialization
4. Verify no dependency conflicts
5. Move item to active, assign agent
6. Notify agent with ticket details

## Block Detection
- Active item with no progress for > 30 minutes → check in
- Active item with no progress for > 2 hours → escalate
- Blocked item with no dependency change for > 4 hours → alert user
- Failed item with retry count >= 3 → escalate to user
