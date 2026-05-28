# High-Quality Incident Report

## Investigation Summary

**Incident:** INC-042
**Service:** payments-api
**Severity:** SEV1
**Root Cause:** Database connection pool maximum reduced from 120 to 12

## Evidence

1. **P99 latency increase**: 180ms → 2,400ms (source: get_incident_metrics)
2. **DB pool saturation**: 100% immediately after deploy (source: get_incident_metrics)
3. **Config diff**: DB_POOL_MAX=120 → DB_POOL_MAX=12 (source: get_deploy_diff)
4. **Error samples**: Connection timeout errors (source: get_error_samples)

## Remediation

- **Action**: rollback_deployment(service="payments-api", deploy_id="payments-api@9f13d2")
- **Risk**: Short-lived request failures during rollout
- **Reversibility**: Redeploy revision 9f13d2 if needed
- **Validation**: Check P99 < 500ms, pool saturation < 60%, error rate < 1%

## Approval

- **Classification**: approval_required
- **Decision**: Approved by operator
- **Evidence attached**: evidence_bundle.json
