"""Outcome helpers."""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from .client import ManagedAgentClient


class Outcome(BaseModel):
    """Outcome resource."""

    model_config = ConfigDict(extra="allow")

    id: str | None = None
    session_id: str
    instruction: str
    rubric: str


class OutcomeStatus(BaseModel):
    """Outcome status representation."""

    model_config = ConfigDict(extra="allow")

    status: str
    session_id: str


class Evaluation(BaseModel):
    """Outcome evaluation record."""

    model_config = ConfigDict(extra="allow")

    criterion: str
    score: float | int
    notes: str | None = None


def define_outcome(
    client: ManagedAgentClient, session_id: str, instruction: str, rubric_path: Path
) -> Outcome:
    """Define a managed-agent outcome using a rubric file."""
    rubric = rubric_path.read_text(encoding="utf-8")
    result = client.call(
        "outcomes",
        "create",
        session_id=session_id,
        instruction=instruction,
        rubric=rubric,
    )
    if isinstance(result, dict):
        return Outcome.model_validate(result)
    return Outcome.model_validate(result.model_dump())


def get_outcome_status(client: ManagedAgentClient, session_id: str) -> OutcomeStatus:
    """Fetch outcome status for a session."""
    result = client.call("outcomes", "status", session_id=session_id)
    if isinstance(result, dict):
        return OutcomeStatus.model_validate(result)
    return OutcomeStatus.model_validate(result.model_dump())


def get_outcome_evaluations(client: ManagedAgentClient, session_id: str) -> list[Evaluation]:
    """Fetch outcome evaluations for a session."""
    result = client.call("outcomes", "evaluations", session_id=session_id)
    return [
        Evaluation.model_validate(item if isinstance(item, dict) else item.model_dump())
        for item in client.extract_list(result)
    ]
