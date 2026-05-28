"""In-memory backend state for the demo API."""

from __future__ import annotations

from collections.abc import AsyncIterator
from datetime import UTC, datetime
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field


class SessionEvent(BaseModel):
    """Event emitted for a mock session."""

    model_config = ConfigDict(extra="forbid")

    id: str
    type: str
    data: dict[str, object] = Field(default_factory=dict)
    created_at: datetime


class SessionRecord(BaseModel):
    """Mock session persisted by the API."""

    model_config = ConfigDict(extra="forbid")

    id: str
    incident_id: str
    scenario_id: str | None = None
    status: str
    created_at: datetime
    updated_at: datetime
    metadata: dict[str, object] = Field(default_factory=dict)
    events: list[SessionEvent] = Field(default_factory=list)


class MemoryStoreRecord(BaseModel):
    """Mock memory-store resource."""

    model_config = ConfigDict(extra="forbid")

    id: str
    name: str
    memory_type: str


class DreamRecord(BaseModel):
    """Mock dream record."""

    model_config = ConfigDict(extra="forbid")

    id: str
    memory_store_id: str
    session_ids: list[str] = Field(default_factory=list)
    instructions: str
    status: str
    created_at: datetime


class ScenarioRecord(BaseModel):
    """Mock demo scenario definition."""

    model_config = ConfigDict(extra="forbid")

    id: str
    name: str
    incident_id: str
    description: str


class MockBackendStore:
    """Small in-memory store that backs placeholder API routes."""

    def __init__(self) -> None:
        """Seed demo resources."""
        self.sessions: dict[str, SessionRecord] = {}
        self.memory_stores: dict[str, MemoryStoreRecord] = {
            "ops_reference_material": MemoryStoreRecord(
                id="ops_reference_material",
                name="Ops Reference Material",
                memory_type="read_only",
            ),
            "operator_learnings": MemoryStoreRecord(
                id="operator_learnings",
                name="Operator Learnings",
                memory_type="read_write",
            ),
        }
        self.dreams: dict[str, DreamRecord] = {}
        self.scenarios: dict[str, ScenarioRecord] = {
            "inc_042": ScenarioRecord(
                id="inc_042",
                name="Payments API latency spike",
                incident_id="inc_042",
                description="Investigate and restore degraded payment requests.",
            ),
            "inc_043": ScenarioRecord(
                id="inc_043",
                name="Worker pool saturation",
                incident_id="inc_043",
                description="Stabilize queue processing and reduce backlog growth.",
            ),
            "inc_044": ScenarioRecord(
                id="inc_044",
                name="MCP connectivity failure",
                incident_id="inc_044",
                description="Restore read access to the synthetic OpsHub MCP server.",
            ),
        }

    def list_sessions(self) -> list[SessionRecord]:
        """Return all known sessions."""
        return list(self.sessions.values())

    def get_session(self, session_id: str) -> SessionRecord | None:
        """Fetch a session if present."""
        return self.sessions.get(session_id)

    def create_session(
        self,
        incident_id: str,
        metadata: dict[str, object] | None = None,
        scenario_id: str | None = None,
    ) -> SessionRecord:
        """Create a new mock session."""
        now = datetime.now(tz=UTC)
        session = SessionRecord(
            id=f"session-{uuid4().hex[:8]}",
            incident_id=incident_id,
            scenario_id=scenario_id,
            status="running",
            created_at=now,
            updated_at=now,
            metadata=metadata or {},
            events=[],
        )
        self.sessions[session.id] = session
        self.append_event(
            session.id,
            "session.created",
            {"incident_id": incident_id, "scenario_id": scenario_id},
        )
        return session

    def append_event(
        self, session_id: str, event_type: str, data: dict[str, object]
    ) -> SessionEvent:
        """Add an event to a session."""
        session = self.sessions[session_id]
        event = SessionEvent(
            id=f"evt-{uuid4().hex[:8]}",
            type=event_type,
            data=data,
            created_at=datetime.now(tz=UTC),
        )
        session.events.append(event)
        session.updated_at = event.created_at
        return event

    def set_session_status(
        self, session_id: str, status: str, reason: str | None = None
    ) -> SessionRecord:
        """Update session status and record the change."""
        session = self.sessions[session_id]
        session.status = status
        payload: dict[str, object] = {"status": status}
        if reason is not None:
            payload["reason"] = reason
        self.append_event(session_id, f"session.status_{status}", payload)
        return session

    async def stream_session_events(self, session_id: str) -> AsyncIterator[dict[str, object]]:
        """Yield a finite SSE-compatible event stream for a session."""
        session = self.sessions[session_id]
        for event in session.events:
            yield {
                "event": event.type,
                "id": event.id,
                "data": {
                    "session_id": session.id,
                    "type": event.type,
                    "payload": event.data,
                    "created_at": event.created_at.isoformat(),
                },
            }

    def list_memory_stores(self) -> list[MemoryStoreRecord]:
        """Return memory stores."""
        return list(self.memory_stores.values())

    def create_dream(
        self, memory_store_id: str, session_ids: list[str], instructions: str
    ) -> DreamRecord:
        """Create a mock dream job."""
        dream = DreamRecord(
            id=f"dream-{uuid4().hex[:8]}",
            memory_store_id=memory_store_id,
            session_ids=session_ids,
            instructions=instructions,
            status="queued",
            created_at=datetime.now(tz=UTC),
        )
        self.dreams[dream.id] = dream
        return dream

    def list_scenarios(self) -> list[ScenarioRecord]:
        """Return available demo scenarios."""
        return list(self.scenarios.values())

    def start_scenario(self, scenario_id: str) -> SessionRecord | None:
        """Create a session for a known scenario."""
        scenario = self.scenarios.get(scenario_id)
        if scenario is None:
            return None
        session = self.create_session(
            incident_id=scenario.incident_id,
            metadata={"scenario_name": scenario.name},
            scenario_id=scenario.id,
        )
        self.append_event(session.id, "scenario.started", {"scenario_id": scenario.id})
        return session
