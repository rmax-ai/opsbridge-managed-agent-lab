# Incident INC-043: Checkout Service Dependency Outage

**Severity:** SEV2
**Service:** checkout-api
**Started:** 2026-05-27 15:00 UTC

## Summary

The checkout service experienced a latency spike at 15:00 UTC. Error rate reached 45%. No relevant deployment change was found. Upstream dependency provider-X is degraded.

## Observed Symptoms

- Latency spike at 15:00 UTC
- Error rate: 45%
- Dependency health: 42%
- Upstream provider: degraded

## Recent Changes

No deployment changes in the incident window.

## Error Samples

```
[15:01:05] ERROR checkout-api: Provider X 503 Service Unavailable
[15:01:19] ERROR checkout-api: Checkout dependency health check degraded
```

## Assessment

This appears to be an upstream dependency failure, not a code or configuration issue within our service. No rollback is needed.
