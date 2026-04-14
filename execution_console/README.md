# Claude Execution Console — PRJ0-56

Rich terminal sidecar for ProjectZero. Shows real-time Feature → Epic → Ticket → Workflow → Agent execution status.

## Architecture

```
FastAPI (port 8001)
  /api/v1/events     ← ingest from Claude hooks, Temporal, JIRA sync
  /api/v1/snapshot   ← roll-up status tree
  /api/v1/events/failed

SQLite (~/.projectzero/console.db)
  ← stores all events

Rich Live renderer
  ← polls snapshot, renders terminal tree
```

## Quick Start (Demo Mode)

No JIRA or Temporal required.

```bash
cd /path/to/ProjectZeroFactory
pip install rich fastapi uvicorn httpx pydantic python-dotenv
python execution_console/scripts/demo.py
```

## Full Mode

```bash
# Terminal 1: backend
uvicorn execution_console.app.main:app --port 8001

# Terminal 2: Rich renderer
python execution_console/scripts/start_console.py
```

## Emit Events

```bash
# From shell
curl -X POST http://localhost:8001/api/v1/events \
  -H "Content-Type: application/json" \
  -d '{"event_type":"ticket_status","ticket_id":"PRJ0-49","status":"RUNNING","pct":67.0,"agent":"impl-agent"}'

# Via Claude hook (auto, set env var)
export CLAUDE_CURRENT_TICKET=PRJ0-49
export CLAUDE_AGENT_NAME=impl-agent
# .claude/hooks/post_tool_use.sh fires on each tool use
```

## JIRA Connect

Set in `.env`:
```
JIRA_BASE_URL=https://isourceinnovation.atlassian.net
JIRA_USER_EMAIL=you@example.com
JIRA_API_TOKEN=your-token
```

Hierarchy is currently hard-coded in `state_engine.py::FEATURE_MAP`. Live JIRA fetch available via `jira_service.fetch_project_issues()`.

## Temporal Connect

Set in `.env`:
```
TEMPORAL_HOST=localhost:7233
TEMPORAL_NAMESPACE=default
TEMPORAL_UI_URL=http://localhost:8233
```

`temporal_service.fetch_running_workflows()` polls running executions. Deep links rendered in terminal (OSC 8 hyperlinks).

## Config

| Variable | Default | Description |
|---|---|---|
| `EXECUTION_CONSOLE_URL` | `http://localhost:8001` | Backend URL |
| `CONSOLE_DB_PATH` | `~/.projectzero/console.db` | SQLite path |
| `JIRA_BASE_URL` | — | JIRA instance URL |
| `JIRA_USER_EMAIL` | — | JIRA auth email |
| `JIRA_API_TOKEN` | — | JIRA API token |
| `TEMPORAL_HOST` | `localhost:7233` | Temporal gRPC host |
| `TEMPORAL_NAMESPACE` | `default` | Temporal namespace |
| `CLAUDE_CURRENT_TICKET` | — | Active ticket for hook tagging |
| `CLAUDE_AGENT_NAME` | `claude` | Agent name for hook tagging |

## Slash Command

Use `/console` in Claude Code to launch the console.

## Limitations

- JIRA hierarchy is hard-coded in `state_engine.py::FEATURE_MAP`. Live fetch requires JIRA credentials.
- Temporal polling uses HTTP API (not gRPC SDK). Requires Temporal server with HTTP gateway enabled.
- OSC 8 hyperlinks only render in terminals that support them (iTerm2, Kitty, WezTerm).
- No auth on FastAPI endpoints — run behind firewall or localhost only.

## Next Steps

- Wire Temporal signal handler to emit events automatically
- Add JIRA webhook receiver for real-time status sync
- Add Prometheus metrics endpoint
- Add WebSocket push to React Control Tower UI
