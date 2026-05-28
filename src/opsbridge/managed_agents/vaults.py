"""Vault helpers."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from .client import ManagedAgentClient


class Vault(BaseModel):
    """Vault resource."""

    model_config = ConfigDict(extra="allow")

    id: str | None = None
    name: str
    credential_type: str
    server_url: str
    scopes: list[str] = Field(default_factory=list)


def create_vault(
    client: ManagedAgentClient,
    name: str,
    credential_type: str,
    server_url: str,
    scopes: list[str],
    token: str,
) -> Vault:
    """Create a vault credential."""
    result = client.call(
        "vaults",
        "create",
        name=name,
        credential_type=credential_type,
        server_url=server_url,
        scopes=scopes,
        token=token,
    )
    if isinstance(result, dict):
        return Vault.model_validate(result)
    return Vault.model_validate(result.model_dump())


def get_vault(client: ManagedAgentClient, vault_id: str) -> Vault:
    """Fetch a vault."""
    result = client.call("vaults", "retrieve", vault_id=vault_id)
    if isinstance(result, dict):
        return Vault.model_validate(result)
    return Vault.model_validate(result.model_dump())


def delete_vault(client: ManagedAgentClient, vault_id: str) -> None:
    """Delete a vault."""
    client.call("vaults", "delete", vault_id=vault_id)
