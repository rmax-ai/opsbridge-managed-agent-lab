# Post-Remediation Validation

## Standard Validation Steps

1. **Latency check**: P99 should return to < 500ms (or within 20% of baseline)
2. **Error rate check**: Below 1%
3. **Pool saturation**: Below 60%
4. **Dependency health**: All upstream services "healthy"
5. **Duration**: Monitor for 15 minutes minimum

## Rollback Verification

- Confirm the rollback was applied (deployment marked inactive)
- Verify the previous active deployment is functioning
- Check that session/ticket state reflects the rollback

## Ticket Update

- Status: "mitigated" or "resolved"
- Summary includes: root cause, action taken, validation result
