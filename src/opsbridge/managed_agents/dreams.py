"""Dream job helpers."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from .client import ManagedAgentClient


class Dream(BaseModel):
    """Dream resource."""

    model_config = ConfigDict(extra="allow")

    id: str | None = None
    memory_store_id: str
    session_ids: list[str] = Field(default_factory=list)
    instructions: str


class DreamStatus(BaseModel):
    """Dream status resource."""

    model_config = ConfigDict(extra="allow")

    id: str
    status: str


class DreamResult(BaseModel):
    """Dream result resource."""

    model_config = ConfigDict(extra="allow")

    dream_id: str
    consolidated_store_id: str | None = None


def create_dream(
    client: ManagedAgentClient, memory_store_id: str, session_ids: list[str], instructions: str
) -> Dream:
    """Create a dream job."""
    result = client.call(
        "dreams",
        "create",
        memory_store_id=memory_store_id,
        session_ids=session_ids,
        instructions=instructions,
    )
    if isinstance(result, dict):
        return Dream.model_validate(result)
    return Dream.model_validate(result.model_dump())


def get_dream_status(client: ManagedAgentClient, dream_id: str) -> DreamStatus:
    """Fetch dream status."""
    result = client.call("dreams", "status", dream_id=dream_id)
    if isinstance(result, dict):
        return DreamStatus.model_validate(result)
    return DreamStatus.model_validate(result.model_dump())


def get_dream_result(client: ManagedAgentClient, dream_id: str) -> DreamResult:
    """Fetch dream result."""
    result = client.call("dreams", "result", dream_id=dream_id)
    if isinstance(result, dict):
        return DreamResult.model_validate(result)
    return DreamResult.model_validate(result.model_dump())
