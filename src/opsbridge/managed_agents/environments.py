"""Managed environment helpers."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field
import yaml

from .client import ManagedAgentClient
from .self_hosted import create_sandbox_config


LOGGER = logging.getLogger(__name__)


class Environment(BaseModel):
    """Managed Agent environment resource."""

    model_config = ConfigDict(extra="allow")

    id: str | None = None
    name: str
    python_version: str
    allowlist: list[str] = Field(default_factory=list)
    tools: list[str] = Field(default_factory=list)
    outputs_dir: str
    self_hosted: bool = False
    sandbox_config: dict[str, object] | None = None


def load_environment_from_yaml(path: Path) -> dict[str, Any]:
    """Load an environment configuration from YAML."""
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise ValueError(f"Environment config at {path} must be a mapping")
    LOGGER.debug("Loaded environment YAML", extra={"path": str(path), "name": data.get("name")})
    return data


def create_environment(
    client: ManagedAgentClient,
    name: str,
    python_version: str,
    allowlist: list[str],
    tools: list[str],
    outputs_dir: str,
    self_hosted: bool = False,
    sandbox_config: dict[str, object] | None = None,
) -> Environment:
    """Create a managed environment."""
    payload: dict[str, object] = {
        "name": name,
        "python_version": python_version,
        "allowlist": allowlist,
        "tools": tools,
        "outputs_dir": outputs_dir,
        "self_hosted": self_hosted,
    }
    if self_hosted and sandbox_config is not None:
        payload["sandbox_config"] = sandbox_config
    result = client.call("environments", "create", **payload)
    if isinstance(result, dict):
        return Environment.model_validate(result)
    return Environment.model_validate(result.model_dump())


def create_environment_from_config(
    client: ManagedAgentClient, config: dict[str, Any]
) -> Environment:
    """Create an environment directly from loaded YAML config."""
    sandbox_config: dict[str, object] | None = None
    self_hosted = bool(config.get("self_hosted", False))
    if self_hosted:
        sandbox_worker = config.get("sandbox_worker", {})
        if isinstance(sandbox_worker, dict):
            sandbox_config = create_sandbox_config(
                name=str(config["name"]),
                worker_image=str(sandbox_worker.get("image", "")),
                workdir=str(sandbox_worker.get("workdir", "/workspace")),
                network_policy={"allowlist": list(config["network"]["allowlist"])},
                filesystem_policy={"outputs_dir": str(config["outputs"]["directory"])},
            )
    return create_environment(
        client=client,
        name=str(config["name"]),
        python_version=str(config["requirements"]["python_version"]),
        allowlist=[str(item) for item in config["network"]["allowlist"]],
        tools=[str(item) for item in config["tools"]["builtin"]],
        outputs_dir=str(config["outputs"]["directory"]),
        self_hosted=self_hosted,
        sandbox_config=sandbox_config,
    )


def get_environment(client: ManagedAgentClient, env_id: str) -> Environment:
    """Fetch an environment by ID."""
    result = client.call("environments", "retrieve", environment_id=env_id)
    if isinstance(result, dict):
        return Environment.model_validate(result)
    return Environment.model_validate(result.model_dump())


def delete_environment(client: ManagedAgentClient, env_id: str) -> None:
    """Delete an environment."""
    client.call("environments", "delete", environment_id=env_id)
