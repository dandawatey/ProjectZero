# Analytics Tracking Plan

## Event Categories

### Funnel Events
- page_view (page, referrer)
- signup_started (source)
- signup_completed (method)
- onboarding_step (step_number, step_name)
- first_key_action (action_type)
- subscription_started (plan, price)

### Engagement Events
- feature_used (feature_name, context)
- session_start (source)
- session_end (duration)
- search_performed (query, results_count)

### Error Events
- error_displayed (error_type, page, message)
- form_validation_failed (form, field, rule)
- api_error (endpoint, status_code)

## Implementation
- Centralized analytics service (single import)
- Events fired from UI layer (not API layer)
- All events include: timestamp, user_id (anonymous), session_id
- No PII in event properties
