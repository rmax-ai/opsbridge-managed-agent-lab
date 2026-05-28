"""SQLite-backed synthetic operational state for the OpsHub MCP server."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any, Final, TypedDict, cast


DB_PATH: Final[Path] = Path(__file__).resolve().parents[1] / "data" / "operations.db"


class IncidentRecord(TypedDict):
    """Incident row returned from SQLite."""

    id: str
    title: str
    service: str
    status: str
    severity: str
    started_at: str
    summary: str


class MetricRecord(TypedDict):
    """Metric row returned from SQLite."""

    id: int
    incident_id: str
    metric_name: str
    timestamp: str
    value: float


class DeploymentRecord(TypedDict):
    """Deployment row returned from SQLite."""

    id: str
    service: str
    version: str
    commit_sha: str
    deployed_at: str
    author: str
    active: int


class TicketRecord(TypedDict):
    """Ticket row returned from SQLite."""

    incident_id: str
    status: str
    owner: str
    description: str
    last_update: str


class StatusMessage(TypedDict):
    """Standard write response message."""

    status: str
    message: str


def _connect() -> sqlite3.Connection:
    """Create a SQLite connection with row access by column name."""

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def get_connection() -> sqlite3.Connection:
    """Public access to a database connection (for seeding)."""

    return _connect()


def _row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    """Convert a SQLite row to a plain dictionary."""

    return {key: row[key] for key in row.keys()}


def init_db() -> None:
    """Create required SQLite tables if they do not exist."""

    with _connect() as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS incidents (
              id TEXT PRIMARY KEY,
              title TEXT,
              service TEXT,
              status TEXT DEFAULT 'open',
              severity TEXT,
              started_at TEXT,
              summary TEXT
            );

            CREATE TABLE IF NOT EXISTS metrics (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              incident_id TEXT,
              metric_name TEXT,
              timestamp TEXT,
              value REAL
            );

            CREATE TABLE IF NOT EXISTS deployments (
              id TEXT PRIMARY KEY,
              service TEXT,
              version TEXT,
              commit_sha TEXT,
              deployed_at TEXT,
              author TEXT,
              active INTEGER DEFAULT 1
            );

            CREATE TABLE IF NOT EXISTS deployment_diffs (
              deploy_id TEXT PRIMARY KEY,
              diff_text TEXT
            );

            CREATE TABLE IF NOT EXISTS tickets (
              incident_id TEXT PRIMARY KEY,
              status TEXT,
              owner TEXT,
              description TEXT,
              last_update TEXT
            );
            """
        )


def list_open_incidents() -> list[IncidentRecord]:
    """Return all currently open incidents."""

    with _connect() as connection:
        rows = connection.execute(
            """
            SELECT id, title, service, status, severity, started_at, summary
            FROM incidents
            WHERE status = 'open'
            ORDER BY started_at
            """
        ).fetchall()
    return [cast(IncidentRecord, _row_to_dict(row)) for row in rows]


def get_incident(incident_id: str) -> IncidentRecord | None:
    """Return one incident by ID."""

    with _connect() as connection:
        row = connection.execute(
            """
            SELECT id, title, service, status, severity, started_at, summary
            FROM incidents
            WHERE id = ?
            """,
            (incident_id,),
        ).fetchone()
    if row is None:
        return None
    return cast(IncidentRecord, _row_to_dict(row))


def get_metrics(incident_id: str, window_minutes: int) -> list[MetricRecord]:
    """Return recent metrics for the incident within the requested window."""

    with _connect() as connection:
        rows = connection.execute(
            """
            SELECT id, incident_id, metric_name, timestamp, value
            FROM metrics
            WHERE incident_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
            """,
            (incident_id, max(window_minutes * 10, 1)),
        ).fetchall()
    return [cast(MetricRecord, _row_to_dict(row)) for row in rows]


