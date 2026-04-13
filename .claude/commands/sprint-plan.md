# /sprint-plan

Show the full 3-sprint delivery plan — all sprints, stories, estimates, agent assignments, status.

## Usage
```
/sprint-plan
```

## What to do

```bash
python3 << 'EOF'
import urllib.request, urllib.error, base64, json, os

BASE  = os.getenv("JIRA_BASE_URL", "https://isourceinnovation.atlassian.net")
EMAIL = os.getenv("JIRA_USER_EMAIL", "dandawate.y@isourceinfosystems.com")
TOKEN = os.getenv("JIRA_API_TOKEN", "")
BOARD = os.getenv("JIRA_BOARD_ID", "67")
creds = base64.b64encode(f"{EMAIL}:{TOKEN}".encode()).decode()
HDR   = {"Authorization": f"Basic {creds}", "Content-Type": "application/json"}

def jira_get(path):
    req = urllib.request.Request(f"{BASE}{path}", headers=HDR)
    with urllib.request.urlopen(req) as r: return json.loads(r.read())

def jira_post(path, data):
    req = urllib.request.Request(f"{BASE}{path}", headers=HDR,
          data=json.dumps(data).encode(), method="POST")
    with urllib.request.urlopen(req) as r: return json.loads(r.read())

sprints = jira_get(f"/rest/agile/1.0/board/{BOARD}/sprint?state=active,future,closed")["values"][-6:]

for sprint in sprints:
    sid  = sprint["id"]
    name = sprint.get("name","?")
    goal = sprint.get("goal","(no goal)")
    state = sprint.get("state","?").upper()
    icon = "✅" if state=="CLOSED" else ("🔵" if state=="ACTIVE" else "📋")

    issues = jira_post("/rest/api/3/search/jql", {
        "jql": f"sprint={sid}",
        "maxResults": 50,
        "fields": ["summary","status","customfield_10016","labels"]
    })["issues"]

    total_sp = sum((i["fields"].get("customfield_10016") or 0) for i in issues)
    done_sp  = sum((i["fields"].get("customfield_10016") or 0) for i in issues if i["fields"]["status"]["name"]=="Done")

    print(f"\n{icon} [{state}] {name}  |  {done_sp}/{total_sp} SP")
    print(f"   Goal: {goal}")
    print(f"   {'Ticket':<12} {'SP':<4} {'Agent':<14} {'Status':<14} Summary")
    print(f"   {'─'*12} {'─'*4} {'─'*14} {'─'*14} {'─'*30}")
    for i in issues:
        f = i["fields"]
        sp = int(f.get("customfield_10016") or 0)
        agent = next((l.replace("agent:","") for l in (f.get("labels") or []) if l.startswith("agent:")), "-")
        st = f["status"]["name"]
        tick = "✅" if st=="Done" else ("🔵" if st=="In Progress" else "⬜")
        print(f"   {i['key']:<12} {sp:<4} {agent:<14} {tick} {st:<12} {f['summary'][:45]}")

print(f"\nConfluence: https://isourceinnovation.atlassian.net/wiki/spaces/PR/pages/4521985")
print(f"Board: {BASE}/jira/software/projects/PRJ0/boards/{BOARD}")
EOF
```

After showing the plan, offer to start Sprint 2 (`/sprint-goal`) or drill into any story (`/ticket KEY`).
