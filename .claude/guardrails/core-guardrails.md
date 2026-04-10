# Core Guardrails

These rules apply to ALL agents at ALL stages. No exceptions.

## Governance
1. All work flows through maker-checker-reviewer-approver chain
2. No artifact ships without passing all three gates
3. Every rejection includes specific, actionable feedback
4. No self-approval (maker ≠ checker ≠ reviewer ≠ approver)

## Quality
5. Write tests before code (TDD)
6. Minimum 80% test coverage, 100% on critical paths
7. Zero linting errors, zero warnings
8. No TODO/FIXME in shipped code
9. No console.log/debug in production code

## Governance
10. No Ticket, No Work — every change references a ticket
11. Every commit message includes ticket ID
12. Every PR links to ticket
13. No stage skipping in SPARC flow

## Truthfulness
14. Never mark done if tests don't pass
15. Never claim coverage without measuring it
16. Never skip security scan and claim clean
17. Never approve without actually reviewing
18. Never use placeholder implementations in "done" code

## Learning
19. Read relevant memory before starting work
20. Write structured learnings after completing work
21. Never self-mutate agent definitions without approval
22. Promote learnings only through memory-agent process

## Security
23. No secrets in code or config files
24. Parameterized queries only
25. Input validation on all user-facing endpoints
26. HTTPS everywhere
