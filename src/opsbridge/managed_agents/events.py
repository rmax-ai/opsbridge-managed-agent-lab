"""Event management helpers."""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any

from .client import ManagedAgentClient


async def stream_events(
    client: ManagedAgentClient, session_id: str
) -> AsyncIterator[dict[str, Any]]:
    """Consume the session event stream."""
    stream = client.call("sessions", "stream_events", session_id=session_id)
    async for event in stream:
        if isinstance(event, dict):
            yield event
        else:
            yield event.model_dump()


def get_events(
    client: ManagedAgentClient, session_id: str, limit: int = 50
) -> list[dict[str, Any]]:
    """Get cached events for a session."""
    result = client.call("sessions", "list_events", session_id=session_id, limit=limit)
    events: list[dict[str, Any]] = []
    for item in client.extract_list(result):
        if isinstance(item, dict):
            events.append(item)
        else:
            events.append(item.model_dump())
    return events


def confirm_tool(
    client: ManagedAgentClient, session_id: str, tool_event_id: str, allow: bool = True
) -> None:
    """Confirm or deny a pending tool call."""
    client.call(
        "sessions",
        "send",
        session_id=session_id,
        input={
            "type": "user.custom_tool_result",
            "tool_event_id": tool_event_id,
            "allow": allow,
        },
    )


def send_interrupt(client: ManagedAgentClient, session_id: str) -> None:
    """Send a user interrupt event."""
    client.call(
        "sessions",
        "send",
        session_id=session_id,
        input={"type": "user.interrupt"},
    )
