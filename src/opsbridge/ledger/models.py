"""Audit ledger persistence models."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from sqlmodel import Field, SQLModel


def utc_now() -> datetime:
    """Return the current UTC time."""
    return datetime.now(timezone.utc)


class WorkflowRun(SQLModel, table=True):
    """Top-level workflow execution record."""

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    claude_session_id: str = Field(index=True, unique=True)
    incident_id: str
    execution_profile: str
    started_at: datetime = Field(default_factory=utc_now)
    completed_at: datetime | None = None
    outcome_status: str = "running"


class EvidenceItem(SQLModel, table=True):
    """Evidence material captured during the workflow."""

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    workflow_run_id: str = Field(foreign_key="workflowrun.id", index=True)
    source_tool: str
    source_event_id: str
    content_hash: str
    payload_json: str
    recorded_at: datetime = Field(default_factory=utc_now)


class ActionProposal(SQLModel, table=True):
    """Proposed action awaiting or resulting from governance checks."""

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    workflow_run_id: str = Field(foreign_key="workflowrun.id", index=True)
    action_type: str
    target_resource: str
    arguments_json: str
    rationale: str
    policy_classification: str
    status: str


class ApprovalDecision(SQLModel, table=True):
    """Human review decision for an action proposal."""

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    proposal_id: str = Field(foreign_key="actionproposal.id", index=True)
    decision: str
    reviewer: str
    reason: str
    decided_at: datetime = Field(default_factory=utc_now)


class ExecutionRecord(SQLModel, table=True):
    """Execution result for an approved action proposal."""

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    proposal_id: str = Field(foreign_key="actionproposal.id", index=True)
    tool_name: str
    arguments_json: str
    result_json: str
    executed_at: datetime = Field(default_factory=utc_now)


class OutcomeEvaluation(SQLModel, table=True):
    """Recorded evaluation feedback for the workflow outcome."""

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    workflow_run_id: str = Field(foreign_key="workflowrun.id", index=True)
    iteration: int
    result: str
    feedback_json: str
    recorded_at: datetime = Field(default_factory=utc_now)
