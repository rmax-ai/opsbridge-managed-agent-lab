"""Business audit event recording tool."""

from __future__ import annotations

import json
from uuid import uuid4

from ..ledger.hashing import sha256_json_digest
from ..ledger.repository import AuditLedgerRepository


def record_audit_event(
    session_id: str,
    event_type: str,
    actor: str,
    evidence_ids: list[str],
    payload: object,
) -> dict[str, str]:
    """Record a business audit event. Returns event_id."""
    repository = AuditLedgerRepository()
    workflow_run = repository.get_workflow_run_by_session(session_id)
    if workflow_run is None:
        workflow_run = repository.create_workflow_run(
            claude_session_id=session_id,
            incident_id="unknown",
            execution_profile="ad_hoc",
            outcome_status="running",
        )

    event_payload = {
        "event_type": event_type,
        "actor": actor,
        "evidence_ids": evidence_ids,
        "payload": payload,
    }
    evidence_item = repository.create_evidence_item(
        workflow_run_id=workflow_run.id,
        source_tool="audit_recorder",
        source_event_id=f"{event_type}:{uuid4()}",
        content_hash=sha256_json_digest(event_payload),
        payload_json=json.dumps(event_payload, sort_keys=True, default=str),
    )
    return {"event_id": evidence_item.id}
