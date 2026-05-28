"""Deterministic outcome evaluation helpers."""

from __future__ import annotations

from pathlib import Path

from .client import ManagedAgentClient

REPO_ROOT = Path(__file__).resolve().parents[3]
RUBRIC_PATH = REPO_ROOT / "config" / "outcomes" / "incident_remediation_rubric.md"

CRITERIA = (
    "incident_context",
    "evidence_quality",
    "root_cause_analysis",
    "uncertainty_tracking",
    "remediation_specificity",
    "risk_management",
    "validation_plan",
    "approval_governance",
    "final_artifacts",
)


class OutcomeEvaluator:
    """Evaluate incident outcomes against the remediation rubric."""

    def __init__(self, client: ManagedAgentClient) -> None:
        """Initialize the evaluator with a managed-agents client."""
        self.client = client
        self._rubric = RUBRIC_PATH.read_text(encoding="utf-8")

    def define_outcome(self, session_id: str, incident_id: str) -> str:
        """Send a `user.define_outcome` event with the rubric attached."""
        description = (
            f"Investigate and remediate incident {incident_id}. "
            "Produce an operator-ready artifact with evidence, governed remediation, "
            "and post-change validation."
        )
        self.client.call(
            "sessions",
            "send",
            session_id=session_id,
            input={
                "type": "user.define_outcome",
                "description": description,
                "rubric": {"type": "text", "content": self._rubric},
                "max_iterations": 3,
            },
        )
        return description

    def evaluate_artifact(self, evidence_bundle: dict[str, object]) -> dict[str, str]:
        """Evaluate an evidence bundle against nine rubric criteria."""
        evidence_items = self._read_list(evidence_bundle.get("evidence_items"))
        alternative_hypotheses = self._read_list(evidence_bundle.get("alternative_hypotheses"))
        approvals = self._read_list(evidence_bundle.get("approvals"))
        executed_actions = self._read_list(evidence_bundle.get("executed_actions"))

        return {
            "incident_context": self._pass_if(
                self._has_text(evidence_bundle.get("incident_id"))
                and self._has_text(evidence_bundle.get("affected_service"))
                and self._has_text(evidence_bundle.get("severity"))
                and self._has_text(evidence_bundle.get("impact_summary"))
            ),
            "evidence_quality": self._pass_if(len(evidence_items) >= 3),
            "root_cause_analysis": self._pass_if(
                self._has_text(evidence_bundle.get("primary_cause"))
                and self._has_text(evidence_bundle.get("secondary_symptoms"))
            ),
            "uncertainty_tracking": self._pass_if(
                self._has_text(evidence_bundle.get("uncertainty_summary"))
                and len(alternative_hypotheses) >= 1
            ),
            "remediation_specificity": self._pass_if(
                self._has_text(evidence_bundle.get("target_resource"))
                and self._has_text(evidence_bundle.get("proposed_action"))
                and self._has_text(evidence_bundle.get("action_arguments"))
            ),
            "risk_management": self._pass_if(
                self._has_text(evidence_bundle.get("risk_summary"))
                and self._has_text(evidence_bundle.get("reversibility_plan"))
                and self._has_text(evidence_bundle.get("expected_effect"))
            ),
            "validation_plan": self._pass_if(
                self._has_text(evidence_bundle.get("validation_plan"))
            ),
            "approval_governance": self._pass_if(
                len(approvals) >= 1
                and self._has_text(evidence_bundle.get("approval_reason"))
                and self._all_actions_are_gated(executed_actions)
            ),
            "final_artifacts": self._pass_if(
                self._has_text(evidence_bundle.get("final_report_path"))
                and self._has_text(evidence_bundle.get("final_json_path"))
                and self._has_text(evidence_bundle.get("execution_result"))
                and self._has_text(evidence_bundle.get("recovery_validation"))
            ),
        }

    def get_evaluations(self, session_id: str) -> list[dict[str, object]]:
        """Fetch prior outcome evaluations for a session."""
        result = self.client.call("outcomes", "evaluations", session_id=session_id)
        evaluations: list[dict[str, object]] = []
        for item in self.client.extract_list(result):
            if isinstance(item, dict):
                evaluations.append(dict(item))
            else:
                evaluations.append(dict(item.model_dump()))
        return evaluations

    def needs_revision(self, evaluation: dict[str, object]) -> bool:
        """Return true when any criterion failed evaluation."""
        for value in evaluation.values():
            if value == "needs_revision":
                return True
            if isinstance(value, dict) and self.needs_revision(value):
                return True
        return False

    def _pass_if(self, passed: bool) -> str:
        """Convert a boolean evaluation to the public status label."""
        return "pass" if passed else "needs_revision"

    def _has_text(self, value: object) -> bool:
        """Return true when the value is a non-empty string."""
        return isinstance(value, str) and value.strip() != ""

    def _read_list(self, value: object) -> list[object]:
        """Normalize list-like evidence values."""
        if isinstance(value, list):
            return value
        return []

    def _all_actions_are_gated(self, executed_actions: list[object]) -> bool:
        """Require each executed write action to include approval metadata."""
        if not executed_actions:
            return False
        for item in executed_actions:
            if not isinstance(item, dict):
                return False
            if item.get("write_capable") is True and item.get("approved") is not True:
                return False
            if item.get("write_capable") is True and not self._has_text(item.get("approval_id")):
                return False
        return True
