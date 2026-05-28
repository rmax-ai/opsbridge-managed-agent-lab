"""Audit ledger page for workflow run history and evidence drill-down."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from app.ui.components.artifact_viewer import render_json_artifact
from app.ui.mock_data import get_state


def render() -> None:
    """Render the audit ledger page."""
    state = get_state()
    st.title("Audit Ledger")
    st.caption("Review workflow run summaries and inspect recorded evidence artifacts.")

    rows = [
        {
            "id": item.id,
            "incident": item.incident,
            "profile": item.profile,
            "started": item.started,
            "completed": item.completed,
            "outcome": item.outcome,
        }
        for item in state.workflow_runs
    ]
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    selected_run_id = st.selectbox(
        "Workflow run",
        options=[item.id for item in state.workflow_runs],
        index=0,
    )
    selected_run = next(item for item in state.workflow_runs if item.id == selected_run_id)
    st.subheader("Evidence Items")
    for evidence in selected_run.evidence_items:
        render_json_artifact(
            f"{evidence.id} • {evidence.source_tool} • {evidence.recorded_at}",
            evidence.payload,
        )
