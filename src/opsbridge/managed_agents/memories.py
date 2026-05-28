"""Memory store helpers."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from .client import ManagedAgentClient


class MemoryStore(BaseModel):
    """Memory store resource."""

    model_config = ConfigDict(extra="allow")

    id: str | None = None
    name: str
    memory_type: str = "read_write"


class MemoryFile(BaseModel):
    """Memory file representation."""

    model_config = ConfigDict(extra="allow")

    path: str
    content_type: str | None = None


def create_memory_store(
    client: ManagedAgentClient, name: str, memory_type: str = "read_write"
) -> MemoryStore:
    """Create a memory store."""
    result = client.call("memory_stores", "create", name=name, memory_type=memory_type)
    if isinstance(result, dict):
        return MemoryStore.model_validate(result)
    return MemoryStore.model_validate(result.model_dump())


def get_memory_store(client: ManagedAgentClient, store_id: str) -> MemoryStore:
    """Fetch a memory store."""
    result = client.call("memory_stores", "retrieve", store_id=store_id)
    if isinstance(result, dict):
        return MemoryStore.model_validate(result)
    return MemoryStore.model_validate(result.model_dump())


def list_memory_stores(client: ManagedAgentClient) -> list[MemoryStore]:
    """List memory stores."""
    result = client.call("memory_stores", "list")
    return [
        MemoryStore.model_validate(item if isinstance(item, dict) else item.model_dump())
        for item in client.extract_list(result)
    ]


def list_memory_files(client: ManagedAgentClient, store_id: str) -> list[MemoryFile]:
    """List files in a memory store."""
    result = client.call("memory_stores", "list_files", store_id=store_id)
    return [
        MemoryFile.model_validate(item if isinstance(item, dict) else item.model_dump())
        for item in client.extract_list(result)
    ]


def get_memory_file(client: ManagedAgentClient, store_id: str, file_path: str) -> str:
    """Read a file from a memory store."""
    result = client.call("memory_stores", "get_file", store_id=store_id, file_path=file_path)
    if isinstance(result, str):
        return result
    if isinstance(result, dict):
        return str(result.get("content", ""))
    return str(getattr(result, "content", ""))
