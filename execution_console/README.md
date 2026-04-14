# Claude Execution Console — PRJ0-56

Rich terminal sidecar for ProjectZero. Real-time Feature → Epic → Ticket → Workflow → Agent execution dashboard.

---

## Architecture

### NORMAL MODE

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       CLAUDE EXECUTION CONSOLE                              │
│                                                                             │
│  EVENT SOURCES              AGGREGATION LAYER          OUTPUT LAYER         │
│  ─────────────              ──────────────────         ────────────         │
│                             ┌──────────────────┐                           │
│  Claude Code ──────────────►│                  │      ┌──────────────────┐ │
│  Hooks (bash)               │  FastAPI Backend │─────►│ Rich Terminal    │ │
│  post_tool_use.sh           │  :8001           │  GET │ Live Dashboard   │ │
│                             │                  │ /snap│ (VS Code term.)  │ │
│  Temporal ─────────────────►│  /api/v1/events  │      └──────────────────┘ │
│  Workflow activities        │  /api/v1/snapshot│                           │
│                             │                  │      ┌──────────────────┐ │
│  JIRA REST ────────────────►│  SQLite store    │─────►│ JSONL event log  │ │
│  On-demand sync             │  ~/.projectzero/ │      │ ~/.projectzero/  │ │
│                             │  console.db      │      └──────────────────┘ │
│  curl / SDK ───────────────►│                  │                           │
│  (manual emit)              │  State Engine    │      ┌──────────────────┐ │
│                             │  (rollup logic)  │─────►│ HTML report      │ │
│                             └──────────────────┘      │ (on demand)      │ │
│                                                        └──────────────────┘ │
│  HIERARCHY                                                                  │
│  ─────────                                                                  │
│  Feature → Epic → Ticket → Workflow → Step/Activity → Agent                 │
└─────────────────────────────────────────────────────────────────────────────┘
```

### CAVEMAN MODE

We have work. Work split into parts.
- Feature = big goal (e.g. "Build Agent System")
- Epic = medium chunk (e.g. "EPIC-AGENT")
- Ticket = one task (e.g. "PRJ0-49: impl-agent worker")
- Workflow = machine doing the task (Temporal runs it)
- Step/Activity = one action inside workflow
- Agent = which Claude worker runs the step

Console sits on side. Watches everything. Shows you what runs.
You open terminal. Console shows all work. Progress moves.
Nothing talks to internals of Claude Code. All sidecar.

---

## Event Flow

### NORMAL MODE

```
Developer shell                  Claude Code               Console Backend
     │                               │                           │
     │ export CLAUDE_CURRENT_TICKET  │                           │
     │ =PRJ0-49                      │                           │
     │                               │                           │
     │──── claude-code ─────────────►│                           │
     │                               │                           │
     │                     [tool: Write file.py]                 │
     │                               │                           │
     │                   PostToolUse hook fires                  │
     │                               │                           │
     │                               │── POST /api/v1/events ───►│
     │                               │   {ticket:"PRJ0-49",      │
     │                               │    step:"Write",          │
     │                               │    status:"RUNNING"}      │
     │                               │                           │── store event
     │                               │◄── 201 OK ────────────────│── rollup pct
     │                               │                           │
     │                               │          Console terminal │
     │                               │◄── GET /snapshot ─────────│
     │                               │─── StatusSnapshot ───────►│── render
     │                               │                           │
```

### CAVEMAN MODE

You work. Claude Code uses tool (edit file, run bash).
Hook script fires. Hook sends message to console.
Console stores message. Console adds to progress.
Terminal shows update. All automatic. No effort.

---

## Progress Roll-up Logic

### NORMAL MODE

```
Step pct (0-100)
    │
    ▼
WorkflowStatus.pct = avg(step pcts)
    │
    ▼
TicketStatus.pct = workflow.pct
    │
    ▼
EpicStatus.pct = avg(ticket pcts in epic)
    │
    ▼
FeatureStatus.pct = avg(epic pcts in feature)
    │
    ▼
StatusSnapshot.overall_pct = avg(all ticket pcts)
```

Status priority (higher = wins):
```
FAILED > BLOCKED > RUNNING > RETRYING > SUCCESS > QUEUED
```
(One failing ticket makes the whole epic/feature FAILED)

### CAVEMAN MODE

Small task finish. Workflow bar moves.
Workflow done. Ticket bar moves.
Ticket done. Epic bar moves.
Epic done. Feature bar moves.
All features average. Overall bar moves.

If one thing fail, all parents show fail. Easy to see problem.

---

## Jira Mapping

### NORMAL MODE

```
JIRA Project (PRJ0)
    │
    ├── Feature (label / custom field)
    │     └── "feature:agents"
    │
    ├── Epic  (issuetype=Epic)
    │     └── EPIC-AGENT: "Agent System (34 agents, 7 teams)"
    │
    └── Ticket (issuetype=Story or Task)
          └── PRJ0-49: "Implement impl-agent worker"
                └── parent = EPIC-AGENT

