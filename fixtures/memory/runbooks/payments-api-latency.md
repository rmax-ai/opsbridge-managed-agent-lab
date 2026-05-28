# Payments API Latency — Runbook

## Investigation Steps

1. Verify recent deployments in the incident window
2. Check database connection pool metrics
3. Inspect config diffs for runtime environment changes
4. Correlate latency spike with pool saturation

## Key Metrics

- P99 latency threshold: 500ms
- DB pool saturation warning: > 80%
- Auth error rate warning: > 5%

## Remediation Options

1. **Rollback deployment** — if a config change correlates with the incident
2. **Scale up pool** — if temporary capacity increase is safer
3. **Traffic shift** — if the issue is localized

## Post-Remediation Validation

- Monitor P99 latency for 15 minutes
- Check pool saturation returns to < 60%
- Verify auth error rate below 1%
