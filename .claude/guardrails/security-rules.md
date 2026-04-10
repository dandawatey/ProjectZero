# Security Rules

## Input Validation
- Validate all user input on the server (never trust client-side only)
- Use schema validation (Zod, Joi, or equivalent)
- Reject unexpected fields (strict schemas)
- Sanitize output to prevent XSS

## Database
- Parameterized queries ONLY (never string concatenation)
- Use ORM where possible (Prisma, Drizzle, SQLAlchemy)
- Least privilege database users
- No raw SQL without security review

## Authentication & Authorization
- Secure password hashing (bcrypt, argon2)
- JWT with short expiry (15 min access, 7 day refresh)
- RBAC enforced at API layer
- Session invalidation on password change

## Secrets
- All secrets in environment variables
- Never in code, config files, or comments
- Never logged (redact in structured logging)
- Rotation policy: 90 days

## Transport
- HTTPS everywhere (no HTTP endpoints)
- CORS restricted to known origins
- CSP headers configured
- HSTS enabled
- Secure cookie flags (HttpOnly, Secure, SameSite)

## Dependencies
- Automated scanning (Dependabot, Snyk)
- No packages with known critical CVEs
- License compliance check
- Monthly manual audit

## Review Triggers
Security review required for ANY change to:
- Authentication or authorization logic
- Data models containing PII
- API endpoints (new or modified)
- Dependency additions or updates
- Infrastructure configuration
