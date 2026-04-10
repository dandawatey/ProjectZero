# Feature Flag Rollout Rules

## Flag Types
- **Boolean**: On/off for all users
- **Percentage**: Gradual rollout (10% → 25% → 50% → 100%)
- **User Segment**: Specific user groups (beta testers, enterprise, region)
- **Environment**: Different behavior per environment

## Lifecycle
1. **Create**: During /implement, when feature needs controlled rollout
2. **Enable**: Start with small percentage or specific segment
3. **Monitor**: Watch error rates and metrics for flagged feature
4. **Expand**: Gradually increase rollout if metrics are good
5. **Complete**: Remove flag once 100% rollout is stable for 2 weeks
6. **Clean up**: Remove flag code, merge as permanent

## Rules
- Every flag has an owner and expiry date
- Flags older than 90 days without activity are flagged for cleanup
- Production-only flags should have monitoring dashboard
- Flag removal is a ticket (tracked work)
