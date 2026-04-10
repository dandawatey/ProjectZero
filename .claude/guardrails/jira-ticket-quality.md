# JIRA Ticket Quality Rules

## Story Format
```
As a [specific user persona],
I want to [perform an action],
So that [I achieve a benefit].
```

## Required Fields
| Field | Required | Rule |
|-------|----------|------|
| Summary | Yes | Clear, under 80 characters |
| Description | Yes | Enough context to implement without asking |
| Acceptance Criteria | Yes | Testable, specific, measurable |
| Story Points | Yes (stories) | Fibonacci: 1, 2, 3, 5, 8, 13 |
| Priority | Yes | P1 (Critical) to P4 (Low) |
| Labels | Yes | Module name, tech area |
| Epic Link | Yes | Parent epic/module |

## Quality Checks
- No vague descriptions ("improve performance" → specify metric and target)
- No acceptance criteria without measurable outcome
- Stories > 8 points should be split
- Bug tickets require: steps to reproduce, expected vs actual, environment

## Anti-Patterns (Rejected)
- "As a developer, I want to refactor..." (developer is not a user persona)
- Acceptance criteria: "works correctly" (not testable)
- Description: "see Slack thread" (context must be in ticket)
- Empty acceptance criteria