Mapping is configurable in state_engine.py::FEATURE_MAP.
When JIRA credentials are set, jira_service.fetch_project_issues()
syncs live hierarchy. Without credentials, FEATURE_MAP is used.
```

### CAVEMAN MODE

JIRA has tickets. Tickets grouped into epics. Epics grouped into features.
Console reads JIRA. Builds tree. Shows tree in terminal.
No JIRA? Use hard-coded map in state_engine.py. Works offline.

---

## Temporal Mapping

### NORMAL MODE

```
Temporal workflow started for PRJ0-49
    │
    ├── workflow_id = "wf-prj0-49-001"
    ├── run_id      = "abc123xyz"
    ├── workflow_type = "FeatureDevelopmentWorkflow"
    │
    └── Event emitted:
        {event_type: "workflow_start",
         ticket_id: "PRJ0-49",
         workflow_run_id: "wf-prj0-49-001",
         temporal_url: "http://localhost:8233/..."}

Console builds deep-link to Temporal UI.
Terminal renders OSC-8 hyperlink (clickable in iTerm2/Kitty/WezTerm).
```

### CAVEMAN MODE

Temporal starts job. Job has ID.
We store: "this ticket" → "this job ID".
Console show link to job. Click link → Temporal UI opens.
See full logs there. Console shows summary here.

---

## Claude Code Hook Integration

### NORMAL MODE

Hook is wired in `.claude/settings.json`:
```json
"PostToolUse": [{
    "matcher": "Write|Edit|NotebookEdit|Bash",
    "hooks": [{
        "type": "command",
        "command": "bash .claude/hooks/post_tool_use.sh"
    }]
}]
```

Hook reads env vars, POSTs event, exits 0.
Runs async (background `&`) — does NOT block Claude Code.

### CAVEMAN MODE

Claude Code finishes tool. Hook script wakes up.
Hook reads: "which ticket?", "which agent?".
Hook sends event to console. Exits fast.
Claude Code not slowed down. Console gets update.

---

## Graphify Auto-Refresh (Knowledge Graph)

### NORMAL MODE

Second PostToolUse hook (also wired in settings.json):
```bash
(graphify-ts generate . --wiki --svg 2>/dev/null
 && rsync -a --delete graphify-out/ .claude/graphify-out/ && rm -rf graphify-out/) &
```

Runs in background after every file edit.
Keeps `.claude/graphify-out/` fresh.
Claude reads graph before searching files → fewer tokens wasted on broad searches.

### CAVEMAN MODE

You edit file. Graph rebuild starts in background.
Background job finishes. Graph file updated.
Next time Claude search codebase, Claude read graph first.
Graph show structure. Claude skip bad searches. Fewer tokens used.

---

## Logging and Traceability

### NORMAL MODE

Three layers:
1. **SQLite** (`~/.projectzero/console.db`) — structured event store, queryable
2. **JSONL** (`~/.projectzero/events.jsonl`) — append-only audit trail, portable
3. **OTel** (optional, disabled by default) — span export to Jaeger/Tempo/Honeycomb

Every event stored in all enabled layers simultaneously.
Log/trace URLs surfaced in terminal as OSC-8 hyperlinks.

### CAVEMAN MODE

Every event saved in three places.
1. Database — fast query
2. Text file — one event per line, easy to grep
3. Trace tool — optional, shows timeline (need to install extra package)

Click link in terminal. See logs for that ticket. No digging needed.

---

## Terminal Renderer Behavior

### NORMAL MODE

```
Render cycle (every ~2s):
  1. fetch_snapshot()  → StatusSnapshot
  2. build_header()    → overall progress bar + counts
  3. build_live_execution() → top panel, only RUNNING/RETRYING tickets
  4. build_feature_tree()   → full hierarchy tree
  5. build_failed_panel()   → only if failures exist
  6. Rich Live.update() → diff-rendered, no full repaint
