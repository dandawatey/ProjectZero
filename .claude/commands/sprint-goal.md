# /sprint-goal

Update the goal of the active (or specified) sprint in JIRA.

## Usage
```
/sprint-goal Implement MCRA 4-eye workflow and TDD enforcement
/sprint-goal 100 "Governance and quality gates"
```

## What to do

Parse `$ARGUMENTS`. If first token is a number, treat it as sprint ID and rest as goal text. Otherwise find active sprint and use full text as goal.

```bash
python3 << 'EOF'
import urllib.request, urllib.error, base64, json, os, sys

BASE  = os.getenv("JIRA_BASE_URL", "https://isourceinnovation.atlassian.net")
EMAIL = os.getenv("JIRA_USER_EMAIL", "dandawate.y@isourceinfosystems.com")
TOKEN = os.getenv("JIRA_API_TOKEN", "")
BOARD = os.getenv("JIRA_BOARD_ID", "67")
creds = base64.b64encode(f"{EMAIL}:{TOKEN}".encode()).decode()
HDR   = {"Authorization": f"Basic {creds}", "Content-Type": "application/json"}

args = "$ARGUMENTS".strip().split(None, 1)
if not args:
    print("Usage: /sprint-goal [sprint-id] <goal text>")
    sys.exit(0)

sprint_id = None
goal_text = "$ARGUMENTS".strip()
if args[0].isdigit():
    sprint_id = int(args[0])
    goal_text = args[1] if len(args) > 1 else ""

if not goal_text:
    print("Error: goal text is required")
    sys.exit(1)

def jira_get(path):
    req = urllib.request.Request(f"{BASE}{path}", headers=HDR)
    with urllib.request.urlopen(req) as r: return json.loads(r.read())

# Find sprint if not specified
if not sprint_id:
    sprints = jira_get(f"/rest/agile/1.0/board/{BOARD}/sprint?state=active")["values"]
    if not sprints:
        print("No active sprint found. Specify sprint ID: /sprint-goal 100 <goal>")
        sys.exit(1)
    sprint_id = sprints[0]["id"]
    sprint_name = sprints[0].get("name","?")
else:
    sprint_name = f"Sprint {sprint_id}"

# Update goal via POST (JIRA agile uses POST for sprint updates)
req = urllib.request.Request(
    f"{BASE}/rest/agile/1.0/sprint/{sprint_id}",
    headers=HDR, method="POST",
    data=json.dumps({"goal": goal_text}).encode()
)
try:
    with urllib.request.urlopen(req) as r:
        print(f"✅ Updated sprint goal")
        print(f"   Sprint: {sprint_name} (id={sprint_id})")
        print(f"   Goal:   {goal_text}")
except urllib.error.HTTPError as e:
    print(f"❌ Failed to update goal: {e.code} {e.read().decode()[:200]}")
EOF
```
