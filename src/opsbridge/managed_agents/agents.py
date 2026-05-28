"""Agent definition helpers."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, ConfigDict, Field

from .client import ManagedAgentClient

LOGGER = logging.getLogger(__name__)


class Agent(BaseModel):
    """Managed Agent resource."""

    model_config = ConfigDict(extra="allow")

    id: str | None = None
    name: str
    role: str
    instructions: str
    tools: dict[str, list[str]] = Field(default_factory=dict)
    mcp_servers: list[dict[str, str]] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)
    permissions: dict[str, str] = Field(default_factory=dict)


def _normalize_mcp_servers(mcp_config: object) -> list[dict[str, str]]:
    """Normalize MCP server config to a list of dicts."""
    if not mcp_config:
        return []
    if isinstance(mcp_config, list):
        result: list[dict[str, str]] = []
        for entry in mcp_config:
            if isinstance(entry, dict):
                result.append({str(k): str(v) for k, v in entry.items()})
        return result
    return []


def load_agent_from_yaml(path: Path) -> dict[str, Any]:
    """Load an agent configuration from YAML."""
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise ValueError(f"Agent config at {path} must be a mapping")
    mcp_servers = _normalize_mcp_servers(data.get("mcp_servers"))
    data["mcp_servers"] = mcp_servers
    return data


def create_agent(
    client: ManagedAgentClient,
    name: str,
    role: str,
    instructions: str,
    tools: dict[str, list[str]],
    mcp_servers: list[dict[str, str]],
    skills: list[str],
    permissions: dict[str, str],
) -> Agent:
    """Create a managed agent."""
    result = client.call(
        "agents",
        "create",
        name=name,
        role=role,
        instructions=instructions,
        tools=tools,
        mcp_servers=mcp_servers,
        skills=skills,
        permissions=permissions,
    )
    if isinstance(result, dict):
        return Agent.model_validate(result)
    return Agent.model_validate(result.model_dump())


def get_agent(client: ManagedAgentClient, agent_id: str) -> Agent:
    """Fetch an agent by ID."""
    result = client.call("agents", "retrieve", agent_id=agent_id)
    if isinstance(result, dict):
        return Agent.model_validate(result)
    return Agent.model_validate(result.model_dump())


def list_agents(client: ManagedAgentClient) -> list[Agent]:
    """List managed agents."""
    result = client.call("agents", "list")
    items = client.extract_list(result)
    return [
        Agent.model_validate(item if isinstance(item, dict) else item.model_dump())
        for item in items
    ]


def update_agent(client: ManagedAgentClient, agent_id: str, **kwargs: Any) -> Agent:
    """Update an agent."""
    result = client.call("agents", "update", agent_id=agent_id, **kwargs)
    if isinstance(result, dict):
        return Agent.model_validate(result)
    return Agent.model_validate(result.model_dump())


def delete_agent(client: ManagedAgentClient, agent_id: str) -> None:
    """Delete an agent."""
    client.call("agents", "delete", agent_id=agent_id)
