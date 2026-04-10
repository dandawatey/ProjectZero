# Security Module

## OWASP Top 10 Checklist
1. **Injection**: Parameterized queries only. Never concatenate user input into SQL/commands.
2. **Broken Authentication**: Secure session management, bcrypt for passwords, JWT with short expiry, MFA support.
3. **Sensitive Data Exposure**: Encrypt at rest (AES-256) and in transit (TLS 1.3). No secrets in code.
4. **XML External Entities**: Disable external entity processing. Use JSON over XML.
5. **Broken Access Control**: RBAC enforced at API layer. Principle of least privilege. Test authorization on every endpoint.
6. **Security Misconfiguration**: Security headers (HSTS, CSP, X-Frame-Options). CORS restricted to known origins. No default credentials.
7. **Cross-Site Scripting**: Output encoding. Content Security Policy. No dangerouslySetInnerHTML without sanitization.
8. **Insecure Deserialization**: Validate and type-check all deserialized input. No eval().
9. **Using Components with Known Vulnerabilities**: Dependabot/Snyk enabled. No packages with known critical CVEs. Monthly dependency audit.
10. **Insufficient Logging & Monitoring**: Audit log for all auth events, data access, admin actions. Tamper-proof logging.

## Secret Management
- All secrets in environment variables (`.env`, never committed)
- Rotation policy: 90 days for API keys, 30 days for admin passwords
- Emergency rotation process documented
- Key vault for production (AWS Secrets Manager, HashiCorp Vault)

## Security Review Triggers
- Any change to authentication or authorization
- Any change to data models (especially PII)
- Any new API endpoint
- Any dependency addition or update
- Any infrastructure change
