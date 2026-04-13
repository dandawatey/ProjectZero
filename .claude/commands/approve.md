# /approve

Approve or reject a workflow stage gate. Sends signal to Temporal workflow.

## Usage
```
/approve
/approve <workflow_run_id> <stage> [comment]
/approve abc-123 specification "Looks good, proceed"
/approve abc-123 architecture reject "Need to revisit DB schema"
```

## What to do

Parse `$ARGUMENTS`. First token = workflow_run_id, second = stage, optional "reject" keyword flips to rejected, rest = comment.

```bash
python3 << 'EOF'
import urllib.request, urllib.error, json, os, sys

API = os.getenv("API_BASE_URL", "http://localhost:8000")

args = "$ARGUMENTS".strip().split(None, 3)

if len(args) < 2:
    print("Usage: /approve <workflow_run_id> <stage> [reject] [comment]")
    print("Stages: specification | architecture | realization | completion")
    print("")
    print("Examples:")
    print("  /approve abc-123 specification")
    print("  /approve abc-123 architecture reject 'Need ADR revisions'")
    sys.exit(0)

workflow_run_id = args[0]
stage = args[1].lower()

approved = True
comment = ""

if len(args) >= 3:
    if args[2].lower() == "reject":
        approved = False
        comment = args[3] if len(args) >= 4 else ""
    else:
        comment = " ".join(args[2:])

valid_stages = ["specification", "architecture", "realization", "completion"]
if stage not in valid_stages:
    print(f"❌ Invalid stage: '{stage}'")
    print(f"   Valid: {', '.join(valid_stages)}")
    sys.exit(1)

action = "APPROVE" if approved else "REJECT"
print(f"{'✅' if approved else '❌'} {action} — {stage} stage")
print(f"   Workflow: {workflow_run_id}")
if comment:
    print(f"   Comment: {comment}")
print(f"   Signaling Temporal workflow...")

payload = json.dumps({
    "workflow_run_id": workflow_run_id,
    "stage": stage,
    "approved": approved,
    "comment": comment
}).encode()

req = urllib.request.Request(
    f"{API}/api/v1/commands/approve",
    headers={"Content-Type": "application/json"},
    data=payload, method="POST"
)

try:
    with urllib.request.urlopen(req, timeout=15) as r:
        d = json.loads(r.read())
    status = d.get("status", "?")
    next_stage = d.get("next_stage")
    print(f"\n✅ Signal sent")
    print(f"   Status:     {status}")
    if next_stage:
        print(f"   Next stage: {next_stage}")
    else:
        print(f"   Workflow complete")
    if d.get("message"):
        print(f"   {d['message']}")
except urllib.error.HTTPError as e:
    err = json.loads(e.read().decode())
    print(f"❌ Failed: {err.get('detail', e.code)}")
    print("   Check workflow_run_id exists and stage matches current gate")
except Exception as e:
    print(f"❌ Error: {e}")
    print("   Is backend running? (API_BASE_URL defaults to http://localhost:8000)")
EOF
```
