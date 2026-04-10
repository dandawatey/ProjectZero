# Release Readiness Checklist

## Code
- [ ] All features in release scope are status "Done"
- [ ] All PRs merged to release branch
- [ ] No open critical/high bugs

## Testing
- [ ] Full test suite passing (unit + integration + e2e)
- [ ] Coverage ≥ 80%
- [ ] Performance tests passed (no regressions)
- [ ] Security scan clean

## Documentation
- [ ] Changelog written
- [ ] API docs current
- [ ] User-facing docs updated

## Deployment
- [ ] Deployment plan documented
- [ ] Rollback plan documented and tested
- [ ] Environment configs verified
- [ ] Database migrations tested on staging copy

## Operations
- [ ] Monitoring configured
- [ ] Alerting configured
- [ ] Runbooks available
- [ ] On-call aware of release

## Sign-off
- [ ] Product Manager: features match requirements
- [ ] Engineering Lead: technical quality approved
- [ ] Security: scan clean, compliance met
