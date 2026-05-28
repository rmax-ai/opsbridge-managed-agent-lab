"""Approval and operator-control API routes."""

from __future__ import annotations

from datetime import datetime
from typing import cast

from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel, ConfigDict

from .state import MockBackendStore, SessionRecord

router = APIRouter(prefix="/api/sessions", tags=["approvals"])


class SessionActionRequest(BaseModel):
    """Optional operator message for a control action."""

    model_config = ConfigDict(extra="forbid")

    reason: str | None = None


class SessionActionResponse(BaseModel):
    """Response for a session control mutation."""

    model_config = ConfigDict(extra="forbid")

    session_id: str
    action: str
    status: str
    reason: str | None = None
    updated_at: datetime


def _store(request: Request) -> MockBackendStore:
    """Return the shared backend store."""
    return cast(MockBackendStore, request.app.state.backend)


def _require_session(request: Request, session_id: str) -> SessionRecord:
    """Fetch a session or raise 404."""
    record = _store(request).get_session(session_id)
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="session not found")
    return record


async def _apply_action(
    request: Request,
    session_id: str,
    action: str,
    next_status: str,
    payload: SessionActionRequest,
) -> SessionActionResponse:
    """Apply a control action to a session."""
    record = _require_session(request, session_id)
    _store(request).append_event(
        record.id,
        f"session.{action}",
        {"reason": payload.reason or "", "action": action},
    )
    updated = _store(request).set_session_status(record.id, next_status, payload.reason)
    return SessionActionResponse(
        session_id=updated.id,
        action=action,
        status=updated.status,
        reason=payload.reason,
        updated_at=updated.updated_at,
    )


@router.post("/{session_id}/approve", response_model=SessionActionResponse)
async def approve_session(
    session_id: str, request: Request, payload: SessionActionRequest
) -> SessionActionResponse:
    """Approve the next pending operator action."""
    return await _apply_action(request, session_id, "approve", "running", payload)


@router.post("/{session_id}/deny", response_model=SessionActionResponse)
async def deny_session(
    session_id: str, request: Request, payload: SessionActionRequest
) -> SessionActionResponse:
    """Deny the next pending operator action."""
    return await _apply_action(request, session_id, "deny", "idle", payload)


@router.post("/{session_id}/interrupt", response_model=SessionActionResponse)
async def interrupt_session(
    session_id: str, request: Request, payload: SessionActionRequest
) -> SessionActionResponse:
    """Interrupt an in-flight session."""
    return await _apply_action(request, session_id, "interrupt", "idle", payload)


@router.post(
    "/{session_id}/resume",
    response_model=SessionActionResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def resume_session(
    session_id: str, request: Request, payload: SessionActionRequest
) -> SessionActionResponse:
    """Resume a paused session."""
    return await _apply_action(request, session_id, "resume", "running", payload)
