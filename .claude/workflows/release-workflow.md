# Workflow: Release

## Steps
1. **Freeze**: Create release branch from develop
2. **Version**: Bump version in package.json, create git tag
3. **Test**: Run full test suite on release branch
4. **Security**: Run security scan (dependency + code)
5. **Changelog**: Generate from commit history since last release
6. **Stage**: Deploy to staging environment
7. **Smoke**: Run smoke tests on staging
8. **Approve**: Release manager confirms staging is good
9. **Deploy**: Deploy to production
10. **Verify**: Run health checks on production
11. **Tag**: Create GitHub release with changelog
12. **Document**: Update Confluence release page
13. **Notify**: Inform stakeholders

## Rollback Trigger
- Health check failure after deploy
- Error rate > 1% within 30 minutes
- P1 bug discovered in production

## Rollback Process
1. Execute `.claude/devops/rollback.sh`
2. Deploy previous version
3. Verify health checks pass
4. Create incident ticket
5. Postmortem within 48 hours