```

OSC 8 hyperlinks render in: iTerm2, Kitty, WezTerm, Hyper, tmux (with config).
VS Code terminal: hyperlinks render as plain text with URL (readable fallback).

### CAVEMAN MODE

Console wake up. Ask for latest status.
Build picture: header, running list, full tree, failed list.
Draw on terminal. Wait 2 seconds. Draw again.
Only changes redrawn. Fast. Clean.
Click links if terminal support. See URL if not.

---

## Demo Mode Explanation

### NORMAL MODE

`demo.py` uses `DemoStateManager` — pure in-memory simulation, no backend required.
- 23 tickets defined with duration and failure probability
- Max 3 concurrent tickets running at once
- Every 1.5s tick: progress advances, completions attempted, retries scheduled
- Rich Live renderer polls state every 0.8s
- Simulation runs until all tickets reach terminal state (or Ctrl+C)

### CAVEMAN MODE

Demo script has fake tickets. No JIRA. No Temporal. No backend.
Script start. 3 tickets start running. Progress bars move.
Tickets finish or fail. New tickets start. Retries happen.
Watch full sprint simulate. Looks real. Is fake.
Good for: demos, screenshots, testing renderer without infra.

---

## Quick Start

### Demo Mode (no dependencies)

```bash
cd /path/to/ProjectZeroFactory
pip install rich fastapi uvicorn httpx pydantic python-dotenv
python execution_console/scripts/demo.py

# Faster simulation:
python execution_console/scripts/demo.py --speed 3.0

# More parallel tickets:
python execution_console/scripts/demo.py --max-concurrent 5
```

### Full Mode

```bash
# Terminal 1: start console backend
cd /path/to/ProjectZeroFactory
uvicorn execution_console.app.main:app --port 8001

# Terminal 2: start Rich renderer (polls backend)
python execution_console/scripts/start_console.py

# Emit events from another terminal or script:
curl -X POST http://localhost:8001/api/v1/events \
  -H "Content-Type: application/json" \
  -d '{"event_type":"ticket_status","ticket_id":"PRJ0-49",
       "status":"RUNNING","pct":67.0,"agent":"impl-agent"}'
```

### CAVEMAN Run Steps

```
1. Install: pip install rich fastapi uvicorn httpx pydantic
2. Run demo: python execution_console/scripts/demo.py
3. Watch bars move.

OR (full mode):
1. Start backend in terminal 1: uvicorn execution_console.app.main:app --port 8001
2. Start console in terminal 2: python execution_console/scripts/start_console.py
3. Send events: curl POST http://localhost:8001/api/v1/events
4. Watch console update.
```

---

## Connect JIRA

```bash
# In .env or shell:
JIRA_BASE_URL=https://your-org.atlassian.net
JIRA_USER_EMAIL=you@example.com
JIRA_API_TOKEN=your-api-token
JIRA_PROJECT_KEY=PRJ0
```

```python
# Fetch live hierarchy:
from execution_console.app.services.jira_service import fetch_project_issues
issues = fetch_project_issues("PRJ0")
```

Live JIRA sync updates `FEATURE_MAP` in state_engine for real ticket names/statuses.

---

## Connect Temporal

```bash
TEMPORAL_HOST=localhost:7233
TEMPORAL_NAMESPACE=default
TEMPORAL_UI_URL=http://localhost:8233
```

`temporal_service.fetch_running_workflows()` polls running executions every refresh.
Running workflows auto-linked to tickets by `workflow_run_id` correlation.

---

## Emit Claude Execution Events

### From shell (Claude Code hook):

```bash
export CLAUDE_CURRENT_TICKET=PRJ0-49
export CLAUDE_AGENT_NAME=impl-agent
# Hook fires automatically on every tool use when Claude Code is running
```

### From Python (Temporal activities or agent workers):

```python
from execution_console.app.integrations.claude.hook_events import HookEventEmitter

emitter = HookEventEmitter("http://localhost:8001")
emitter.emit(
    event_type="step_start",
    ticket_id="PRJ0-49",
    epic_key="EPIC-AGENT",
    workflow_run_id="wf-prj0-49-001",
    step="impl_activity",
    agent="impl-agent",
    status="RUNNING",
    pct=45.0,
)
```

### Via curl:

```bash
curl -X POST http://localhost:8001/api/v1/events \
  -H "Content-Type: application/json" \
  -d @execution_console/examples/sample_events.json
```

---

## API Reference

| Endpoint | Method | Description |
|---|---|---|
| `/api/v1/events` | POST | Ingest execution event |
| `/api/v1/snapshot` | GET | Current rollup snapshot |
| `/api/v1/events/failed` | GET | All failed events |
| `/api/v1/events` | DELETE | Clear all events |
| `/api/v1/health` | GET | Health check |

---

## Run Tests

```bash
cd /path/to/ProjectZeroFactory
pip install pytest
pytest execution_console/tests/ -v
```

---

## Generate HTML Report

```python
from execution_console.app.services.state_engine import build_snapshot
from execution_console.app.utils.html_report import generate

