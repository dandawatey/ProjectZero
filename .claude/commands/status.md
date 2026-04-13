# /status

Show ProjectZero system status — workflows, agents, integration health, active sprint burn.

## Usage
```
/status
```

## What to do

Call backend API and JIRA in parallel, then display a combined dashboard:

```bash
python3 << 'EOF'
import urllib.request, urllib.error, base64, json, os, sys
from datetime import datetime, timezone

API   = os.getenv("API_BASE_URL", "http://localhost:8000")
BASE  = os.getenv("JIRA_BASE_URL", "https://isourceinnovation.atlassian.net")
EMAIL = os.getenv("JIRA_USER_EMAIL", "dandawate.y@isourceinfosystems.com")
TOKEN = os.getenv("JIRA_API_TOKEN", "")
BOARD = os.getenv("JIRA_BOARD_ID", "67")
creds = base64.b64encode(f"{EMAIL}:{TOKEN}".encode()).decode()
JIRA_HDR = {"Authorization": f"Basic {creds}", "Content-Type": "application/json"}

def get(url, headers=None):
    try:
        req = urllib.request.Request(url, headers=headers or {})
        with urllib.request.urlopen(req, timeout=5) as r: return json.loads(r.read()), True
    except Exception as e: return {"error": str(e)}, False

now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

# Backend health
health, ok = get(f"{API}/health")
backend_status = "🟢 Online" if ok and health.get("status")=="ok" else "🔴 Offline"

# Dashboard summary
dash, ok2 = get(f"{API}/api/v1/dashboard/summary")
if ok2:
    wf = dash
    active   = wf.get("active_workflows", "?")
    done     = wf.get("completed_workflows", "?")
    failed   = wf.get("failed_workflows", "?")
    blocked  = wf.get("blocked_workflows", "?")
    pending  = wf.get("pending_approvals", "?")
else:
    active=done=failed=blocked=pending="?"

# Integration health
int_health, ok3 = get(f"{API}/api/v1/integrations/status")
jira_h = "?" ; conf_h = "?"
if ok3:
    for svc in int_health.get("services",[]):
        n = svc.get("name","").lower()
        s = "🟢" if svc.get("healthy") else "🔴"
        if "jira" in n: jira_h = s
        if "confluence" in n: conf_h = s

# Active sprint
try:
    req = urllib.request.Request(f"{BASE}/rest/agile/1.0/board/{BOARD}/sprint?state=active", headers=JIRA_HDR)
    with urllib.request.urlopen(req, timeout=5) as r:
        sprints = json.loads(r.read()).get("values",[])
    sprint = sprints[0] if sprints else None
    if sprint:
        sprint_name = sprint.get("name","?")
        sprint_goal = sprint.get("goal","(no goal)")[:60]
        req2 = urllib.request.Request(
            f"{BASE}/rest/api/3/search/jql",
            headers=JIRA_HDR, method="POST",
            data=json.dumps({"jql":f"sprint={sprint['id']}","fields":["status","customfield_10016"],"maxResults":50}).encode()
        )
        with urllib.request.urlopen(req2, timeout=5) as r2:
            issues = json.loads(r2.read()).get("issues",[])
        tsp = sum((i["fields"].get("customfield_10016") or 0) for i in issues)
        dsp = sum((i["fields"].get("customfield_10016") or 0) for i in issues if i["fields"]["status"]["name"]=="Done")
        pct = round(dsp/tsp*100) if tsp else 0
        sprint_line = f"{sprint_name} | {dsp}/{tsp} SP ({pct}%)"
    else:
        sprint_line = "No active sprint"
except Exception as e:
    sprint_line = f"JIRA unreachable ({e})"

print(f"""
╔══════════════════════════════════════════════
║  ProjectZero Status — {now}
╠══════════════════════════════════════════════
║  Backend:      {backend_status}
║  JIRA:         {jira_h}  Confluence: {conf_h}
╠══════════════════════════════════════════════
║  Workflows:    🔵 Active={active}  ✅ Done={done}  ❌ Failed={failed}  🔴 Blocked={blocked}
║  Approvals:    ⏳ Pending={pending}
╠══════════════════════════════════════════════
║  Sprint:       {sprint_line}
╚══════════════════════════════════════════════""")
EOF
```

After displaying, offer next actions: `/sprint` for full sprint detail, `/ticket KEY` for a specific story, `/approve` for pending approvals.
