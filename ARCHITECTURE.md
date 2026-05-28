# OpsBridge — Architecture

## Problem statement

Demo how Claude Managed Agents provide governed, auditable, and reusable incident response — from investigation through remediation to organizational learning — across cloud and self-hosted execution profiles.

## Design goals

1. Demonstrate all Managed Agents features (agents, environments, sessions, events, tools, MCP, vaults, outcomes, memory, dreams, subagents, webhooks, skills, sandboxes)
2. Separate the managed agent runtime, execution boundary, and enterprise control plane
3. Provide two execution profiles: cloud (full feature set) and self-hosted (private-network execution)

## Component diagram

```
┌─────────────┐     ┌───────────────────────────────────────┐
│  Streamlit   │────▶│          FastAPI Backend              │
│  UI          │     │  (Sessions, Approvals, Webhooks,     │
└─────────────┘     │   Memory, Scenarios, SSE)             │
                    └───────────┬───────────────────────────┘
                                │
                    ┌──────────▼───────────────────────────┐
                    │       Claude Managed Agents API       │
                    │  (coordinator + 4 specialist agents)  │
                    │  Outcomes, Memory, Dreams, Events     │
                    └───────────┬───────────────────────────┘
                                │
              ┌─────────────────┼──────────────────┐
              ▼                 ▼                   ▼
    ┌─────────────────┐ ┌──────────────┐ ┌──────────────────┐
    │  OpsHub MCP     │ │ Self-hosted │ │  Audit Ledger    │
    │  Server         │ │ Sandbox      │ │  (SQLite)        │
    │  (Synthetic)    │ │ Worker       │ │                  │
    └─────────────────┘ └──────────────┘ └──────────────────┘
```

## Key design decisions

- **Streamlit** for rapid UI prototyping (7 pages)
- **FastAPI** for backend: SSE streaming, webhooks, REST endpoints
- **SQLite** for both operational state and audit ledger (zero infrastructure)
- **MCP via streamable HTTP** for synthetic OpsHub tools
- **Two profiles** to demonstrate both cloud and self-hosted execution
- **Application-side custom tools** for policy evaluation and audit recording (not MCP-side)

## Module layout

```
src/opsbridge/
├── api/              # FastAPI routes
├── managed_agents/   # Anthropic SDK integration
├── tools/            # Custom application tools
├── ledger/           # Audit ledger (SQLite)
└── config.py         # Configuration (pydantic-settings)

mcp_server/           # Synthetic OpsHub MCP server
  ├── server.py
  ├── auth.py
  ├── tools_read.py
  ├── tools_write.py
  ├── state.py        # In-memory operational state
  └── seed.py         # Seed data for demos

sandbox_worker/       # Self-hosted execution worker
  ├── Dockerfile
  └── worker.py

app/ui/               # Streamlit pages
  ├── streamlit_app.py
  ├── pages/
  └── components/

config/               # Agent, environment, outcome, policy configs
skills/               # Custom incident-response skill
fixtures/             # Incident data and seed memory
tests/                # Unit, integration, governance evals
```
