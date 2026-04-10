# Workflow: Maker-Checker-Reviewer-Approver

## Purpose
Governance chain ensuring every artifact is validated through multiple independent gates before acceptance.

## Chain
```
Maker (produces) → Checker (validates basics) → Reviewer (deep review) → Approver (authorizes)
```

## Maker
- Any agent that produces an artifact (code, spec, architecture, etc.)
- Must complete work according to their agent contract
- Must include tests/validation for their work
- Submits to Checker when done

## Checker (Gate 1)
- Automated/semi-automated validation
- Checks: tests pass, lint clean, security scan clean, builds successfully
- Binary pass/fail — no subjective judgment
- **PASS** → forwards to Reviewer
- **FAIL** → returns to Maker with specific findings (file, line, issue)

## Reviewer (Gate 2)
- Deep quality assessment
- Checks: code quality, architecture alignment, test adequacy, documentation
- Can provide improvement suggestions (non-blocking) and blocking findings
- **APPROVE** → forwards to Approver
- **REJECT** → returns to Maker with actionable feedback

## Approver (Gate 3)
- Business and governance validation
- Checks: business requirements met, governance compliant, ready for merge
- **APPROVE** → work is authorized (merge/deploy)
- **REJECT** → returns to Maker with business-level feedback

## Rules
1. Each gate is independent — Reviewer does not re-check what Checker checked
2. Rejection always includes specific, actionable feedback
3. Maker cannot be their own Checker, Reviewer, or Approver
4. All gate decisions logged in audit-log.md
5. No bypassing gates — even for "small" changes
