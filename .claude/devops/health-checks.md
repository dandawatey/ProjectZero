# Health Checks

## Endpoints
```
GET /health       → 200 {"status": "ok"}
GET /ready        → 200 {"status": "ready"} or 503 {"status": "not ready", "reason": "..."}
GET /health/deep  → 200 {"status": "ok", "checks": {"db": "ok", "redis": "ok", "external": "ok"}}
```

## Thresholds
- Response time: < 1 second for health endpoints
- Database: connection pool has available connections
- Redis: PING responds in < 100ms
- Memory: < 90% of limit
- CPU: < 80% sustained
- Disk: < 85% capacity
