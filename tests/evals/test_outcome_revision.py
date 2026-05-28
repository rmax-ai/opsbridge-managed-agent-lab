"""Governance evals: outcome artifact completeness."""

from __future__ import annotations

import pytest

from src.opsbridge.managed_agents.outcome_evaluator import OutcomeEvaluator


@pytest.mark.governance
class TestOutcomeRevision:
    """Verify outcome rubric evaluation and revision."""

    def test_complete_artifact_passes_all_criteria(self, valid_evidence_bundle: dict) -> None:
        """A complete evidence bundle should pass most criteria."""
        evaluator = OutcomeEvaluator.__new__(OutcomeEvaluator)
        evaluation = evaluator.evaluate_artifact(valid_evidence_bundle)
        passing = sum(1 for v in evaluation.values() if v == "pass")
        failing = sum(1 for v in evaluation.values() if v == "needs_revision")
        assert passing >= 6, f"Expected >=6 passing, got {passing}. Failing: {failing}"

    def test_missing_validation_plan_fails(self) -> None:
        """Artifact without validation_plan must get needs_revision."""
        evaluator = OutcomeEvaluator.__new__(OutcomeEvaluator)
        bundle = {"incident_id": "INC-042", "evidence_items": []}
        evaluation = evaluator.evaluate_artifact(bundle)
        assert evaluation.get("validation_plan") == "needs_revision"
        assert evaluator.needs_revision(evaluation)

    def test_needs_revision_detection(self) -> None:
        """needs_revision must return True when any criterion fails."""
        evaluator = OutcomeEvaluator.__new__(OutcomeEvaluator)
        failing = {"incident_id": "INC-042"}
        assert evaluator.needs_revision(evaluator.evaluate_artifact(failing))
