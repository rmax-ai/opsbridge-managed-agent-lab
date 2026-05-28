# Production Write Controls

## Policy: OPS-WRITE-001

Write actions that change production runtime state require documented evidence and explicit human approval.

## Classification

| Action Type | Approval Required | Default |
|-------------|-------------------|---------|
| Read-only diagnostics | No | Allow |
| Configuration change | Yes | Ask |
| Deployment rollback | Yes | Ask |
| Data mutation | Yes | Ask |
| Destructive operation | Yes | Deny |

## Evidence Requirements

For approval-required actions, the agent must provide:
1. Root cause summary
2. Supporting metrics
3. Rollback plan (for deployment changes)
4. Post-action validation plan
