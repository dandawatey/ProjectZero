# Workflow: Recovery

## Trigger
Work interruption: IDE crash, context overflow, network failure, validation failure

## Steps
1. **Identify**: Determine failure class (from recovery model)
2. **Load**: Read `.claude/recovery/state.json` for last checkpoint
3. **Validate**: Verify current state matches checkpoint expectations
4. **Decide**: Determine recovery action:
   - Retry (same action, incremented retry count)
   - Rollback (revert to last known good state)
   - Escalate (notify user, too many retries)
5. **Execute**: Perform recovery action
6. **Verify**: Confirm recovery successful (state is valid)
7. **Continue**: Resume from checkpoint

## Retry Limits
- Max 3 retries for validation failures
- Max 5 retries for integration failures
- 1 retry for context overflow (must start new session)
- Unlimited for IDE restart (just resume)