snapshot = build_snapshot()
generate(snapshot, output_path="/tmp/exec-report.html")
# open /tmp/exec-report.html
```

---

## Project Structure

```
execution_console/
├── app/
│   ├── api/
│   │   └── routes.py           ← FastAPI endpoints
│   ├── core/
│   │   └── config.py           ← Central config (all env vars)
│   ├── integrations/
│   │   ├── claude/
│   │   │   └── hook_events.py  ← Hook event contract + Python emitter
│   │   ├── jira/               ← (placeholder for jira_service move)
│   │   ├── otel/
│   │   │   └── exporter.py     ← OpenTelemetry span export (optional)
│   │   └── temporal/           ← (placeholder for temporal_service move)
│   ├── models/
│   │   └── events.py           ← Pydantic canonical models
│   ├── renderers/
│   │   └── rich_console.py     ← Rich terminal renderer
│   ├── services/
│   │   ├── event_store.py      ← SQLite store
│   │   ├── jira_service.py     ← JIRA REST client
│   │   ├── state_engine.py     ← Roll-up logic
│   │   └── temporal_service.py ← Temporal HTTP poller
│   ├── utils/
│   │   ├── html_report.py      ← HTML report generator
│   │   └── jsonl_log.py        ← JSONL event logger
│   └── main.py                 ← FastAPI app
├── examples/
│   └── sample_events.json      ← Example event payloads
├── scripts/
│   ├── demo.py                 ← Streaming demo (no infra needed)
│   └── start_console.py        ← Full mode launcher
├── tests/
│   ├── test_models.py          ← Model + rollup unit tests
│   └── test_state_engine.py    ← Snapshot build tests
├── .env.example                ← All config vars documented
└── requirements.txt
```

---

## Configuration Reference

| Variable | Default | Description |
|---|---|---|
| `EXECUTION_CONSOLE_URL` | `http://localhost:8001` | Backend URL for renderer to poll |
| `CONSOLE_DB_PATH` | `~/.projectzero/console.db` | SQLite database path |
| `CONSOLE_LOG_PATH` | `~/.projectzero/events.jsonl` | JSONL audit log path |
| `CONSOLE_REFRESH_SECONDS` | `2.0` | Renderer refresh interval |
| `JIRA_BASE_URL` | — | JIRA instance URL |
| `JIRA_USER_EMAIL` | — | JIRA auth email |
| `JIRA_API_TOKEN` | — | JIRA API token |
| `JIRA_PROJECT_KEY` | `PRJ0` | JIRA project key to sync |
| `TEMPORAL_HOST` | `localhost:7233` | Temporal gRPC/HTTP host |
| `TEMPORAL_NAMESPACE` | `default` | Temporal namespace |
| `TEMPORAL_UI_URL` | `http://localhost:8233` | Temporal Web UI for deep links |
| `CLAUDE_CURRENT_TICKET` | — | Active ticket (used by hooks) |
| `CLAUDE_AGENT_NAME` | `claude` | Agent role name (used by hooks) |
| `OTEL_ENABLED` | `false` | Enable OTel span export |
| `OTEL_ENDPOINT` | `http://localhost:4317` | OTel collector endpoint |

---

## Limitations

- JIRA hierarchy defaults to hard-coded `FEATURE_MAP` without credentials
- Temporal polling uses HTTP API — requires Temporal with HTTP gateway
- OSC 8 hyperlinks only in: iTerm2, Kitty, WezTerm, Hyper (VS Code shows plain URL)
- No auth on FastAPI endpoints — localhost/firewall only
- graphify-ts background refresh runs per file edit — may lag on slow machines

---

## Assumptions

1. One FastAPI instance per machine (port 8001). Multi-machine: deploy behind a shared URL.
2. SQLite for simplicity. Postgres upgrade: swap event_store.py only.
3. JIRA hierarchy uses `parent` field for epic→ticket. Custom hierarchies need `customfield_10014`.
4. Temporal correlation: `workflow_run_id` in events must match actual Temporal workflow ID.
5. OTel disabled by default — install `opentelemetry-sdk` + exporter packages to enable.

---

## Next Enhancements

| Priority | Enhancement |
|---|---|
| High | JIRA webhook receiver (`POST /api/v1/jira/webhook`) for real-time sync |
| High | WebSocket push to React Control Tower (replace polling with push) |
| High | Temporal signal handler that auto-emits events from workflow activities |
| Medium | Maker-Checker-Reviewer-Approver visualisation (4-eye flow as swimlanes) |
| Medium | Per-agent productivity metrics (tickets/hour, avg duration, failure rate) |
| Medium | Prometheus `/metrics` endpoint for Grafana integration |
| Low | Execution replay (scrub through JSONL log, re-render history) |
| Low | Slack/Teams notification on failure or completion |
| Low | Multi-product view (one console, multiple product repos) |
| Low | Keyboard shortcuts (r=refresh, f=filter, q=quit, s=status) |

---

## Slash Command

```
/console   ← launch from Claude Code (wired in .claude/skills/)
```
