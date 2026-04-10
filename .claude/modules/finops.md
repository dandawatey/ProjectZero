# FinOps Module

## Cloud Cost Management
- Track costs per service, environment, and team using resource tags
- Mandatory tags: `team`, `environment`, `project`, `cost-center`
- Budget alerts at 80% and 100% thresholds
- Monthly cost reports to stakeholders

## Optimization Pipeline
1. **Identify**: Automated scans for unused resources, oversized instances
2. **Recommend**: Generate rightsizing and cleanup recommendations
3. **Approve**: Cost changes over threshold require team lead approval
4. **Implement**: Execute approved optimizations
5. **Verify**: Confirm cost reduction in next billing cycle

## Key Practices
- Reserved instances for predictable workloads (analyze 3-month usage first)
- Spot/preemptible instances for non-critical batch jobs
- Auto-scaling for variable workloads with min/max bounds
- Non-production environments auto-shutdown outside business hours
- Storage lifecycle policies (archive after 90 days, delete after 365)

## Reporting
- Weekly: Cost summary by service, anomaly detection
- Monthly: Trend analysis, budget vs actual, optimization impact
- Quarterly: Architecture review for cost efficiency, reserved instance planning
