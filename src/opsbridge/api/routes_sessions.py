"""Session API routes."""

from __future__ import annotations

from datetime import datetime
from typing import cast

from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel, ConfigDict, Field
from sse_starlette import EventSourceResponse

from .state import MockBackendStore, SessionRecord

router = APIRouter(prefix="/api/sessions", tags=["sessions"])


class SessionResponse(BaseModel):
    """JSON view of a mock session."""

    model_config = ConfigDict(extra="forbid")

    id: str
    incident_id: str
    scenario_id: str | None = None
    status: str
    created_at: datetime
    updated_at: datetime
    metadata: dict[str, object] = Field(default_factory=dict)

    @classmethod
    def from_record(cls, record: SessionRecord) -> SessionResponse:
        """Build a response model from backend state."""
        return cls.model_validate(record.model_dump(exclude={"events"}))


class SessionListResponse(BaseModel):
    """List response for sessions."""

    model_config = ConfigDict(extra="forbid")

    sessions: list[SessionResponse]


class CreateSessionRequest(BaseModel):
    """Request payload for creating a session."""

    model_config = ConfigDict(extra="forbid")

    incident_id: str
    metadata: dict[str, object] = Field(default_factory=dict)


def _store(request: Request) -> MockBackendStore:
    """Return the shared backend store."""
    return cast(MockBackendStore, request.app.state.backend)


@router.get("", response_model=SessionListResponse)
async def list_sessions(request: Request) -> SessionListResponse:
    """List sessions."""
    sessions = [SessionResponse.from_record(record) for record in _store(request).list_sessions()]
    return SessionListResponse(sessions=sessions)


@router.post("", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(request: Request, payload: CreateSessionRequest) -> SessionResponse:
    """Create a new mock session."""
    record = _store(request).create_session(payload.incident_id, payload.metadata)
    return SessionResponse.from_record(record)


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(session_id: str, request: Request) -> SessionResponse:
    """Fetch a session by ID."""
    record = _store(request).get_session(session_id)
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="session not found")
    return SessionResponse.from_record(record)


@router.get("/{session_id}/stream")
async def stream_session(session_id: str, request: Request) -> EventSourceResponse:
    """Stream session events as SSE."""
    record = _store(request).get_session(session_id)
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="session not found")
    return EventSourceResponse(_store(request).stream_session_events(record.id))
