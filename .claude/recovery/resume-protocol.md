# Resume Protocol

## Steps
1. **Read state**: Load `.claude/recovery/state.json`
2. **Validate state**: Check that `initialized` is true, identify `activeCommand` and `activeStep`
3. **Verify files**: Check that files referenced by the checkpoint actually exist
4. **Load memory**: Read relevant memory files for current context
5. **Verify queue**: Check `.claude/delivery/queue/` state is consistent
6. **Verify git**: Check git status — clean tree or expected in-progress changes
7. **Report**: Show user where we're resuming from
8. **Continue**: Execute from the checkpoint step

## If State is Corrupted
1. Check `failure-log.md` for last known good state
2. Check git log for last committed work
3. Manually set state.json to last known good values
4. Re-run the active command from the beginning of the current step
