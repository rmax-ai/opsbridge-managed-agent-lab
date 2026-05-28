"""Demo scenario API routes."""

from __future__ import annotations

from datetime import datetime
from typing import cast

from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel, ConfigDict

from .state import MockBackendStore

router = APIRouter(prefix="/api/scenarios", tags=["scenarios"])


class ScenarioResponse(BaseModel):
    """JSON view of a demo scenario."""

    model_config = ConfigDict(extra="forbid")

    id: str
    name: str
    incident_id: str
    description: str


class ScenarioListResponse(BaseModel):
    """List response for demo scenarios."""

    model_config = ConfigDict(extra="forbid")

    scenarios: list[ScenarioResponse]


class ScenarioStartResponse(BaseModel):
    """Response for starting a demo scenario."""

    model_config = ConfigDict(extra="forbid")

    scenario_id: str
    session_id: str
    incident_id: str
    status: str
    started_at: datetime


def _store(request: Request) -> MockBackendStore:
    """Return the shared backend store."""
    return cast(MockBackendStore, request.app.state.backend)


@router.get("", response_model=ScenarioListResponse)
async def list_scenarios(request: Request) -> ScenarioListResponse:
    """List available demo scenarios."""
    scenarios = [
        ScenarioResponse.model_validate(record.model_dump())
        for record in _store(request).list_scenarios()
    ]
    return ScenarioListResponse(scenarios=scenarios)


@router.post(
    "/{scenario_id}/start",
    response_model=ScenarioStartResponse,
    status_code=status.HTTP_201_CREATED,
)
async def start_scenario(scenario_id: str, request: Request) -> ScenarioStartResponse:
    """Start a scenario and return the created session."""
    session = _store(request).start_scenario(scenario_id)
    if session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="scenario not found")
    return ScenarioStartResponse(
        scenario_id=scenario_id,
        session_id=session.id,
        incident_id=session.incident_id,
        status=session.status,
        started_at=session.updated_at,
    )