def get_deployments(service: str, limit: int) -> list[DeploymentRecord]:
    """Return recent deployments for a service."""

    with _connect() as connection:
        rows = connection.execute(
            """
            SELECT id, service, version, commit_sha, deployed_at, author, active
            FROM deployments
            WHERE service = ?
            ORDER BY deployed_at DESC
            LIMIT ?
            """,
            (service, limit),
        ).fetchall()
    return [cast(DeploymentRecord, _row_to_dict(row)) for row in rows]


def get_deploy_diff(deploy_id: str) -> str | None:
    """Return the stored deployment diff text."""

    with _connect() as connection:
        row = connection.execute(
            "SELECT diff_text FROM deployment_diffs WHERE deploy_id = ?",
            (deploy_id,),
        ).fetchone()
    return None if row is None else str(row["diff_text"])


def get_ticket(incident_id: str) -> TicketRecord | None:
    """Return the ticket state for an incident."""

    with _connect() as connection:
        row = connection.execute(
            """
            SELECT incident_id, status, owner, description, last_update
            FROM tickets
            WHERE incident_id = ?
            """,
            (incident_id,),
        ).fetchone()
    if row is None:
        return None
    return cast(TicketRecord, _row_to_dict(row))


def update_ticket(incident_id: str, patch: dict[str, str]) -> StatusMessage:
    """Update incident ticket fields using a partial patch."""

    current = get_ticket(incident_id)
    if current is None:
        raise ValueError(f"Ticket not found for incident {incident_id}")

    updated = {
        "status": patch.get("status", current["status"]),
        "owner": patch.get("owner", current["owner"]),
        "description": patch.get("description", current["description"]),
        "last_update": patch.get("last_update", current["last_update"]),
    }
    with _connect() as connection:
        connection.execute(
            """
            UPDATE tickets
            SET status = ?, owner = ?, description = ?, last_update = ?
            WHERE incident_id = ?
            """,
            (
                updated["status"],
                updated["owner"],
                updated["description"],
                updated["last_update"],
                incident_id,
            ),
        )
    return {
        "status": "ok",
        "message": f"Ticket for incident {incident_id} updated",
    }


def rollback_deployment(service: str, deploy_id: str) -> StatusMessage:
    """Mark a deployment inactive to simulate a rollback."""

    with _connect() as connection:
        row = connection.execute(
            "SELECT id FROM deployments WHERE service = ? AND id = ?",
            (service, deploy_id),
        ).fetchone()
        if row is None:
            raise ValueError(f"Deployment {deploy_id} not found for {service}")
        connection.execute("UPDATE deployments SET active = 0 WHERE id = ?", (deploy_id,))
    return {
        "status": "ok",
        "message": f"Deployment {deploy_id} rolled back for {service}",
    }


def close_incident(incident_id: str, resolution: str) -> StatusMessage:
    """Close an incident and persist the resolution summary."""

    with _connect() as connection:
        row = connection.execute("SELECT id FROM incidents WHERE id = ?", (incident_id,)).fetchone()
        if row is None:
            raise ValueError(f"Incident {incident_id} not found")
        connection.execute(
            "UPDATE incidents SET status = 'closed', summary = ? WHERE id = ?",
            (resolution, incident_id),
        )
    return {
        "status": "ok",
        "message": f"Incident {incident_id} closed",
    }


def delete_deployment_history(service: str) -> StatusMessage:
    """Delete deployment history for a service."""

    with _connect() as connection:
        deploy_rows = connection.execute(
            "SELECT id FROM deployments WHERE service = ?",
            (service,),
        ).fetchall()
        deploy_ids = [str(row["id"]) for row in deploy_rows]
        connection.execute("DELETE FROM deployments WHERE service = ?", (service,))
        if deploy_ids:
            connection.executemany(
                "DELETE FROM deployment_diffs WHERE deploy_id = ?",
                [(deploy_id,) for deploy_id in deploy_ids],
            )
    return {
        "status": "ok",
        "message": f"Deployment history deleted for {service}",
    }
