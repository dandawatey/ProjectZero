# Usage: Code Reviewer

## How to Invoke
Activate this skill when its trigger conditions are met (see triggers.md).

## Process
1. Readability: Is the code clear? Good names? Reasonable length? 2. Correctness: Does it do what the ticket says? Edge cases handled? 3. Performance: Any N+1 queries? Unnecessary re-renders? Expensive operations in loops? 4. Security: Input validation? SQL injection? XSS? Auth checks? 5. Tests: Meaningful tests? Good coverage? Testing behavior not implementation? 6. Architecture: Follows module boundaries? Correct patterns? No circular deps?

## Expected Output
Completed work following the methodology above, with quality validated against checklist.md.
