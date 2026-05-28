# PYTHON_DEVELOPMENT.md — Python Conventions for OpsBridge

## Project Layout

```
src/opsbridge/          # Main package (src layout)
  ├── __init__.py
  ├── config.py         # Settings via pydantic-settings
  ├── api/              # FastAPI routes
  ├── managed_agents/   # Anthropic Managed Agents SDK integration
  ├── tools/            # Custom application-controlled tools
  └── ledger/           # Audit ledger models and repository

mcp_server/             # Synthetic OpsHub MCP server (independent package)
  ├── __init__.py
  ├── server.py
  ├── auth.py
  ├── tools_read.py
  ├── tools_write.py
  ├── state.py
  └── seed.py

tests/
  ├── conftest.py
  ├── unit/
  ├── integration/
  └── evals/
```

## Conventions

- **Use `pathlib.Path`** for all filesystem paths — never `os.path`
- **Use `typing`** with modern syntax: `list[str]` not `List[str]` (Python 3.12)
- **Use `dataclass` or Pydantic v2 BaseModel** for data containers
- **Use `enum.StrEnum`** for string enums (Python 3.11+)
- **Use `logging.getLogger(__name__)`** everywhere; no print statements
- **Use `pydantic-settings`** for configuration via env vars and `.env`

## Async

- FastAPI routes use async/await
- MCP server uses synchronous code (simple in-memory operations)
- Anthropic SDK calls are async
- Use `asyncio` for stream/event handling

## Testing

- `pytest` with `pytest-asyncio` for async tests
- Fixtures in `tests/conftest.py` and `tests/mocks/conftest.py`
- Governance evals use parametrized pytest markers

## Useful Commands

```bash
ruff format src/ tests/
ruff check --fix src/ tests/
mypy src/
pytest -v --tb=short -x
pytest -m governance -v   # Run governance evals only
```
