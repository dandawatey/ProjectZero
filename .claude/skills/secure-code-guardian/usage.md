# Usage: Secure Code Guardian

## How to Invoke
Activate when trigger conditions are met (see triggers.md).

## Process
1. OWASP scan: Check each Top 10 category. 2. Dependency audit: Check for known CVEs. 3. Secret scan: Search for hardcoded secrets, API keys, passwords. 4. Input validation: Verify all user inputs validated server-side. 5. Auth review: Verify authentication and authorization correct. 6. Report: Generate findings with severity and remediation.
