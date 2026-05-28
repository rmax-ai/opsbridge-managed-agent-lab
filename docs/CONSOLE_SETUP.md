# Console Setup Guide

## Equivalent Agent Configuration in Anthropic Console

This guide shows how to configure the same agents manually in the [Anthropic Console](https://console.anthropic.com).

### Incident Commander Agent

1. Navigate to **Agents** → **Create Agent**
2. Name: `incident_commander`
3. Role: "Coordinates incident investigation, delegates specialist analysis..."
4. Instructions: Paste from `config/agents/incident_commander.yaml`
5. Tools: Enable `read`, `write`, `edit`, `glob`, `grep`
6. MCP Servers: Add `opshub` with read-only scope
7. Skills: Attach custom `incident-response-protocol` skill
8. Permissions: Set tool_call and bash to `always_allow`, mcp_write to `never`

### Specialist Agents

Create 4 additional agents following the YAML configs in `config/agents/`:
- `metrics_investigator` — read-only MCP tools for metrics
- `deployment_investigator` — read-only MCP tools + file tools
- `policy_reviewer` — custom tool `evaluate_action_policy`
- `remediation_executor` — MCP write tools with `always_ask`

### Environment

1. Navigate to **Environments** → **Create Environment**
2. Cloud demo: Python 3.12, allowlisted hosts
3. Self-hosted: Sandbox worker with local runtime

### Vault

1. Navigate to **Vaults** → **Create Vault**
2. Credential type: Bearer token
3. Scopes: `incidents:read`, `metrics:read`, `deploys:read`, `incidents:write`, `deploys:rollback`

### Outcome

1. Navigate to **Outcomes** → **Define Outcome**
2. Upload `config/outcomes/incident_remediation_rubric.md`
3. Max iterations: 3

### Memory

1. Navigate to **Memory** → **Create Store**
2. Create `ops_reference_material` (read-only)
3. Create `operator_learnings` (read-write)
