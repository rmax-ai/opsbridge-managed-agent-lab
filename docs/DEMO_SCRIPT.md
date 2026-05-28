# Demo Script

## Five-Minute Version

### Act 1: Show Configured Resources (30s)
- Open Control Room → show 5 configured agents, environment, vault, attached skill
- "All resources provisioned through the managed-agents API"

### Act 2: Start INC-042 (30s)
- Select "Authorization API Latency Spike" from scenario dropdown
- Click "Start Investigation"
- Observe session status change to "running"

### Act 3: Parallel Subagent Investigation (1 min)
- Open Thread Explorer → see 3 specialist agents working in parallel
- Metrics Investigator: analyzing latency, pool saturation, error samples
- Deployment Investigator: inspecting deploy diff (DB_POOL_MAX 120→12)
- Policy Reviewer: classifying proposed remediation path
- Each thread shows tool invocation timeline

### Act 4: Outcome Evaluation — First Pass Fails (30s)
- Outcome Inspector shows first iteration: NEEDS_REVISION
- Missing: post-action validation plan
- "The agent self-corrects — the rubric caught the gap"

### Act 5: Outcome Evaluation — Second Pass Passes (30s)
- Outcome Inspector shows iteration 2: SATISFIED (9/9 criteria)
- Evidence bundle complete, validation plan added

### Act 6: Approval Inbox (1 min)
- open Approval Inbox → 2 pending actions:
  - `rollback_deployment(payments-api@9f13d2)` — APPROVE
  - `delete_deployment_history(payments-api)` — DENY
- Click approve on rollback, deny on destructive action
- Show confirmation that only approved action executed

### Act 7: Recovery & Audit (30s)
- Control Room shows metrics recovered: P99 2.4s → 190ms
- Audit Ledger shows complete record: evidence, proposals, approvals, execution

### Act 8: Memory Lab (30s)
- Show memory stores: ops_reference_material (read-only), operator_learnings (read-write)
- Show existing Dream consolidation result
- "Organizational learning without trust compromise"

## Fifteen-Minute Version

Includes all of the above plus:
- **Authentication failure demo**: Start session without vault → show MCP auth error
- **Interrupt demo**: Click "Pause" mid-investigation → outcome marked interrupted → resume with revised instruction
- **Adversarial incident (INC-044)**: Show agent refusing to bypass governance, logging the attempt
- **Deployment Profiles comparison**: Cloud vs self-hosted feature table
