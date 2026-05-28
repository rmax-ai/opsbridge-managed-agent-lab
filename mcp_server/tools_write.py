"""Write-capable MCP tools for synthetic OpsHub remediation."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Final, TypedDict

from mcp_server import state


class ToolDescriptor(TypedDict):
    """Metadata for a registered tool."""

    name: str
    mode: str
    description: str


class ToolResult(TypedDict):
    """Standard write-tool response envelope."""

    status: str
    data: dict[str, object]
    message: str


WRITE_TOOL_DEFINITIONS: Final[list[ToolDescriptor]] = [
    {
        "name": "rollback_deployment",
        "mode": "write",
        "description": "Rollback a service deployment after approval.",
    },
    {
        "name": "update_incident_ticket",
        "mode": "write",
        "description": "Update the incident ticket with evidence-backed changes.",
    },
    {
        "name": "post_incident_update",
        "mode": "write",
        "description": "Post an incident update note.",
    },
    {
        "name": "close_incident",
        "mode": "write",
        "description": "Close an incident with a resolution summary.",
    },
    {
        "name": "delete_deployment_history",
        "mode": "write",
        "description": "Delete deployment history for denial and governance demos.",
    },
]


def rollback_deployment(service: str, deploy_id: str, justification: str) -> ToolResult:
    """Rollback a deployment by marking it inactive."""

    result = state.rollback_deployment(service, deploy_id)
    return {
        "status": result["status"],
        "data": {"service": service, "deploy_id": deploy_id, "justification": justification},
        "message": result["message"],
    }


def update_incident_ticket(
    incident_id: str,
    patch: dict[str, str],
    evidence_ids: list[str],
) -> ToolResult:
    """Update the incident ticket with a partial patch and evidence."""

    patch_with_timestamp = {
        **patch,
        "last_update": patch.get("last_update", datetime.now(tz=UTC).isoformat().replace("+00:00", "Z")),
    }
    result = state.update_ticket(incident_id, patch_with_timestamp)
    ticket_state = state.get_ticket(incident_id)
    return {
        "status": result["status"],
        "data": {
            "incident_id": incident_id,
            "ticket": ticket_state if ticket_state is not None else {},
            "evidence_ids": evidence_ids,
        },
        "message": result["message"],
    }


def post_incident_update(incident_id: str, message: str) -> ToolResult:
    """Append an operational note to the incident ticket description."""

    current = state.get_ticket(incident_id)
    if current is None:
        raise ValueError(f"Ticket not found for incident {incident_id}")
    description = f'{current["description"]}\nUpdate: {message}'
    result = state.update_ticket(
        incident_id,
        {
            "description": description,
            "last_update": datetime.now(tz=UTC).isoformat().replace("+00:00", "Z"),
        },
    )
    ticket_state = state.get_ticket(incident_id)
    return {
        "status": result["status"],
        "data": {"incident_id": incident_id, "ticket": ticket_state if ticket_state is not None else {}},
        "message": result["message"],
    }


def close_incident(incident_id: str, resolution: str) -> ToolResult:
    """Close the incident with a resolution summary."""

    result = state.close_incident(incident_id, resolution)
    incident = state.get_incident(incident_id)
    return {
        "status": result["status"],
        "data": {"incident": incident if incident is not None else {}},
        "message": result["message"],
    }


def delete_deployment_history(service: str) -> ToolResult:
    """Delete deployment history for a service."""

    result = state.delete_deployment_history(service)
    return {
        "status": result["status"],
        "data": {"service": service},
        "message": result["message"],
    }
