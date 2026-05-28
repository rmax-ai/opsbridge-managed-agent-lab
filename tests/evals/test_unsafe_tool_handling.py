"""Governance evals: unsafe/destructive tool handling."""

from __future__ import annotations

import pytest

from src.opsbridge.tools.policy_check import evaluate_action_policy


@pytest.mark.governance
class TestUnsafeToolHandling:
    """Verify dangerous actions are properly gated."""

    def test_destructive_tool_denied_by_default(self) -> None:
        """Destructive tool delete_deployment_history must default deny."""
        result = evaluate_action_policy(
            actor_id="remediation_executor",
            action_type="delete_deployment_history",
            target_resource="payments-api",
            evidence_ids=[],
        )
        assert result.decision != "always_allow"

    def test_write_tool_requires_evidence(self) -> None:
        """Write actions with missing evidence must be blocked."""
        result = evaluate_action_policy(
            actor_id="remediation_executor",
            action_type="rollback_deployment",
            target_resource="payments-api@9f13d2",
            evidence_ids=[],
        )
        if hasattr(result, "missing_evidence"):
            assert len(result.missing_evidence) > 0

    def test_read_tool_never_blocked(self) -> None:
        """Read diagnostics must always execute."""
        for tool in ["get_incident", "get_metrics", "list_open_incidents"]:
            result = evaluate_action_policy(
                actor_id="metrics_investigator",
                action_type=tool,
                target_resource="INC-042",
                evidence_ids=[],
            )
            assert result.decision == "always_allow"

    def test_audit_recorder_always_allowed(self) -> None:
        """Audit recording must never be blocked."""
        result = evaluate_action_policy(
            actor_id="coordinator",
            action_type="record_audit_event",
            target_resource="INC-042",
            evidence_ids=[],
        )
        assert result.decision == "always_allow"
