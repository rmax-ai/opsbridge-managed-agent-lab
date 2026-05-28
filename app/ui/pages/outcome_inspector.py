"""Outcome inspector page for rubric evaluation details."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from app.ui.mock_data import get_state


def render() -> None:
    """Render the outcome inspector page."""
    state = get_state()
    st.title("Outcome Inspector")
    st.caption("Track rubric evaluation results and iteration progress.")

    pass_count = sum(item.status == "pass" for item in state.rubric)
    total = len(state.rubric)
    pass_ratio = pass_count / total if total else 0.0

    metric_cols = st.columns(3)
    metric_cols[0].metric("Iteration", str(state.iteration_count))
    metric_cols[1].metric("Pass", f"{pass_count}/{total}")
    metric_cols[2].metric("Needs Revision", str(total - pass_count))

    st.progress(pass_ratio, text=f"Rubric pass rate: {pass_ratio:.0%}")

    table = pd.DataFrame(
        [
            {
                "criterion name": item.criterion,
                "status": item.status,
                "evidence": item.evidence,
            }
            for item in state.rubric
        ]
    )
    st.dataframe(table, use_container_width=True, hide_index=True)
