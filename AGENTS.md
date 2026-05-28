# AGENTS.md – OpsBridge Managed Agent Lab

Guidelines for AI coding agents contributing to this project.

## 1. Code Organisation

- **Python 3.12+** with `src/` layout under `src/opsbridge/`
- Each domain has its own module: `managed_agents/`, `mcp_server/`, `tools/`, `ledger/`, `ui/`, `api/`
- Tests mirror source structure under `tests/`
- Configuration files go in `config/`
- Fixtures in `fixtures/`

## 2. Error Handling

- Use `Result` pattern (or explicit exception types) for domain logic
- Custom exceptions in `src/opsbridge/exceptions.py`
- Log using `structlog` or `logging` module
- No bare `except:` — always catch specific exceptions

## 3. Type System

- Strict type hints everywhere (mypy strict mode)
- Pydantic v2 for all data models and settings
- SQLModel/SQLAlchemy for database models
- No `Any` without strong justification

## 4. Testing

- `pytest` with `pytest-asyncio` for async tests
- Unit tests for pure logic, integration tests for IO boundaries
- Governance evals in `tests/evals/`
- Mock external services (Anthropic API, MCP server) — never hit production endpoints in tests

## 5. Documentation

- Docstrings on all public functions and classes (Google style)
- README updated with any new features or commands
- Architecture documentation stays accurate with code

## 6. Dependencies

- Pinned in `pyproject.toml` with minimal version bounds
- No additional dependencies without updating `pyproject.toml`

## 7. Formatting & Linting

- `ruff format` for formatting
- `ruff check` for linting
- `mypy src/` for type checking

## 8. CI / CD

- All tests must pass before merge
- Ruff and mypy gates
- No pre-existing failures — fix or ignore known issues explicitly

## 9. References

- `docs/ARCHITECTURE.md`
- `docs/DEMO_SCRIPT.md`
- `docs/RUNBOOK.md`
