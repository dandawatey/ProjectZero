# Skill: Code Reviewer

## Purpose
Structured code review covering all quality dimensions.

## Methodology
1. Readability: Is the code clear? Good names? Reasonable length? 2. Correctness: Does it do what the ticket says? Edge cases handled? 3. Performance: Any N+1 queries? Unnecessary re-renders? Expensive operations in loops? 4. Security: Input validation? SQL injection? XSS? Auth checks? 5. Tests: Meaningful tests? Good coverage? Testing behavior not implementation? 6. Architecture: Follows module boundaries? Correct patterns? No circular deps?

## Stage Mapping
Used during: Realization, Completion (unless otherwise noted)

## Integration
Available to all agents. Invoke when trigger conditions are met.
