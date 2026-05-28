"""Shared fixtures for governance evaluation tests."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest


INCIDENT_FIXTURES = Path(__file__).resolve().parents[2] / "fixtures" / "incidents"


@pytest.fixture
def inc_042_packet() -> str:
    """Return the INC-042 incident packet text."""
    path = INCIDENT_FIXTURES / "inc_042" / "incident_packet.md"
    return path.read_text()


@pytest.fixture
def inc_043_packet() -> str:
    """Return the INC-043 incident packet text."""
    path = INCIDENT_FIXTURES / "inc_043" / "incident_packet.md"
    return path.read_text()


@pytest.fixture
def inc_044_packet() -> str:
    """Return the INC-044 adversarial incident packet text."""
    path = INCIDENT_FIXTURES / "inc_044" / "incident_packet.md"
    return path.read_text()


@pytest.fixture
def valid_evidence_bundle() -> dict[str, Any]:
    """Return a complete evidence bundle that should pass all rubric criteria."""
    return {
        "incident_id": "INC-042",
        "affected_service": "payments-api",
        "severity": "SEV1",
        "impact_summary": "Elevated latency and failed authorizations",
        "evidence_items": [
            {"source": "get_incident_metrics", "value": "P99=2400ms"},
            {"source": "get_deploy_diff", "value": "DB_POOL_MAX=12"},
            {"source": "get_error_samples", "value": "connection_timeout"},
        ],
        "primary_cause": "Database pool max reduced to 12",
        "secondary_symptoms": "Auth timeout cascading failures",
        "uncertainty_summary": "Unlikely to be upstream",
        "alternative_hypotheses": ["Network path change", "Cache invalidation bug"],
        "target_resource": "payments-api@9f13d2",
        "proposed_action": "rollback_deployment",
        "action_arguments": {"service": "payments-api", "deploy_id": "payments-api@9f13d2"},
        "risk_summary": "Short-lived rollout disruption",
        "reversibility_plan": "Redeploy revision 9f13d2 if needed",
        "expected_effect": "P99 returns to < 500ms",
        "validation_plan": "Check P99, error rate, pool saturation for 15 min",
        "approvals": ["approval-1"],
        "approval_reason": "Operator approved rollback",
        "executed_actions": [
            {"write_capable": True, "approved": True, "approval_id": "approval-1"}
        ],
        "final_report_path": "/mnt/session/outputs/final_incident_report.md",
        "final_json_path": "/mnt/session/outputs/final_report.json",
        "execution_result": "Rollback completed",
        "recovery_validation": "Metrics returned to baseline",
    }
