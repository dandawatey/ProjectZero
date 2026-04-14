Run quality gates (coverage ≥80%, lint, types) against a product repo.

## Usage
/check [repo_path]

## What it does
Calls POST /api/v1/commands/check with the repo_path argument (defaults to current directory).
Returns a table showing each gate result.

## Steps
1. Set REPO="${1:-.}"
2. Call: curl -s -X POST http://localhost:8000/api/v1/commands/check \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer $PROJECTZERO_TOKEN" \
     -d "{\"repo_path\": \"$REPO\"}"
3. Parse and display as table:
   | Gate     | Status | Score      |
   |----------|--------|------------|
   | coverage | ✓ PASS | 87.3%      |
   | lint     | ✗ FAIL | 12 errors  |
   | types    | SKIP   | not found  |
4. Show overall: PASS or FAIL with remediation hints for failed gates.
