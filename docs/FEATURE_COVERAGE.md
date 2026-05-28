# Managed Agents Feature Coverage

| Feature | Demo Implementation | Status |
|---------|-------------------|--------|
| Agents | 5 configured agents (coordinator + 4 specialists) | ✅ |
| Environments | Cloud + self-hosted profiles | ✅ |
| Sessions | Incident investigation per session | ✅ |
| Event Streaming | SSE from session via FastAPI | ✅ |
| Session Durability | Reconnect to running session | ✅ |
| Built-in Tools | File read/write, grep, glob | ✅ |
| Files API | Upload incident packets | ✅ |
| Skills | incident-response-protocol skill | ✅ |
| Custom Tools | policy_check, audit_recorder, impact_calculator | ✅ |
| MCP Server | Synthetic OpsHub (17 tools, authenticated) | ✅ |
| MCP Tunnel | Documented for private-network profile | ✅ |
| Vaults | Bearer credential attachment | ✅ |
| Permission Policies | always_allow / always_ask / default_deny | ✅ |
| Subagents | Metrics, Deployment, Policy, Remediation | ✅ |
| Outcomes | 9-criterion rubric with revision loop | ✅ |
| Interrupt | Pause/stop/resume with revised instruction | ✅ |
| Webhooks | POST /webhooks/anthropic handler | ✅ |
| Memory | Read-only reference + read-write learnings | ✅ |
| Dreams | Consolidation with diff/adopt/discard | ✅ |
| Self-Hosted Sandbox | Docker Compose + local worker | ✅ |
| Console Builder | README walkthrough | ✅ |
