# OpsBridge Managed Agent Lab

Python demo showcasing Claude Managed Agents for governed incident response.

## Quick Start

```bash
make bootstrap-cloud
make seed-demo-data
make run-ui
```

Profiles:
- **bootstrap-cloud** — full cloud profile with Memory, Dreams, Outcomes
- **bootstrap-self-hosted** — enterprise sandbox profile (private execution)
- **run-ui** — Streamlit dashboard (http://localhost:8501)
- **run-api** — FastAPI backend (http://localhost:8000)

## Backend API

The FastAPI backend exposes placeholder endpoints for the Streamlit demo:

- `/api/sessions` for session CRUD-style flows and SSE event streaming
- `/api/memory/stores` and `/api/memory/dreams` for mock Memory and Dreams operations
- `/api/scenarios` for starting seeded incident demos
- `/webhooks/anthropic` for mock session status and vault webhook ingestion

## Architecture

See `docs/ARCHITECTURE.md` for full documentation.

## License

MIT
