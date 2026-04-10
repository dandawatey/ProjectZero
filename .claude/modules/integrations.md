# Integrations Module

## Third-Party API Patterns
- **Adapter pattern**: Wrap external APIs in internal interfaces. Swap providers without changing business logic.
- **Interface-based**: Define TypeScript interfaces for external services. Implement per provider.
- **Example**: `interface PaymentProvider { charge(amount, token): Promise<Receipt> }` → Stripe implementation, test mock.

## Webhook Handling
1. Verify signature (provider-specific)
2. Check idempotency key (don't process same event twice)
3. Acknowledge receipt immediately (200 OK)
4. Process in background (queue for async handling)
5. Retry failed processing (max 5 retries, exponential backoff)

## Retry / Backoff Policy
- **Strategy**: Exponential backoff with jitter
- **Schedule**: 1s → 2s → 4s → 8s → 16s (5 retries max)
- **Jitter**: ±25% to prevent thundering herd
- **Circuit breaker**: Open after 5 failures in 60s, half-open after 30s

## API Key Management
- Keys in environment variables only
- Per-environment keys (dev/staging/prod)
- Key rotation support (accept old and new during rotation)
- Rate limit tracking (stay under provider limits with client-side throttle)

## Fallback Strategies
- Graceful degradation (feature works with reduced functionality)
- Cached responses (serve stale data with warning)
- Queue for retry (operations saved and retried when service recovers)
- Manual override (admin can trigger sync/retry)
