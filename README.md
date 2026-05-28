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

## Architecture

See `docs/ARCHITECTURE.md` for full documentation.

## License

MIT
