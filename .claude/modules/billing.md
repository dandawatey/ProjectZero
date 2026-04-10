# Billing Module

## Payment Integration
- **Provider**: Stripe (recommended) or equivalent
- **Approach**: Never store card data. Use provider tokenization. PCI DSS compliance via provider.
- **Webhook handling**: Verify signatures, process idempotently, queue for retry on failure.

## Subscription Management
- Create subscription (trial → active)
- Upgrade/downgrade (prorated)
- Cancel (immediate or end-of-period)
- Reactivate within grace period
- All state changes logged to audit trail

## Usage Metering
- Track usage events with timestamps
- Aggregate at billing period boundaries
- Calculate charges per pricing tier
- Show real-time usage in dashboard
- Alert at 80% and 100% of limits

## Invoice Generation
- Monthly or annual billing cycles
- Line items with descriptions
- Tax calculation via provider (Stripe Tax) or tax service
- PDF generation for download
- Email delivery

## Implementation Rules
- Billing service as separate module with own database
- All operations idempotent (safe to retry)
- Reconciliation job runs daily (compare provider state with local state)
- Refund requires approval workflow
- All billing events in audit log
