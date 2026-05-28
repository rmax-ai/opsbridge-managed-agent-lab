"""Configuration via pydantic-settings."""

from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration loaded from env vars and .env."""

    anthropic_api_key: str = ""
    managed_agents_api_url: str = "https://api.anthropic.com"
    managed_agents_beta: str = "managed-agents-2026-04-01"
    dreaming_beta: str = "dreaming-2026-04-21"

    opshub_mcp_url: str = "http://localhost:8001"
    opshub_auth_token: str = "demo-token-opsbridge-2026"

    api_host: str = "0.0.0.0"
    api_port: int = 8000
    streamlit_port: int = 8501

    audit_db_path: Path = Path("data/audit.db")
    ops_db_path: Path = Path("data/operations.db")

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
