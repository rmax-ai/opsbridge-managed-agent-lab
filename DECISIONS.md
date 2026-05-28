# Decisions

## Major assumptions

1. Claude Managed Agents API is available and stable (managed-agents-2026-04-01)
2. Dreams API uses dreaming-2026-04-21 beta surface
3. Self-hosted sandbox workers communicate via the public Managed Agents API
4. MCP tunnel is optional — streamable HTTP is sufficient for demo purposes
5. Demo does not require real Jira, PagerDuty, GitHub or production credentials

## Key decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| UI framework | Streamlit | Fast iteration, minimal JS, built-in components |
| Backend | FastAPI | Async SSE, webhook handling, RESTful |
| Database | SQLite | Zero infrastructure, suitable for demo scale |
| MCP transport | Streamable HTTP | Simpler than SSE transport for demo |
| Custom tools | Application-side | Demonstrates tool loop governance |
| Agent definitions | YAML config files | Easy to inspect and modify |
| Two profiles | Cloud + self-hosted | Covers both product paths |
| Memory | Native Managed Agents API | Demonstrates true product capability |

## Known limitations

- Not designed for production multi-tenancy
- No real external service integration
- Synthetic OpsHub data is simplified
- Self-hosted sandbox uses Docker Compose, not full Kubernetes
