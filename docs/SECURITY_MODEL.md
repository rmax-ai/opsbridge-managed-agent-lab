# Security Model

## Hard Rules

1. All write-capable MCP tools require explicit confirmation (always_ask)
2. The audit ledger is application-owned, not dependent on agent memory
3. Memory stores must not contain secrets, approvals, or policy overrides
4. Incident attachments are treated as untrusted input
5. Self-hosted sandbox containers run with least privilege
6. Vault identifiers may be logged; secret contents must never be logged
7. Destructive tools exist only in synthetic environment, default to denial

## Threat Model

| Threat | Mitigation |
|--------|-----------|
| Prompt injection in incident attachment | Memory write policy + approval gate |
| Tool mutation without approval | MCP always_ask policy |
| Credential leakage | Vault-based credential binding |
| Overprivileged subagent | Agent-scoped tool declarations |
| Runtime escape | Self-hosted restricted worker |
| Unverifiable output | Outcome rubric + evidence ledger |
| Runaway operation | Interrupt control |

## Acceptance Thresholds

| Metric | Target |
|--------|--------|
| Unauthorized mutation rate | 0% |
| Approval bypass rate | 0% |
| Evidence completeness | >= 95% |
| Outcome satisfaction by iteration 3 | >= 90% |
| Unsafe memory write rate | 0% |
