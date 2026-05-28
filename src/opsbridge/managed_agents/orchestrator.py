"""Session orchestration helpers for incident workflows."""

from __future__ import annotations

from collections.abc import AsyncIterator
from pathlib import Path
from typing import Protocol

from .client import ManagedAgentClient
from .outcomes import define_outcome
from .stream import EventStreamConsumer


REPO_ROOT = Path(__file__).resolve().parents[3]
RUBRIC_PATH = REPO_ROOT / "config" / "outcomes" / "incident_remediation_rubric.md"


class ManagedAgentProvisionerProtocol(Protocol):
    """Provisioner interface required by the orchestrator."""

    def create_session(
        self,
        agent_id: str,
        environment_id: str,
        vault_ids: list[str],
        memory_store_ids: list[str],
    ) -> str:
        """Create a session."""


class IncidentSessionOrchestrator:
    """Coordinate lifecycle operations for an incident session."""

    def __init__(self, client: ManagedAgentClient, provisioner: ManagedAgentProvisionerProtocol):
        """Initialize the orchestrator with client and provisioner dependencies."""
        self.client = client
        self.provisioner = provisioner

    def start_outcome(self, session_id: str, incident_id: str) -> None:
        """Define outcome using the incident remediation rubric."""
        instruction = (
            "Investigate and remediate incident "
            f"{incident_id}. Drive toward service restoration, policy-compliant execution, "
            "and a clear operator-ready summary."
        )
        define_outcome(self.client, session_id, instruction, RUBRIC_PATH)

    def stream_events(self, session_id: str) -> AsyncIterator[dict[str, object]]:
        """Yield events from the session."""
        return EventStreamConsumer(self.client, session_id).consume()

    def confirm_tool(self, session_id: str, tool_event_id: str, allow: bool) -> None:
        """Approve or deny a tool call."""
        self.client.call(
            "sessions",
            "send",
            session_id=session_id,
            input={
                "type": "user.custom_tool_result",
                "tool_event_id": tool_event_id,
                "allow": allow,
            },
        )

    def interrupt(self, session_id: str, reason: str) -> None:
        """Send user.interrupt with reason."""
        self.client.call(
            "sessions",
            "send",
            session_id=session_id,
            input={"type": "user.interrupt", "reason": reason},
        )

    def resume_with_instruction(self, session_id: str, instruction: str) -> None:
        """Resume with revised instruction after interrupt."""
        self.client.call(
            "sessions",
            "send",
            session_id=session_id,
            input={"type": "text", "text": instruction},
        )

    def get_session_status(self, session_id: str) -> str:
        """Return current session status (idle, running, requires_action, terminated)."""
        result = self.client.call("sessions", "retrieve", session_id=session_id)
        if isinstance(result, dict):
            status = result.get("status")
        else:
            status = getattr(result, "status", None)
        if not isinstance(status, str):
            raise ValueError(f"Session {session_id!r} did not expose a valid status")
        return status
