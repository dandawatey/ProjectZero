# /agent-map

Show which agent handles each workflow stage (STAGE_AGENT_MAP).

## Usage
```
/agent-map
```

## What to do

```bash
python3 << 'EOF'
import urllib.request, urllib.error, json, os

API = os.getenv("API_BASE_URL", "http://localhost:8000")

try:
    req = urllib.request.Request(f"{API}/api/v1/commands/agent-map")
    with urllib.request.urlopen(req, timeout=5) as r:
        d = json.loads(r.read())

    print("ProjectZero — Stage → Agent Map\n")
    for stage, entries in d.get("stages",{}).items():
        print(f"  📋 {stage.upper()}")
        for e in entries:
            print(f"     Agent:    {e.get('agent_type','?')}")
            print(f"     Activity: {e.get('activity','?')}()")
            print(f"     Queue:    {e.get('task_queue','?')}")
            if e.get('description'): print(f"     Desc:     {e['description']}")
        print()
    
    print(f"Stage order: {' → '.join(d.get('stage_order',[]))}")
    print(f"\nAPI: {API}/api/v1/commands/agent-map")
except Exception as e:
    print(f"❌ Cannot reach backend: {e}")
    print("   Start backend: cd platform/backend && uvicorn app.main:app --reload")
    print("\nFallback (static):")
    print("  specification → spec-agent (spec_activity)")
    print("  architecture  → arch-agent (arch_activity)")
    print("  realization   → impl-agent (impl_activity) → review-agent (review_activity)")
    print("  completion    → deploy-agent (deploy_activity)")
EOF
```
