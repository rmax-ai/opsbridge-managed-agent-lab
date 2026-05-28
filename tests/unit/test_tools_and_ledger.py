"""Unit tests for policy, impact, and audit ledger modules."""

from __future__ import annotations

import json
from pathlib import Path

from src.opsbridge.ledger.hashing import sha256_content_digest, sha256_json_digest
from src.opsbridge.ledger.repository import AuditLedgerRepository
from src.opsbridge.tools.audit_recorder import record_audit_event
from src.opsbridge.tools.impact_calculator import calculate_incident_cost
from src.opsbridge.tools.policy_check import (
    evaluate_action_policy,
    retrieve_operational_policy,
)


def test_policy_check_allows_read_action() -> None:
    result = evaluate_action_policy(
        actor_id="agent-1",
        action_type="get_incident",
        target_resource="incident/inc_042",
        evidence_ids=[],
    )
    assert result.decision == "always_allow"
    assert result.policy_id == "mcp_read:get_*"


def test_policy_check_requires_approval_for_update_with_evidence() -> None:
    result = evaluate_action_policy(
        actor_id="agent-1",
        action_type="update_service",
        target_resource="svc/auth",
        evidence_ids=["root_cause_summary", "proposed_change"],
    )
    assert result.decision == "approval_required"
    assert result.policy_id == "mcp_write:update_*"


def test_policy_check_prohibits_destructive_action_without_required_evidence() -> None:
    result = evaluate_action_policy(
        actor_id="agent-1",
        action_type="delete_cluster",
        target_resource="cluster/prod-1",
        evidence_ids=["root_cause_summary"],
    )
    assert result.decision == "prohibited"
    assert "missing evidence" in " ".join(result.reasons)


def test_retrieve_operational_policy_returns_rule() -> None:
    policy = retrieve_operational_policy("mcp_write:rollback_*")
    assert policy["policy"] == "always_ask"
    assert policy["group"] == "mcp_write"


def test_impact_calculation_is_deterministic() -> None:
    estimate = calculate_incident_cost(
        affected_requests=5_000,
        failed_authorizations=125,
        estimated_loss_per_failure=120.0,
    )
    assert estimate.total_requests_affected == 5_000
    assert estimate.total_failures == 125
    assert estimate.estimated_loss == 15_000.0
    assert estimate.severity == "high"


def test_hashing_helpers_are_stable() -> None:
    assert sha256_content_digest("abc") == sha256_content_digest(b"abc")
    assert sha256_json_digest({"b": 2, "a": 1}) == sha256_json_digest({"a": 1, "b": 2})


def test_audit_ledger_crud(tmp_path: Path) -> None:
    repository = AuditLedgerRepository(database_url=f"sqlite:///{tmp_path / 'audit.db'}")

    workflow_run = repository.create_workflow_run(
        claude_session_id="session-1",
        incident_id="inc_042",
        execution_profile="cloud",
    )
    evidence = repository.create_evidence_item(
        workflow_run_id=workflow_run.id,
        source_tool="get_incident",
        source_event_id="evt-1",
        content_hash=sha256_content_digest("payload"),
        payload_json=json.dumps({"hello": "world"}),
    )
    proposal = repository.create_action_proposal(
        workflow_run_id=workflow_run.id,
        action_type="rollback_deployment",
        target_resource="deploy/auth",
        arguments={"version": "123"},
        rationale="error spike after deployment",
        policy_classification="approval_required",
        status="pending",
    )
    approval = repository.create_approval_decision(
        proposal_id=proposal.id,
        decision="approved",
        reviewer="operator@example.com",
        reason="validated rollback plan",
    )
    execution = repository.create_execution_record(
        proposal_id=proposal.id,
        tool_name="rollback_deployment",
        arguments={"version": "123"},
        result={"status": "ok"},
    )
    evaluation = repository.create_outcome_evaluation(
        workflow_run_id=workflow_run.id,
        iteration=1,
        result="pass",
        feedback={"restored": True},
    )
    updated_run = repository.update_workflow_run_outcome(
        workflow_run.id,
        outcome_status="completed",
    )

    assert repository.get_workflow_run(workflow_run.id) is not None
    assert repository.get_workflow_run_by_session("session-1") is not None
    assert repository.list_workflow_runs()[0].id == workflow_run.id
    assert repository.get_evidence_item(evidence.id) is not None
    assert repository.list_evidence_items(workflow_run.id)[0].id == evidence.id
    assert repository.get_action_proposal(proposal.id) is not None
    assert repository.list_action_proposals(workflow_run.id)[0].id == proposal.id
    assert repository.get_approval_decision(approval.id) is not None
    assert repository.list_approval_decisions(proposal.id)[0].id == approval.id
    assert repository.get_execution_record(execution.id) is not None
    assert repository.list_execution_records(proposal.id)[0].id == execution.id
    assert repository.get_outcome_evaluation(evaluation.id) is not None
    assert repository.list_outcome_evaluations(workflow_run.id)[0].id == evaluation.id
    assert updated_run.outcome_status == "completed"


def test_record_audit_event_creates_evidence(monkeypatch, tmp_path: Path) -> None:
    database_url = f"sqlite:///{tmp_path / 'audit-recorder.db'}"
    monkeypatch.setattr(
        "src.opsbridge.tools.audit_recorder.AuditLedgerRepository",
        lambda: AuditLedgerRepository(database_url=database_url),
    )

    result = record_audit_event(
        session_id="session-99",
        event_type="operator_note",
        actor="alice",
        evidence_ids=["evt-1"],
        payload={"message": "watch rollback closely"},
    )

    repository = AuditLedgerRepository(database_url=database_url)
    workflow_run = repository.get_workflow_run_by_session("session-99")
    assert "event_id" in result
    assert workflow_run is not None
    evidence_items = repository.list_evidence_items(workflow_run.id)
    assert len(evidence_items) == 1
    assert evidence_items[0].source_tool == "audit_recorder"
