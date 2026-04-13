# /publish-cxo

Publish CXO portfolio metrics from JIRA to Confluence. Optionally publish a single project.

## Usage
```
/publish-cxo
/publish-cxo PRJ0
/publish-cxo INETZERO
```

## What to do

```bash
python3 << 'EOF'
import urllib.request, urllib.error, json, os, sys

API = os.getenv("API_BASE_URL", "http://localhost:8000")

arg = "$ARGUMENTS".strip().upper()

def post(path):
    req = urllib.request.Request(f"{API}{path}", method="POST",
          data=b"{}", headers={"Content-Type":"application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read()), None
    except urllib.error.HTTPError as e:
        return None, f"HTTP {e.code}: {e.read().decode()[:200]}"
    except Exception as e:
        return None, str(e)

if arg:
    print(f"📊 Publishing CXO metrics for {arg} to Confluence...")
    d, err = post(f"/api/v1/cxo/publish/{arg}")
else:
    print(f"📊 Publishing full CXO Portfolio to Confluence...")
    d, err = post("/api/v1/cxo/publish")

if err:
    print(f"❌ Failed: {err}")
    print("   Is the backend running? (API_BASE_URL defaults to http://localhost:8000)")
    print("   Are CONFLUENCE_BASE_URL and JIRA_API_TOKEN set in .env?")
else:
    page_id = d.get("page_id","?")
    url = d.get("url", f"https://isourceinnovation.atlassian.net/wiki/pages/{page_id}")
    print(f"✅ Published to Confluence")
    print(f"   Page ID: {page_id}")
    print(f"   URL:     {url}")
EOF
```
