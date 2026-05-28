"""Session management helpers."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from .client import ManagedAgentClient


class Session(BaseModel):
    """Managed Agent session resource."""

    model_config = ConfigDict(extra="allow")

    id: str | None = None
    agent_id: str
    environment_id: str
    vault_ids: list[str] = Field(default_factory=list)
    memory_store_ids: list[str] = Field(default_factory=list)
    metadata: dict[str, object] = Field(default_factory=dict)


def create_session(
    client: ManagedAgentClient,
    agent_id: str,
    environment_id: str,
    vault_ids: list[str] | None = None,
    memory_store_ids: list[str] | None = None,
    metadata: dict[str, object] | None = None,
) -> Session:
    """Create a managed-agent session."""
    result = client.call(
        "sessions",
        "create",
        agent_id=agent_id,
        environment_id=environment_id,
        vault_ids=vault_ids or [],
        memory_store_ids=memory_store_ids or [],
        metadata=metadata or {},
    )
    if isinstance(result, dict):
        return Session.model_validate(result)
    return Session.model_validate(result.model_dump())


def get_session(client: ManagedAgentClient, session_id: str) -> Session:
    """Fetch a session by ID."""
    result = client.call("sessions", "retrieve", session_id=session_id)
    if isinstance(result, dict):
        return Session.model_validate(result)
    return Session.model_validate(result.model_dump())


def list_sessions(client: ManagedAgentClient) -> list[Session]:
    """List managed-agent sessions."""
    result = client.call("sessions", "list")
    return [
        Session.model_validate(item if isinstance(item, dict) else item.model_dump())
        for item in client.extract_list(result)
    ]


def delete_session(client: ManagedAgentClient, session_id: str) -> None:
    """Delete a session."""
    client.call("sessions", "delete", session_id=session_id)


def send_text(client: ManagedAgentClient, session_id: str, text: str) -> None:
    """Send a text input event to a session."""
    client.call("sessions", "send", session_id=session_id, input={"type": "text", "text": text})


def send_message(client: ManagedAgentClient, session_id: str, content: object) -> None:
    """Send a message payload to a session."""
    client.call(
        "sessions",
        "send",
        session_id=session_id,
        input={"type": "message", "content": content},
    )
