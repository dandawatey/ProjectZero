# /ticket

Fetch and display a JIRA ticket from ProjectZero (PRJ0) with full detail.

## Usage
```
/ticket PRJ0-37
/ticket INETZERO-12
```

## What to do

The argument is a JIRA ticket key. Run:

```bash
python3 << 'EOF'
import urllib.request, urllib.error, base64, json, os, sys

KEY = "$ARGUMENTS"
if not KEY:
    print("Usage: /ticket <KEY>  e.g. /ticket PRJ0-37")
    sys.exit(0)

BASE  = os.getenv("JIRA_BASE_URL", "https://isourceinnovation.atlassian.net")
EMAIL = os.getenv("JIRA_USER_EMAIL", "dandawate.y@isourceinfosystems.com")
TOKEN = os.getenv("JIRA_API_TOKEN", "")
creds = base64.b64encode(f"{EMAIL}:{TOKEN}".encode()).decode()
HDR   = {"Authorization": f"Basic {creds}"}

def jira(path):
    req = urllib.request.Request(f"{BASE}{path}", headers=HDR)
    with urllib.request.urlopen(req) as r: return json.loads(r.read())

try:
    d = jira(f"/rest/api/3/issue/{KEY}?fields=summary,status,issuetype,priority,assignee,customfield_10016,customfield_10020,labels,description,parent")
    f = d["fields"]
    sprint = ""
    for s in (f.get("customfield_10020") or []):
        if isinstance(s, dict) and s.get("state") in ("active","future"):
            sprint = s.get("name","")
            break
    sp = f.get("customfield_10016") or "?"
    agent = next((l.replace("agent:","") for l in (f.get("labels") or []) if l.startswith("agent:")), "unassigned")
    print(f"""
┌─ {KEY} ─────────────────────────────────────
│ {f['summary']}
├─────────────────────────────────────────────
│ Type:     {f['issuetype']['name']}
│ Status:   {f['status']['name']}
│ Priority: {(f.get('priority') or {}).get('name','?')}
│ SP:       {sp}
│ Agent:    {agent}
│ Sprint:   {sprint or 'Backlog'}
│ Labels:   {', '.join(f.get('labels') or []) or 'none'}
│ URL:      {BASE}/browse/{KEY}
└─────────────────────────────────────────────""")
except Exception as e:
    print(f"Error fetching {KEY}: {e}")
EOF
```

Display the output clearly. If the ticket has acceptance criteria or description content, summarise it in 2-3 bullet points after the table.
