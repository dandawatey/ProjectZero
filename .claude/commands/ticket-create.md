# /ticket-create

Create a new JIRA story from a feature description using the Spec Agent (Claude API).
Parses the description into user stories with acceptance criteria, then creates JIRA tickets.

## Usage
```
/ticket-create
/ticket-create Add OAuth2 SSO login for enterprise customers
/ticket-create PRJ0 "Real-time dashboard with WebSocket updates"
```

## What to do

1. If no description in `$ARGUMENTS`, ask the user: "What feature do you want to specify? Describe it in 1-2 sentences."
2. Determine project key: first word of args if it matches `[A-Z]+-?` pattern, else use `PRJ0` or ask.
3. Call `/api/v1/commands/spec/parse` with the description text.
4. Display the generated stories and ask for confirmation before creating JIRA tickets.

```bash
python3 << 'EOF'
import urllib.request, urllib.error, json, os, sys

API = os.getenv("API_BASE_URL", "http://localhost:8000")

args = "$ARGUMENTS".strip().split(None, 1)
project_key = "PRJ0"
desc = "$ARGUMENTS".strip()

# Check if first arg looks like a project key
if args and args[0].isupper() and len(args[0]) <= 8:
    project_key = args[0]
    desc = args[1] if len(args) > 1 else ""

if not desc:
    print("Usage: /ticket-create [PROJECT-KEY] <feature description>")
    print("Example: /ticket-create PRJ0 Add OAuth SSO login for enterprise customers")
    sys.exit(0)

print(f"🤖 Spec Agent parsing: '{desc[:80]}'")
print(f"   Project: {project_key}")
print(f"   Calling Claude (claude-sonnet-4-6)...")

# Use a placeholder product_id — spec/parse works without a real product
payload = json.dumps({
    "product_id": "00000000-0000-0000-0000-000000000000",
    "prd_text": desc,
    "jira_project_key": project_key,
    "create_jira_tickets": False,  # preview first
}).encode()

req = urllib.request.Request(
    f"{API}/api/v1/commands/spec/parse",
    headers={"Content-Type": "application/json"},
    data=payload, method="POST"
)
try:
    with urllib.request.urlopen(req, timeout=60) as r:
        d = json.loads(r.read())
    
    print(f"\n✅ Spec generated: {d.get('feature_title','?')}")
    print(f"   {d.get('feature_summary','')[:100]}")
    
    stories = d.get("stories", [])
    print(f"\n{len(stories)} user stories:\n")
    for i, s in enumerate(stories, 1):
        print(f"  {i}. [{s.get('estimate_sp','?')}sp] {s.get('title','?')}")
        print(f"     As a {s.get('role','?')}, I want to {s.get('action','?')}")
        ac = s.get("acceptance_criteria", [])[:2]
        for c in ac:
            print(f"     ✓ Given {c.get('given','?')} → Then {c.get('then','?')}")
        print()
    
    if d.get("risks"):
        print(f"Risks: {', '.join(d['risks'][:3])}")
    
    print("\nTo create these as JIRA tickets, confirm with: yes")
    print("(Or re-run with create_jira_tickets=True in the API directly)")

except urllib.error.HTTPError as e:
    err = json.loads(e.read().decode())
    print(f"❌ Failed: {err.get('detail', e.code)}")
    print("   Is ANTHROPIC_API_KEY set in .env?")
except Exception as e:
    print(f"❌ Error: {e}")
EOF
```

After showing the preview, ask "Create these tickets in JIRA? (yes/no)". If yes, call the same endpoint with `create_jira_tickets: true` and display the created ticket keys.
