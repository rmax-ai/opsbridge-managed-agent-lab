"""Repository layer for the audit ledger."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import TypeVar

from sqlmodel import Session, SQLModel, create_engine, select

from ..config import settings
from .models import (
    ActionProposal,
    ApprovalDecision,
    EvidenceItem,
    ExecutionRecord,
    OutcomeEvaluation,
    WorkflowRun,
)

ModelT = TypeVar(
    "ModelT",
    WorkflowRun,
    EvidenceItem,
    ActionProposal,
    ApprovalDecision,
    ExecutionRecord,
    OutcomeEvaluation,
)


class AuditLedgerRepository:
    """CRUD access for audit ledger tables."""

    def __init__(self, database_url: str | None = None):
        """Initialize the repository and create tables if needed."""
        self._database_url = database_url or _sqlite_url(settings.audit_db_path)
        self.engine = create_engine(self._database_url)
        SQLModel.metadata.create_all(self.engine)

    def create_workflow_run(
        self,
        claude_session_id: str,
        incident_id: str,
        execution_profile: str,
        outcome_status: str = "running",
    ) -> WorkflowRun:
        """Create a workflow run record."""
        workflow_run = WorkflowRun(
            claude_session_id=claude_session_id,
            incident_id=incident_id,
            execution_profile=execution_profile,
            outcome_status=outcome_status,
        )
        return self._add_and_refresh(workflow_run)

    def get_workflow_run(self, workflow_run_id: str) -> WorkflowRun | None:
        """Fetch a workflow run by primary key."""
        with Session(self.engine) as session:
            return session.get(WorkflowRun, workflow_run_id)

    def get_workflow_run_by_session(self, claude_session_id: str) -> WorkflowRun | None:
        """Fetch a workflow run by managed-agent session ID."""
        statement = select(WorkflowRun).where(WorkflowRun.claude_session_id == claude_session_id)
        with Session(self.engine) as session:
            return session.exec(statement).first()

    def list_workflow_runs(self) -> list[WorkflowRun]:
        """List workflow runs."""
        with Session(self.engine) as session:
            return list(session.exec(select(WorkflowRun)))

    def update_workflow_run_outcome(
        self,
        workflow_run_id: str,
        outcome_status: str,
        completed_at: datetime | None = None,
    ) -> WorkflowRun:
        """Update workflow outcome status."""
        with Session(self.engine) as session:
            workflow_run = session.get(WorkflowRun, workflow_run_id)
            if workflow_run is None:
                raise KeyError(f"Workflow run {workflow_run_id!r} not found")
            workflow_run.outcome_status = outcome_status
            if completed_at is not None:
                workflow_run.completed_at = completed_at
            session.add(workflow_run)
            session.commit()
            session.refresh(workflow_run)
            return workflow_run

    def create_evidence_item(
        self,
        workflow_run_id: str,
        source_tool: str,
        source_event_id: str,
        content_hash: str,
        payload_json: str,
    ) -> EvidenceItem:
        """Create an evidence item."""
        evidence_item = EvidenceItem(
            workflow_run_id=workflow_run_id,
            source_tool=source_tool,
            source_event_id=source_event_id,
            content_hash=content_hash,
            payload_json=payload_json,
        )
        return self._add_and_refresh(evidence_item)

    def get_evidence_item(self, evidence_item_id: str) -> EvidenceItem | None:
        """Fetch an evidence item by primary key."""
        with Session(self.engine) as session:
            return session.get(EvidenceItem, evidence_item_id)

    def list_evidence_items(self, workflow_run_id: str) -> list[EvidenceItem]:
        """List evidence items for a workflow run."""
        statement = select(EvidenceItem).where(EvidenceItem.workflow_run_id == workflow_run_id)
        with Session(self.engine) as session:
            return list(session.exec(statement))

    def create_action_proposal(
        self,
        workflow_run_id: str,
        action_type: str,
        target_resource: str,
        arguments: object,
        rationale: str,
        policy_classification: str,
        status: str,
    ) -> ActionProposal:
        """Create an action proposal."""
        proposal = ActionProposal(
            workflow_run_id=workflow_run_id,
            action_type=action_type,
            target_resource=target_resource,
            arguments_json=_serialize_json(arguments),
            rationale=rationale,
            policy_classification=policy_classification,
            status=status,
        )
        return self._add_and_refresh(proposal)

    def get_action_proposal(self, proposal_id: str) -> ActionProposal | None:
        """Fetch an action proposal by primary key."""
        with Session(self.engine) as session:
            return session.get(ActionProposal, proposal_id)

    def list_action_proposals(self, workflow_run_id: str) -> list[ActionProposal]:
        """List action proposals for a workflow run."""
        statement = select(ActionProposal).where(ActionProposal.workflow_run_id == workflow_run_id)
        with Session(self.engine) as session:
            return list(session.exec(statement))

    def create_approval_decision(
        self,
        proposal_id: str,
        decision: str,
        reviewer: str,
        reason: str,
    ) -> ApprovalDecision:
        """Create an approval decision."""
        approval = ApprovalDecision(
            proposal_id=proposal_id,
            decision=decision,
            reviewer=reviewer,
            reason=reason,
        )
        return self._add_and_refresh(approval)

    def get_approval_decision(self, approval_decision_id: str) -> ApprovalDecision | None:
        """Fetch an approval decision by primary key."""
        with Session(self.engine) as session:
            return session.get(ApprovalDecision, approval_decision_id)

    def list_approval_decisions(self, proposal_id: str) -> list[ApprovalDecision]:
        """List approval decisions for a proposal."""
        statement = select(ApprovalDecision).where(ApprovalDecision.proposal_id == proposal_id)
        with Session(self.engine) as session:
            return list(session.exec(statement))

    def create_execution_record(
        self,
        proposal_id: str,
        tool_name: str,
        arguments: object,
        result: object,
    ) -> ExecutionRecord:
        """Create an execution record."""
        record = ExecutionRecord(
            proposal_id=proposal_id,
            tool_name=tool_name,
            arguments_json=_serialize_json(arguments),
            result_json=_serialize_json(result),
        )
        return self._add_and_refresh(record)

    def get_execution_record(self, execution_record_id: str) -> ExecutionRecord | None:
        """Fetch an execution record by primary key."""
        with Session(self.engine) as session:
            return session.get(ExecutionRecord, execution_record_id)

    def list_execution_records(self, proposal_id: str) -> list[ExecutionRecord]:
        """List execution records for a proposal."""
        statement = select(ExecutionRecord).where(ExecutionRecord.proposal_id == proposal_id)
        with Session(self.engine) as session:
            return list(session.exec(statement))

    def create_outcome_evaluation(
        self,
        workflow_run_id: str,
        iteration: int,
        result: str,
        feedback: object,
    ) -> OutcomeEvaluation:
        """Create an outcome evaluation record."""
        evaluation = OutcomeEvaluation(
            workflow_run_id=workflow_run_id,
            iteration=iteration,
            result=result,
            feedback_json=_serialize_json(feedback),
        )
        return self._add_and_refresh(evaluation)

    def get_outcome_evaluation(self, outcome_evaluation_id: str) -> OutcomeEvaluation | None:
        """Fetch an outcome evaluation by primary key."""
        with Session(self.engine) as session:
            return session.get(OutcomeEvaluation, outcome_evaluation_id)

    def list_outcome_evaluations(self, workflow_run_id: str) -> list[OutcomeEvaluation]:
        """List outcome evaluations for a workflow run."""
        statement = select(OutcomeEvaluation).where(
            OutcomeEvaluation.workflow_run_id == workflow_run_id
        )
        with Session(self.engine) as session:
            return list(session.exec(statement))

    def _add_and_refresh(self, record: ModelT) -> ModelT:
        with Session(self.engine) as session:
            session.add(record)
            session.commit()
            session.refresh(record)
            return record


def _sqlite_url(path: Path) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    return f"sqlite:///{path}"


def _serialize_json(payload: object) -> str:
    return json.dumps(payload, sort_keys=True, default=str)
