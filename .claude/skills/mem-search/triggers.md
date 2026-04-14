# Triggers: mem-search

## Auto-invoke when
- User types `/mem-search <query>`
- Agent starts a new ticket (read past context first)
- User asks "what did we decide about X" or "have we done this before"
- Agent encounters a problem that may have been solved in a past session

## Do NOT invoke when
- Worker is confirmed down and user has not started it
- Query is about live code (use Grep/Glob instead)
- User asks about current session context (use conversation history)
