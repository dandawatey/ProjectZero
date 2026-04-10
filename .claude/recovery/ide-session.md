# IDE Session Recovery

## After IDE Restart
1. Open terminal in project root
2. Run `/resume` to reload last state
3. Verify git status matches expectations
4. Verify .env is loaded
5. Continue from last checkpoint

## After Context Overflow
1. Session context has been lost
2. Run `/resume` — it reads state.json and reloads context
3. Previous conversation is not available, but state is preserved
4. Continue from checkpoint with fresh context

## After Machine Restart
1. Open project in IDE
2. Verify git state (no unexpected changes)
3. Run `/resume`
4. If resume fails, check `.claude/recovery/failure-log.md` for last known state
