# RUNBOOK — OpsBridge Managed Agent Lab

## Setup

```bash
# Prerequisites
pip install -e ".[dev]"

# Start OpsHub MCP server (synthetic enterprise systems)
uvicorn mcp_server.server:app --host 0.0.0.0 --port 8001

# Start FastAPI backend
uvicorn src.opsbridge.api.main:app --host 0.0.0.0 --port 8000

# Start Streamlit UI
streamlit run app/ui/streamlit_app.py --server.port 8501
```

## Makefile Commands

```bash
make bootstrap-cloud        # Provision cloud Managed Agents
make bootstrap-self-hosted  # Provision self-hosted profile
make seed-demo-data         # Seed OpsHub MCP data
make run-mcp-server         # Start MCP server (port 8001)
make run-api                # Start FastAPI backend (port 8000)
make run-ui                 # Start Streamlit UI (port 8501)
make test                   # Run all tests
make test-evals             # Run governance evals
make lint                   # Lint and type-check
make format                 # Auto-format
```

## Troubleshooting

### MCP Server won't start
- Check port 8001 is free: `lsof -i :8001`
- Verify .env has OPSHUB_AUTH_TOKEN set

### Tests fail with ModuleNotFoundError
- Ensure working directory is repo root
- Run `pip install -e ".[dev]"` first

### Streamlit UI blank
- Check FastAPI backend is running (port 8000)
- Check browser console for CORS errors

## Testing

```bash
# Unit tests
pytest tests/unit/ -v

# Governance evals
pytest tests/evals/ -v -m governance

# All tests
make test
```

## Cleanup

```bash
make clean                         # Remove DB files and pycache
git worktree remove ../<name>      # Remove Codex worktrees
```
