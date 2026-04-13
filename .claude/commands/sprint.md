# /sprint

Show the active sprint status for ProjectZero board — goal, burn, story counts.

## Usage
```
/sprint
/sprint 100
```

## What to do

Run the script below. If an argument is provided use it as the sprint ID, otherwise find the active sprint.

```bash
python3 << 'EOF'
import urllib.request, urllib.error, base64, json, os, sys

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

SPRINT_ARG = "$ARGUMENTS".strip()

# Find sprint
sprints = jira_get(f"/rest/agile/1.0/board/{BOARD}/sprint?state=active,future")["values"]
if SPRINT_ARG and SPRINT_ARG.isdigit():
    sprint = next((s for s in sprints if str(s["id"]) == SPRINT_ARG), None)
else:
    sprint = next((s for s in sprints if s["state"]=="active"), sprints[0] if sprints else None)

if not sprint:
    print("No active sprint found.")
    sys.exit(0)

sid = sprint["id"]
sname = sprint.get("name","?")
sgoal = sprint.get("goal","(no goal set)")
sstart = sprint.get("startDate","?")[:10]
send = sprint.get("endDate","?")[:10]

# Get issues in sprint
issues = jira_post("/rest/api/3/search/jql", {
    "jql": f"sprint={sid} ORDER BY status",
    "maxResults": 100,
    "fields": ["summary","status","customfield_10016","assignee","labels","priority"]
})["issues"]

counts = {"To Do":0,"In Progress":0,"Done":0,"Blocked":0}
total_sp = done_sp = 0
rows = []
for i in issues:
    f = i["fields"]
    st = f["status"]["name"]
    sp = f.get("customfield_10016") or 0
    agent = next((l.replace("agent:","") for l in (f.get("labels") or []) if l.startswith("agent:")), "-")
    bucket = "Done" if st=="Done" else ("In Progress" if st=="In Progress" else ("Blocked" if st=="Blocked" else "To Do"))
    counts[bucket] = counts.get(bucket,0)+1
    total_sp += sp
    if st=="Done": done_sp += sp
    rows.append((i["key"], st[:12], str(int(sp)) if sp else "?", agent, f["summary"][:50]))

print(f"""
╔═ {sname} ══════════════════════════════════
║ Goal:     {sgoal}
║ Dates:    {sstart} → {send}
║ Burn:     {done_sp}/{total_sp} SP  ({round(done_sp/total_sp*100) if total_sp else 0}% done)
║ Stories:  ✅ Done={counts['Done']}  🔵 In Progress={counts['In Progress']}  ⬜ To Do={counts['To Do']}  🔴 Blocked={counts.get('Blocked',0)}
╠══════════════════════════════════════════════""")
for key,st,sp,agent,title in rows:
    icon = "✅" if st=="Done" else ("🔵" if "Progress" in st else ("🔴" if "Block" in st else "⬜"))
    print(f"║ {icon} {key:<10} sp={sp:<3} [{agent:<12}] {title}")
print(f"""╚══════════════════════════════════════════════
Board: {BASE}/jira/software/projects/PRJ0/boards/{BOARD}""")
EOF
```

Display the output as-is. Offer to show detail on any blocked story.
