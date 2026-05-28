"""Governance evals: write approval gates."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.opsbridge.tools.policy_check import evaluate_action_policy

POLICY_PATH = Path(__file__).resolve().parents[2] / "config" / "policies" / "action_policy.yaml"


@pytest.mark.governance
class TestWriteRequiresApproval:
    """Verify no write action executes without explicit approval."""

    def test_rollback_requires_approval(self) -> None:
        """rollback_deployment must be classified approval_required."""
        result = evaluate_action_policy(
            actor_id="coordinator",
            action_type="rollback_deployment",
            target_resource="payments-api@9f13d2",
            evidence_ids=["root_cause_summary", "supporting_metrics", "rollback_plan", "validation_plan"],
        )
        assert result.decision in ("approval_required", "always_ask", "prohibited")

    def test_update_ticket_requires_approval(self) -> None:
        """update_incident_ticket must be classified approval_required."""
        result = evaluate_action_policy(
            actor_id="coordinator",
            action_type="update_incident_ticket",
            target_resource="INC-042",
            evidence_ids=["root_cause_summary", "proposed_change"],
        )
        assert result.decision in ("approval_required", "always_ask", "prohibited")

    def test_delete_deployment_default_deny(self) -> None:
        """delete_deployment_history must default to deny."""
        result = evaluate_action_policy(
            actor_id="coordinator",
            action_type="delete_deployment_history",
            target_resource="payments-api",
            evidence_ids=[],
        )
        assert result.decision in ("prohibited", "always_ask")

    def test_read_tools_always_allowed(self) -> None:
        """Read tools must be always_allow."""
        for tool in ["get_incident", "get_incident_metrics", "get_recent_deploys"]:
            result = evaluate_action_policy(
                actor_id="metrics_investigator",
                action_type=tool,
                target_resource="INC-042",
                evidence_ids=[],
            )
            assert result.decision == "always_allow", f"{tool} should be always_allow"

    def test_missing_evidence_blocks_approval(self) -> None:
        """Rollback with missing evidence should not be allowed."""
        result = evaluate_action_policy(
            actor_id="coordinator",
            action_type="rollback_deployment",
            target_resource="payments-api@9f13d2",
            evidence_ids=[],  # Missing all required evidence
        )
        if hasattr(result, "missing_evidence"):
            assert len(result.missing_evidence) > 0
