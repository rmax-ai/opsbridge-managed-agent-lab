"""Mock session-state models and seed data for the Streamlit UI."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Literal

import streamlit as st
from pydantic import BaseModel, Field


class EventItem(BaseModel):
    """Single event emitted during a managed-agent workflow."""

    timestamp: str
    event_type: str
    summary: str
    details: str
    agent: str


class ToolInvocation(BaseModel):
    """Tool execution record used in timelines and thread explorer views."""

    timestamp: str
    tool_name: str
    summary: str
    status: Literal["completed", "pending", "blocked"]
    arguments: dict[str, str]
    output: str


class SpecialistThread(BaseModel):
    """Specialist worker assignment and result details."""

    name: str
    delegated_task: str
    available_tools: list[str]
    invocation_log: list[ToolInvocation]
    final_result: str


class ApprovalCardData(BaseModel):
    """Pending tool approval request."""

    id: str
    action_name: str
    arguments: dict[str, str]
    agent: str
    incident_id: str
    supporting_evidence: list[str]
    policy_classification: str
    rubric_status: Literal["aligned", "needs_review", "blocked"]
    decision: Literal["pending", "approved", "denied"] = "pending"


class RubricCriterion(BaseModel):
    """Single outcome evaluation criterion."""

    criterion: str
    status: Literal["pass", "needs_revision"]
    evidence: str


class EvidenceArtifact(BaseModel):
    """Ledger evidence record."""

    id: str
    source_tool: str
    recorded_at: str
    payload: dict[str, str]


class WorkflowRunRecord(BaseModel):
    """Audit-ledger summary row with drill-down evidence."""

    id: str
    incident: str
    profile: str
    started: str
    completed: str
    outcome: str
    evidence_items: list[EvidenceArtifact]


class MemoryVersion(BaseModel):
    """Versioned memory entry."""

    version: str
    created_at: str
    summary: str
    content_before: str
    content_after: str


class MemoryStore(BaseModel):
    """Memory store metadata and contents."""

    name: str
    mode: Literal["read-only", "read-write"]
    description: str
    entries: list[MemoryVersion]


class DeploymentFeature(BaseModel):
    """Deployment profile comparison row."""

    capability: str
    cloud: str
    self_hosted: str


class OpsBridgeMockState(BaseModel):
    """Top-level mock state persisted in Streamlit session state."""

    selected_incident: str = "INC-042"
    uploaded_filename: str | None = None
    outcome_status: Literal["Running", "Blocked", "Completed"] = "Running"
    interrupted: bool = False
    active_run_id: str = "run-2026-05-28-001"
    event_feed: list[EventItem] = Field(default_factory=list)
    tool_timeline: list[ToolInvocation] = Field(default_factory=list)
    specialists: list[SpecialistThread] = Field(default_factory=list)
    approvals: list[ApprovalCardData] = Field(default_factory=list)
    rubric: list[RubricCriterion] = Field(default_factory=list)
    iteration_count: int = 2
    workflow_runs: list[WorkflowRunRecord] = Field(default_factory=list)
    memory_stores: list[MemoryStore] = Field(default_factory=list)
    deployment_features: list[DeploymentFeature] = Field(default_factory=list)


def _iso_time(minutes_ago: int) -> str:
    """Build a stable ISO-8601 timestamp string."""
    value = datetime.now(timezone.utc) - timedelta(minutes=minutes_ago)
    return value.strftime("%Y-%m-%d %H:%M:%S UTC")


def build_mock_state() -> OpsBridgeMockState:
    """Construct the default UI mock state."""
    specialist_logs = [
        ToolInvocation(
            timestamp=_iso_time(18),
            tool_name="metrics.query",
            summary="Fetched p95 latency and error spikes for checkout-api.",
            status="completed",
            arguments={"service": "checkout-api", "window": "30m"},
            output="Latency regressed after deploy sha a91c77e.",
        ),
        ToolInvocation(
            timestamp=_iso_time(16),
            tool_name="deployments.history",
            summary="Compared rollout batches across regions.",
            status="completed",
            arguments={"service": "checkout-api", "limit": "5"},
            output="us-east-1 received canary first; failure concentrated there.",
        ),
        ToolInvocation(
            timestamp=_iso_time(14),
            tool_name="policy.check",
            summary="Validated rollback as medium-risk change.",
            status="completed",
            arguments={"action": "rollback deployment", "target": "checkout-api"},
            output="Human approval required before write action.",
        ),
    ]

    workflow_runs = [
        WorkflowRunRecord(
            id="run-2026-05-28-001",
            incident="INC-042",
            profile="cloud_demo",
            started="2026-05-28 14:02:11 UTC",
            completed="2026-05-28 14:18:54 UTC",
            outcome="pass",
            evidence_items=[
                EvidenceArtifact(
                    id="ev-1107",
                    source_tool="metrics.query",
                    recorded_at="2026-05-28 14:06:12 UTC",
                    payload={
                        "service": "checkout-api",
                        "finding": "p95 latency rose 221% after deployment a91c77e",
                    },
                ),
                EvidenceArtifact(
                    id="ev-1114",
                    source_tool="deployments.history",
                    recorded_at="2026-05-28 14:08:41 UTC",
                    payload={
                        "region": "us-east-1",
                        "finding": "canary batch correlated with error spike",
                    },
                ),
            ],
        ),
        WorkflowRunRecord(
            id="run-2026-05-28-002",
            incident="INC-043",
            profile="self_hosted_demo",
            started="2026-05-28 15:01:03 UTC",
            completed="2026-05-28 15:25:50 UTC",
            outcome="needs_revision",
            evidence_items=[
                EvidenceArtifact(
                    id="ev-1128",
                    source_tool="policy.check",
                    recorded_at="2026-05-28 15:12:05 UTC",
                    payload={
                        "classification": "high_risk",
                        "finding": "vault rotation required before action execution",
                    },
                )
            ],
        ),
    ]

    memory_stores = [
        MemoryStore(
            name="ops_reference_material",
            mode="read-only",
            description="Immutable runbooks, architecture notes, and escalation contacts.",
            entries=[
                MemoryVersion(
                    version="v12",
                    created_at="2026-05-26 09:14:00 UTC",
                    summary="Checkout service rollback runbook refresh.",
                    content_before="Step 4 referenced legacy deploy tooling.",
                    content_after="Step 4 now points to managed rollout controller and canary halt flow.",
                )
            ],
        ),
        MemoryStore(
            name="operator_learnings",
            mode="read-write",
            description="Post-incident observations proposed for future orchestration runs.",
            entries=[
                MemoryVersion(
                    version="v7",
                    created_at="2026-05-28 14:30:00 UTC",
                    summary="Capture canary region before broad rollback approvals.",
                    content_before="Rollback approvals lacked regional blast-radius evidence.",
                    content_after="Approval packets now include canary region, metric deltas, and user impact.",
                ),
                MemoryVersion(
                    version="v8-dream",
                    created_at="2026-05-28 16:10:00 UTC",
                    summary="Dream candidate to cluster policy denials by missing evidence.",
                    content_before="Policy denials require manual pattern review.",
                    content_after="Dream suggests auto-tagging repeated denial reasons for future prompts.",
                ),
            ],
        ),
    ]

    return OpsBridgeMockState(
        event_feed=[
            EventItem(
                timestamp=_iso_time(20),
                event_type="session.started",
                summary="Coordinator opened investigation workspace for INC-042.",
                details="Execution profile cloud_demo booted with rubric-driven outcome tracking.",
                agent="Coordinator",
            ),
            EventItem(
                timestamp=_iso_time(17),
                event_type="delegate",
                summary="Metrics, Deployment, and Policy specialists launched in parallel.",
                details="Each specialist received isolated context with only incident scope and allowed tools.",
                agent="Coordinator",
            ),
            EventItem(
                timestamp=_iso_time(12),
                event_type="approval.required",
                summary="Rollback proposal paused for human confirmation.",
                details="Policy specialist marked the action medium risk because it affects customer traffic.",
                agent="Policy",
            ),
            EventItem(
                timestamp=_iso_time(6),
                event_type="outcome.iteration",
                summary="Outcome evaluator requested stronger evidence on blast radius.",
                details="Coordinator added deployment history and canary region context to the answer.",
                agent="Outcome Evaluator",
            ),
        ],
        tool_timeline=specialist_logs,
        specialists=[
            SpecialistThread(
                name="Metrics",
                delegated_task="Confirm whether customer impact began after the most recent checkout deployment.",
                available_tools=["metrics.query", "logs.search", "service_catalog.read"],
                invocation_log=[specialist_logs[0]],
                final_result="Error rate and p95 latency both inflected within 4 minutes of deploy sha a91c77e.",
            ),
            SpecialistThread(
                name="Deployment",
                delegated_task="Trace rollout order and identify whether the failure tracks a single batch or region.",
                available_tools=[
                    "deployments.history",
                    "change_calendar.read",
                    "artifact.metadata",
                ],
                invocation_log=[specialist_logs[1]],
                final_result="The canary in us-east-1 showed the fault first; later batches were halted before broader spread.",
            ),
            SpecialistThread(
                name="Policy",
                delegated_task="Classify rollback and data collection actions against the governance policy.",
                available_tools=["policy.check", "approvals.queue", "vault.access.request"],
                invocation_log=[specialist_logs[2]],
                final_result="Rollback is allowed with human approval; no privileged vault action is needed for initial mitigation.",
            ),
        ],
        approvals=[
            ApprovalCardData(
                id="approval-201",
                action_name="rollback deployment",
                arguments={
                    "service": "checkout-api",
                    "environment": "prod",
                    "target_sha": "a91c77e^",
                },
                agent="Policy",
                incident_id="INC-042",
                supporting_evidence=[
                    "Metrics specialist linked p95 spike to the latest release.",
                    "Deployment specialist isolated impact to the canary region.",
                    "Outcome evaluator requested blast-radius evidence before closure.",
                ],
                policy_classification="medium_risk_write",
                rubric_status="aligned",
            ),
            ApprovalCardData(
                id="approval-202",
                action_name="collect secure token for rollback automation",
                arguments={"vault": "prod-deploy", "ttl": "10m"},
                agent="Coordinator",
                incident_id="INC-043",
                supporting_evidence=[
                    "Rollback path requires scoped deployment token.",
                    "Self-hosted profile enforces isolated vault boundary.",
                ],
                policy_classification="high_risk_secret_access",
                rubric_status="needs_review",
            ),
        ],
        rubric=[
            RubricCriterion(
                criterion="Incident scope identified",
                status="pass",
                evidence="Coordinator explicitly named checkout-api, impacted region, and customer symptom.",
            ),
            RubricCriterion(
                criterion="Customer impact quantified",
                status="pass",
                evidence="Latency, error rate, and affected checkout traffic were cited from metrics data.",
            ),
            RubricCriterion(
                criterion="Root cause hypothesis grounded",
                status="pass",
                evidence="Deployment correlation and metric timing support the rollback hypothesis.",
            ),
            RubricCriterion(
                criterion="Alternative hypotheses considered",
                status="needs_revision",
                evidence="Database saturation was mentioned but not disproven with direct evidence.",
            ),
            RubricCriterion(
                criterion="Evidence provenance captured",
                status="pass",
                evidence="Tool outputs were logged and attached to the ledger.",
            ),
            RubricCriterion(
                criterion="Policy review completed",
                status="pass",
                evidence="Policy specialist classified the write action and routed it for approval.",
            ),
            RubricCriterion(
                criterion="Human approval honored",
                status="pass",
                evidence="Rollback remained blocked until approval state changed from pending.",
            ),
            RubricCriterion(
                criterion="Remediation plan actionable",
                status="needs_revision",
                evidence="The plan lacks an explicit verification step after rollback.",
            ),
            RubricCriterion(
                criterion="Final summary concise",
                status="pass",
                evidence="Outcome answer remained brief while preserving the decision trail.",
            ),
        ],
        workflow_runs=workflow_runs,
        memory_stores=memory_stores,
        deployment_features=[
            DeploymentFeature(
                capability="Memory",
                cloud="Managed long-term stores with hosted retention controls.",
                self_hosted="Operator-managed persistence with custom retention and storage backends.",
            ),
            DeploymentFeature(
                capability="Dreams",
                cloud="Scheduled background synthesis managed by the provider.",
                self_hosted="Local/offline synthesis jobs under customer scheduling.",
            ),
            DeploymentFeature(
                capability="Subagents",
                cloud="Elastic coordinator fan-out with hosted concurrency limits.",
                self_hosted="Bounded by local worker capacity and enterprise controls.",
            ),
            DeploymentFeature(
                capability="Approvals",
                cloud="Hosted approval inbox with policy hooks and audit trail.",
                self_hosted="Approval flow stays inside the customer trust boundary.",
            ),
            DeploymentFeature(
                capability="Vaults",
                cloud="Provider-integrated secret brokerage with scoped access.",
                self_hosted="Customer-owned vault integration and rotation standards.",
            ),
            DeploymentFeature(
                capability="Network boundary",
                cloud="Traffic exits through managed provider endpoints.",
                self_hosted="No provider-side data plane beyond configured connectors.",
            ),
        ],
    )


def get_state() -> OpsBridgeMockState:
    """Return the current mock UI state from Streamlit session state."""
    if "opsbridge_ui_state" not in st.session_state:
        st.session_state["opsbridge_ui_state"] = build_mock_state()
    state = st.session_state["opsbridge_ui_state"]
    if isinstance(state, OpsBridgeMockState):
        return state
    restored_state = OpsBridgeMockState.model_validate(state)
    st.session_state["opsbridge_ui_state"] = restored_state
    return restored_state


def save_state(state: OpsBridgeMockState) -> None:
    """Persist the mock UI state back into Streamlit session state."""
    st.session_state["opsbridge_ui_state"] = state
