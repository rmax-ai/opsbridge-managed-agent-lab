"""Webhook ingestion routes."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import cast

from fastapi import APIRouter, Request
from pydantic import BaseModel, ConfigDict, Field

from .state import MockBackendStore

router = APIRouter(tags=["webhooks"])


class AnthropicWebhookRequest(BaseModel):
    """Incoming mock webhook payload."""

    model_config = ConfigDict(extra="allow")

    type: str
    session_id: str | None = None
    vault_id: str | None = None
    data: dict[str, object] = Field(default_factory=dict)


class WebhookResponse(BaseModel):
    """Acknowledgement for webhook processing."""

    model_config = ConfigDict(extra="forbid")

    accepted: bool
    event_type: str
    session_id: str | None = None
    vault_id: str | None = None
    status: str | None = None
    received_at: datetime


def _store(request: Request) -> MockBackendStore:
    """Return the shared backend store."""
    return cast(MockBackendStore, request.app.state.backend)


@router.post("/webhooks/anthropic", response_model=WebhookResponse)
async def handle_anthropic_webhook(
    request: Request, payload: AnthropicWebhookRequest
) -> WebhookResponse:
    """Handle mock session and vault webhooks."""
    status_value: str | None = None

    if payload.session_id is not None and payload.type.startswith("session.status_"):
        status_value = payload.type.removeprefix("session.status_")
        record = _store(request).get_session(payload.session_id)
        if record is not None:
            _store(request).set_session_status(record.id, status_value)
    elif payload.session_id is not None:
        record = _store(request).get_session(payload.session_id)
        if record is not None:
            _store(request).append_event(record.id, payload.type, payload.data)

    return WebhookResponse(
        accepted=True,
        event_type=payload.type,
        session_id=payload.session_id,
        vault_id=payload.vault_id,
        status=status_value,
        received_at=datetime.now(tz=UTC),
    )
