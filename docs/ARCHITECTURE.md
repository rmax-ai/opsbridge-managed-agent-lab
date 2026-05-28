# OpsBridge — Architecture

## Problem Statement

Demo how Claude Managed Agents provide governed, auditable incident response — from investigation through remediation to organizational learning — across cloud and self-hosted execution profiles.

## System Architecture

```
┌─────────────┐     ┌──────────────────────────────────────┐
│  Streamlit   │────▶│          FastAPI Backend             │
│  UI (8501)  │     │  (Sessions, Approvals, Webhooks,    │
└─────────────┘     │   Memory, Scenarios, SSE, CORS)     │
                    └───────────┬──────────────────────────┘
                                │
                    ┌──────────▼──────────────────────────┐
                    │     Claude Managed Agents API        │
                    │  Coordinator + 4 Specialist Agents   │
                    │  Outcomes, Memory, Dreams, Events    │
                    └───────────┬──────────────────────────┘
                                │
              ┌─────────────────┼──────────────────┐
              ▼                 ▼                   ▼
    ┌─────────────────┐ ┌──────────────┐ ┌──────────────────┐
    │  OpsHub MCP     │ │ Self-hosted │ │  Audit Ledger    │
    │  Server (8001)  │ │ Sandbox      │ │  (SQLite)        │
    │  Authenticated  │ │ Worker       │ │                  │
    └─────────────────┘ └──────────────┘ └──────────────────┘
```

## Execution Profiles

### Cloud Profile
- Anthropic-managed cloud environment
- Full feature set: Memory, Dreams, Subagents, Approvals, Vaults
- Public MCP endpoint with OAuth/bearer auth

### Self-Hosted Profile
- Customer-controlled sandbox worker
- Private OpsHub service on internal network
- Same orchestration, approvals, and audit model
- No native Memory/Dreams (not currently supported)

## Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| UI | Streamlit | Fast iteration, minimal JS |
| Backend | FastAPI | Async SSE, webhooks, REST |
| MCP Transport | Streamable HTTP | Simpler than SSE transport |
| Custom Tools | Application-side | Demonstrates governance |
| Database | SQLite | Zero infrastructure |
| Audit Ledger | Application-owned | Not dependent on agent memory |

## Module Layout

```
src/opsbridge/
├── api/                # FastAPI routes
│   ├── main.py
│   ├── routes_sessions.py
│   ├── routes_approvals.py
│   ├── routes_memory.py
│   ├── routes_webhooks.py
│   ├── routes_demo_scenarios.py
│   └── state.py        # Mock backend store
├── managed_agents/     # Anthropic SDK integration
│   ├── client.py       # SDK wrapper
│   ├── agents.py       # Agent CRUD
│   ├── sessions.py     # Session CRUD
│   ├── environments.py # Environment CRUD
│   ├── events.py       # Event streaming
│   ├── outcomes.py     # Outcome helpers
│   ├── outcome_evaluator.py  # Rubric evaluation
│   ├── memories.py     # Memory store CRUD
│   ├── dreams.py       # Dream job management
│   ├── vaults.py       # Vault CRUD
│   ├── permissions.py  # Policy evaluation
│   ├── orchestrator.py # Incident lifecycle
│   ├── stream.py       # SSE event consumer
│   ├── provision.py    # Resource provisioning
│   └── self_hosted.py  # Sandbox config
├── tools/              # Custom application tools
│   ├── policy_check.py
│   ├── audit_recorder.py
│   └── impact_calculator.py
└── ledger/             # Audit ledger
    ├── models.py       # SQLModel tables
    ├── repository.py   # CRUD operations
    └── hashing.py      # SHA-256 digests

mcp_server/             # Synthetic OpsHub MCP
├── server.py
├── auth.py
├── state.py
├── tools_read.py
├── tools_write.py
└── seed.py

app/ui/                 # Streamlit UI
├── streamlit_app.py
├── pages/ (7 pages)
└── components/ (3 components)
```
