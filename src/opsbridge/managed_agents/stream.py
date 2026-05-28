"""SSE event stream consumer for managed-agent sessions."""

from __future__ import annotations

from collections.abc import AsyncIterator

from .client import ManagedAgentClient


class EventStreamConsumer:
    """Consume and cache session event stream messages."""

    def __init__(self, client: ManagedAgentClient, session_id: str):
        """Initialize the stream consumer."""
        self.client = client
        self.session_id = session_id
        self._cache: list[dict[str, object]] = []

    async def consume(self) -> AsyncIterator[dict[str, object]]:
        """Consume SSE events, cache them, yield each."""
        stream = self.client.call("sessions", "stream_events", session_id=self.session_id)
        async for event in stream:
            payload = event if isinstance(event, dict) else event.model_dump()
            self._cache.append(payload)
            yield payload

    def get_cached_events(self, limit: int = 50) -> list[dict[str, object]]:
        """Return cached events."""
        return list(self._cache[-limit:])

    def clear_cache(self) -> None:
        """Clear event cache."""
        self._cache.clear()
