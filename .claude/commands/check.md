# /check

Run quality gates on a product repo: lint (ruff), type check (mypy), tests (pytest --cov). Reports pass/fail per gate with coverage %.

## Usage
```
/check
/check /path/to/product-repo
/check PRJ0
```

## What to do

If arg looks like a path, use it. If arg looks like a project key, resolve from backend. Else use current directory. Run ruff → mypy → pytest in sequence. Gate: coverage ≥ 80%.

```bash
python3 << 'EOF'
import subprocess, os, sys, re, urllib.request, json

API = os.getenv("API_BASE_URL", "http://localhost:8000")
arg = "$ARGUMENTS".strip()

# Resolve repo path
repo_path = None
if arg.startswith("/") or arg.startswith("~") or arg.startswith("."):
    repo_path = os.path.expanduser(arg)
elif arg and arg.isupper():
    # Looks like project key — ask backend
    try:
        req = urllib.request.Request(f"{API}/api/v1/products/")
        with urllib.request.urlopen(req, timeout=5) as r:
            products = json.loads(r.read())
        for p in products:
            if p.get("jira_project_key","").upper() == arg.upper():
                repo_path = p.get("repo_path")
                break
        if not repo_path:
            print(f"❌ No product found for project key: {arg}")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Cannot resolve product repo: {e}")
        sys.exit(1)
else:
    repo_path = os.getcwd()

print(f"🔍 Quality gates: {repo_path}\n")

def run(cmd, cwd):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr

gates = []

# --- Ruff lint ---
code, out = run(["ruff", "check", "."], repo_path)
status = "✅ PASS" if code == 0 else "❌ FAIL"
gates.append(("Lint (ruff)", code == 0, out[:300] if code != 0 else ""))
print(f"{status}  Lint (ruff)")
if code != 0:
    print(f"         {out.strip()[:200]}")

# --- Mypy type check ---
code, out = run(["mypy", ".", "--ignore-missing-imports", "--no-error-summary"], repo_path)
errors = [l for l in out.splitlines() if ": error:" in l]
ok = len(errors) == 0
status = "✅ PASS" if ok else "❌ FAIL"
gates.append(("Types (mypy)", ok, f"{len(errors)} errors" if not ok else ""))
print(f"{status}  Types (mypy)" + (f" — {len(errors)} errors" if not ok else ""))
if not ok:
    for e in errors[:3]:
        print(f"         {e}")

# --- Pytest + coverage ---
code, out = run([
    "pytest", "--tb=short", "-q",
    "--cov=.", "--cov-report=term-missing", "--cov-fail-under=80"
], repo_path)

# Extract coverage %
cov_pct = None
for line in out.splitlines():
    m = re.search(r"TOTAL\s+\d+\s+\d+\s+(\d+)%", line)
    if m:
        cov_pct = int(m.group(1))
        break

# Extract pass/fail counts
passed = failed = 0
for line in out.splitlines():
    m = re.search(r"(\d+) passed", line)
    if m: passed = int(m.group(1))
    m = re.search(r"(\d+) failed", line)
    if m: failed = int(m.group(1))

test_ok = code == 0
cov_ok = (cov_pct or 0) >= 80
status = "✅ PASS" if test_ok else "❌ FAIL"
cov_str = f"{cov_pct}%" if cov_pct is not None else "?"
cov_icon = "✅" if cov_ok else "❌"
gates.append(("Tests (pytest)", test_ok, f"{passed} passed, {failed} failed"))
gates.append(("Coverage ≥80%", cov_ok, f"{cov_str}"))
print(f"{status}  Tests (pytest) — {passed} passed, {failed} failed")
print(f"{cov_icon}     Coverage — {cov_str}")
if not test_ok:
    for line in out.splitlines():
        if "FAILED" in line or "ERROR" in line:
            print(f"         {line}")

# --- Summary ---
all_pass = all(g[1] for g in gates)
print(f"\n{'═'*46}")
print(f"  {'✅ ALL GATES PASS' if all_pass else '❌ GATES FAILED'}")
print(f"{'═'*46}")
for name, ok, detail in gates:
    icon = "✅" if ok else "❌"
    print(f"  {icon}  {name}" + (f"  ({detail})" if detail else ""))
print(f"{'═'*46}")

if all_pass:
    print("\nReady for /review")
else:
    print("\nFix failures before /review")
    sys.exit(1)
EOF
```
