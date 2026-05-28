# Incident INC-042: Authorization API P99 Latency Spike

**Severity:** SEV1
**Service:** payments-api
**Started:** 2026-05-27 14:30 UTC
**Reported by:** alerts@monitoring

## Summary

P99 latency for the Authorization API increased from a baseline of 180ms to 2.4s immediately after the deployment of `payments-api@9f13d2` at 14:30 UTC. Authorizations are failing with connection timeout errors.

## Observed Symptoms

- P99 latency: 2,400ms (baseline: 180ms)
- DB pool saturation: 100%
- Auth error rate: 18%
- Failed authorizations: 342 in 10 minutes

## Recent Changes

- Deployment `payments-api@9f13d2` at 14:29 UTC
- Author: deploy-bot
- Config environment template modified

## Error Samples

```
[14:31:11] ERROR payments-api: Timeout waiting for DB connection from pool (pool_max=12)
[14:31:42] ERROR payments-api: Authorization query queue exceeded 2s threshold
```

## Requested Actions

Investigate the P99 latency spike affecting card authorization traffic, determine the likely root cause, prepare a remediation proposal, and apply the fix only after approval.
