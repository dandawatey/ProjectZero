# /console

Launch the Claude Execution Console — Rich terminal dashboard showing Feature/Epic/Ticket/Workflow execution status.

## Usage
/console [--demo]

## Steps
1. If --demo flag: run demo mode with mock data
   cd /path/to/repo && python execution_console/scripts/demo.py

2. Normal mode (requires running backend):
   # Terminal 1: start backend
   uvicorn execution_console.app.main:app --port 8001
   
   # Terminal 2: start Rich console
   python execution_console/scripts/start_console.py

3. To ingest a custom event:
   curl -X POST http://localhost:8001/api/v1/events \
     -H "Content-Type: application/json" \
     -d '{"event_type":"ticket_status","ticket_id":"PRJ0-49","status":"RUNNING","pct":67.0,"agent":"impl-agent"}'

## Environment Variables
- EXECUTION_CONSOLE_URL: backend URL (default: http://localhost:8001)
- CONSOLE_DB_PATH: SQLite path (default: ~/.projectzero/console.db)
- CLAUDE_CURRENT_TICKET: set this in your shell to auto-tag events
