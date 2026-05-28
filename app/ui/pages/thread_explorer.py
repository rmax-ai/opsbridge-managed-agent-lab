"""Thread explorer page for specialist hierarchy inspection."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from app.ui.mock_data import get_state


def render() -> None:
    """Render the thread explorer page."""
    state = get_state()
    st.title("Thread Explorer")
    st.caption("Inspect coordinator fan-out, specialist context boundaries, and tool traces.")

    with st.container(border=True):
        st.markdown("### Coordinator")
        st.write(
            "The coordinator decomposes the incident into metrics, deployment, and policy tracks. "
            "Each specialist receives only the delegated task, scoped evidence, and an allowlisted tool set."
        )
        st.info(
            "Context isolation prevents one specialist from inheriting the full scratchpad of another. "
            "Only summarized findings are returned to the coordinator."
        )

    for specialist in state.specialists:
        with st.expander(f"{specialist.name} Specialist", expanded=True):
            top_cols = st.columns([2, 1])
            top_cols[0].markdown(f"**Delegated task:** {specialist.delegated_task}")
            top_cols[1].markdown("**Available tools**")
            top_cols[1].write(", ".join(specialist.available_tools))

            invocation_rows = [
                {
                    "timestamp": item.timestamp,
                    "tool": item.tool_name,
                    "status": item.status,
                    "summary": item.summary,
                }
                for item in specialist.invocation_log
            ]
            st.dataframe(pd.DataFrame(invocation_rows), use_container_width=True, hide_index=True)
            st.markdown(f"**Final result:** {specialist.final_result}")
