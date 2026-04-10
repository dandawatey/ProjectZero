# Agent Protocol

## Receiving Work
1. Ralph moves queue item to active with agent assignment
2. Agent reads ticket details from queue item
3. Agent loads relevant memory from .claude/memory/
4. Agent begins work according to its contract

## Reporting Status
- On start: update active-ticket.json with agent and status
- On progress: checkpoint to state.json
- On completion: report to Ralph, move to next gate
- On failure: log to failure-log.md, report to Ralph

## Handoff Protocol
1. Completing agent writes output artifacts
2. Agent updates queue item status
3. Ralph detects completion, routes to next gate
4. Next agent receives item with all prior context

## Escalation
- Agent cannot resolve issue → report to Ralph with details
- Ralph attempts recovery (retry, reassign)
- If recovery fails → escalate to user with full context
